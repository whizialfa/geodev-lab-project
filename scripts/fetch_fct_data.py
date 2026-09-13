#!/usr/bin/env python3
"""Download, crop, and clean FCT healthcare-access geospatial inputs.

Run:
    python fetch_fct_data.py

Output CRS is EPSG:4326. For area or distance calculations later, reproject to
UTM zone 32N: EPSG:32632 (WGS84) or EPSG:26332 (Minna / UTM 32N).
"""

from __future__ import annotations

import logging
import re
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import rasterio
import requests
from rasterio.mask import mask as raster_mask
from shapely.geometry import Point, mapping
from shapely.validation import make_valid

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "raw" / "fct_fetch"
OUTPUT = ROOT / "output"
ZIP_PATH = ROOT / "fct_healthcare_data.zip"

USER_AGENT = "15-min-cities-nigeria/0.1 (research; FCT healthcare fetch)"
TIMEOUT = 180

# OCHA COD-AB shapefile package (HDX dataset cod-ab-nga).
COD_AB_URL = (
    "https://data.humdata.org/dataset/81ac1d38-f603-4a98-804d-325c658599a3/"
    "resource/01c65fd9-bd0c-4608-aa1e-2e86bbccf3e5/download/"
    "nga_admin_boundaries.shp.zip"
)

# WorldPop constrained 2020, 100 m (HDX worldpop-population-counts-for-nigeria),
# with WorldPop FTP mirrors if HDX redirects fail.
WORLDPOP_URLS = (
    (
        "https://data.humdata.org/dataset/f32489c5-6cdd-4226-a37f-e911e633e1db/"
        "resource/6061d980-4631-478c-b840-e97fa3f38473/download/"
        "nga_ppp_2020_constrained.tif"
    ),
    (
        "https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/"
        "2020/maxar_v1/NGA/nga_ppp_2020_constrained.tif"
    ),
    (
        "https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/"
        "2020/BSGM/NGA/nga_ppp_2020_constrained.tif"
    ),
)

OVERPASS_ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)

AMENITIES = ("hospital", "clinic", "doctors")
OUTPUT_CRS = "EPSG:4326"
# FCT sits in UTM 32N; use this if you need metres.
ANALYSIS_CRS = "EPSG:32632"  # alternative Nigerian datum: EPSG:26332
FCT_NODATA = -99999.0

FCT_NAME_TOKENS = (
    "federal capital territory",
    "fct",
    "fct abuja",
    "abuja fct",
)
FCT_PCODES = {"NG015", "NG-FC", "FC"}
# west, south, east, north — whole FCT, used if the COD-AB dissolve is unavailable
FCT_BBOX = (6.75, 8.25, 7.87, 9.37)

log = logging.getLogger("fetch_fct_data")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s",
    )


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def download_file(url: str, dest: Path, http: requests.Session) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 200:
        log.info("Using cached %s", dest.name)
        return dest
    log.info("Downloading %s", url)
    with http.get(url, stream=True, timeout=TIMEOUT, allow_redirects=True) as resp:
        resp.raise_for_status()
        tmp = dest.with_suffix(dest.suffix + ".part")
        with tmp.open("wb") as out:
            for chunk in resp.iter_content(chunk_size=1024 * 256):
                if chunk:
                    out.write(chunk)
        tmp.replace(dest)
    return dest


def extract_zip(archive: Path, out_dir: Path) -> Path:
    if out_dir.exists() and any(out_dir.rglob("*.shp")):
        return out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(out_dir)
    return out_dir


def to_wgs84(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        return gdf.set_crs(OUTPUT_CRS)
    return gdf.to_crs(OUTPUT_CRS)


def _norm(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def _is_blank(value) -> bool:
    return _norm(value) == ""


def pick_column(columns, *candidates: str) -> str | None:
    lower = {c.lower(): c for c in columns}
    for name in candidates:
        if name.lower() in lower:
            return lower[name.lower()]
    return None


def find_shapefile(root: Path, level: int) -> Path:
    shps = list(root.rglob("*.shp"))
    if not shps:
        raise FileNotFoundError(f"No shapefiles in {root}")
    skip = ("line", "point", "capital", "senator")
    polygon_shps = [p for p in shps if not any(s in p.stem.lower() for s in skip)]
    pat = re.compile(rf"(?:^|_)(?:adm|admin)0*{level}(?:_em)?$", re.I)
    ranked = [p for p in polygon_shps if pat.search(p.stem)]
    if not ranked:
        raise FileNotFoundError(f"No admin level {level} shapefile under {root}")
    ranked.sort(key=lambda p: ("_em" in p.stem.lower(), len(p.stem)))
    return ranked[0]


def fct_mask(gdf: gpd.GeoDataFrame) -> pd.Series:
    name_col = pick_column(
        gdf.columns,
        "ADM1_EN",
        "admin1Name",
        "ADM1_NAME",
        "adm1_name",
        "adm1_ref_n",
        "STATENAME",
        "state",
        "adm1_en",
    )
    pcode_col = pick_column(
        gdf.columns,
        "ADM1_PCODE",
        "admin1Pcode",
        "ADM1_CODE",
        "adm1_pcode",
    )
    mask = pd.Series(False, index=gdf.index)
    if name_col:
        names = gdf[name_col].map(lambda v: _norm(v).lower())
        mask = names.isin(FCT_NAME_TOKENS) | names.str.contains(
            "federal capital", na=False
        )
    if pcode_col:
        codes = gdf[pcode_col].map(lambda v: _norm(v).upper())
        mask = mask | codes.isin(FCT_PCODES)
    return mask


def name_field(gdf: gpd.GeoDataFrame, level: int) -> str | None:
    return pick_column(
        gdf.columns,
        f"ADM{level}_EN",
        f"admin{level}Name",
        f"ADM{level}_NAME",
        f"adm{level}_name",
        f"adm{level}_ref_n",
        "WARDNAME",
        "WardName",
        "ward",
        "name",
    )


def _union(gdf: gpd.GeoDataFrame):
    if hasattr(gdf, "union_all"):
        return gdf.union_all()
    return gdf.unary_union


def dissolve_fct(adm1: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    subset = adm1.loc[fct_mask(adm1)].copy()
    if subset.empty:
        raise ValueError(
            "Could not find FCT in the admin-1 layer. "
            "Expected a name like 'Federal Capital Territory' or pcode NG015."
        )
    subset["geometry"] = subset.geometry.make_valid()
    dissolved = subset.dissolve()
    dissolved = dissolved[["geometry"]].reset_index(drop=True)
    dissolved["name"] = "Federal Capital Territory"
    return to_wgs84(dissolved)


def clean_wards(wards: gpd.GeoDataFrame, fct: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, dict]:
    dropped: dict[str, int] = {}
    n0 = len(wards)
    wards = to_wgs84(wards)

    by_attr = fct_mask(wards)
    if by_attr.any():
        wards = wards.loc[by_attr].copy()
        dropped["not_fct_attribute"] = int((~by_attr).sum())
    else:
        dropped["not_fct_attribute"] = 0

    empty = wards.geometry.isna() | wards.geometry.is_empty
    dropped["null_or_empty_geometry"] = int(empty.sum())
    wards = wards.loc[~empty].copy()
    wards["geometry"] = wards.geometry.make_valid()

    n_col = name_field(wards, 3) or name_field(wards, 2)
    if n_col:
        blank = wards[n_col].map(_is_blank)
        dropped["blank_name"] = int(blank.sum())
        wards = wards.loc[~blank].copy()
    else:
        dropped["blank_name"] = 0
        n_col = "name"
        wards[n_col] = ""

    fct_geom = _union(fct)
    intersects = wards.intersects(fct_geom)
    dropped["outside_fct_boundary"] = int((~intersects).sum())
    wards = wards.loc[intersects].copy()
    if not wards.empty:
        wards = gpd.clip(wards, fct)

    dropped["total"] = n0 - len(wards)
    wards = wards.reset_index(drop=True)
    return wards, dropped


def overpass_query(fct: gpd.GeoDataFrame | None) -> tuple[str, str]:
    amenity_block = "\n".join(
        f'  nwr["amenity"="{a}"](area.fct);' for a in AMENITIES
    )
    area_query = (
        "[out:json][timeout:120];\n"
        'area["ISO3166-2"="NG-FC"]->.fct;\n'
        f"(\n{amenity_block}\n);\n"
        "out center tags;"
    )
    if fct is not None and not fct.empty:
        minx, miny, maxx, maxy = fct.total_bounds
    else:
        minx, miny, maxx, maxy = FCT_BBOX[0], FCT_BBOX[1], FCT_BBOX[2], FCT_BBOX[3]
    bbox_block = "\n".join(
        f'  nwr["amenity"="{a}"]({miny},{minx},{maxy},{maxx});' for a in AMENITIES
    )
    bbox_query = (
        "[out:json][timeout:120];\n"
        f"(\n{bbox_block}\n);\n"
        "out center tags;"
    )
    return area_query, bbox_query


def overpass_elements(http: requests.Session, query: str) -> list[dict]:
    last_error: Exception | None = None
    for url in OVERPASS_ENDPOINTS:
        try:
            log.info("Overpass query via %s", url)
            resp = http.post(url, data={"data": query}, timeout=TIMEOUT)
            resp.raise_for_status()
            payload = resp.json()
            return payload.get("elements", [])
        except Exception as exc:  # noqa: BLE001 — log and try the next mirror
            last_error = exc
            log.warning("Overpass endpoint failed (%s): %s", url, exc)
    raise RuntimeError(f"All Overpass endpoints failed: {last_error}")


def elements_to_gdf(elements: list[dict]) -> gpd.GeoDataFrame:
    rows = []
    for el in elements:
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        tags = el.get("tags") or {}
        rows.append(
            {
                "osm_id": el.get("id"),
                "osm_type": el.get("type"),
                "name": tags.get("name"),
                "amenity": tags.get("amenity"),
                "healthcare": tags.get("healthcare"),
                "geometry": Point(float(lon), float(lat)) if lat is not None and lon is not None else None,
            }
        )
    if not rows:
        return gpd.GeoDataFrame(
            columns=["osm_id", "osm_type", "name", "amenity", "healthcare", "geometry"],
            crs=OUTPUT_CRS,
        )
    return gpd.GeoDataFrame(rows, crs=OUTPUT_CRS)


def clean_facilities(
    points: gpd.GeoDataFrame, fct: gpd.GeoDataFrame | None
) -> tuple[gpd.GeoDataFrame, dict]:
    dropped: dict[str, int] = {}
    n0 = len(points)
    missing_xy = points.geometry.isna() | points.geometry.is_empty
    dropped["missing_coordinates"] = int(missing_xy.sum())
    points = points.loc[~missing_xy].copy()

    blank_both = points["name"].map(_is_blank) & points["amenity"].map(_is_blank)
    dropped["blank_name_and_amenity"] = int(blank_both.sum())
    points = points.loc[~blank_both].copy()

    if fct is not None and not fct.empty and not points.empty:
        fct_geom = _union(fct)
        inside = points.intersects(fct_geom)
        dropped["outside_fct_boundary"] = int((~inside).sum())
        points = points.loc[inside].copy()
    else:
        dropped["outside_fct_boundary"] = 0

    if points.empty:
        dropped["duplicate_coordinates"] = 0
        dropped["total"] = n0
        return points.reset_index(drop=True), dropped

    xy = points.geometry.apply(lambda g: (round(g.x, 7), round(g.y, 7)))
    dup = xy.duplicated()
    dropped["duplicate_coordinates"] = int(dup.sum())
    points = points.loc[~dup].copy()
    dropped["total"] = n0 - len(points)
    return points.reset_index(drop=True), dropped


def clip_population(raster_path: Path, fct: gpd.GeoDataFrame, dest: Path) -> dict:
    with rasterio.open(raster_path) as src:
        src_crs = src.crs.to_string() if src.crs else "unknown"
        out_crs = src.crs or OUTPUT_CRS
        fct_for_mask = fct
        if src.crs and src.crs.to_epsg() not in (4326, None):
            fct_for_mask = fct.to_crs(src.crs)
        geoms = [mapping(make_valid(geom)) for geom in fct_for_mask.geometry]
        nodata = src.nodata if src.nodata is not None else FCT_NODATA
        image, transform = raster_mask(
            src,
            geoms,
            crop=True,
            nodata=nodata,
            filled=True,
        )
        profile = src.profile.copy()

    profile.update(
        {
            "height": image.shape[1],
            "width": image.shape[2],
            "transform": transform,
            "nodata": nodata,
            "compress": "lzw",
            "tiled": True,
            "blockxsize": 256,
            "blockysize": 256,
            "crs": out_crs,
        }
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(dest, "w", **profile) as dst:
        dst.write(image)

    band = image[0]
    if nodata is not None:
        n_valid = int((band != nodata).sum())
        n_nodata = int((band == nodata).sum())
    else:
        n_valid = int(band.size)
        n_nodata = 0
    return {
        "pixels_total": int(band.size),
        "pixels_valid": n_valid,
        "pixels_nodata": n_nodata,
        "width": int(profile["width"]),
        "height": int(profile["height"]),
        "src_crs": src_crs,
        "nodata": nodata,
    }


def print_vector_summary(title: str, gdf: gpd.GeoDataFrame, dropped: dict) -> None:
    geom_types = (
        sorted(gdf.geometry.geom_type.unique().tolist()) if not gdf.empty else ["(none)"]
    )
    print(f"\n=== {title} ===")
    print(f"features: {len(gdf)}")
    print(f"geometry type: {', '.join(geom_types)}")
    print(f"CRS: {gdf.crs}")
    print(f"columns: {list(gdf.columns)}")
    print("dropped:")
    for reason, count in dropped.items():
        print(f"  {reason}: {count}")


def print_raster_summary(title: str, stats: dict, dest: Path) -> None:
    print(f"\n=== {title} ===")
    print(f"file: {dest.name}")
    print(f"pixels (all / valid / NoData): {stats['pixels_total']} / {stats['pixels_valid']} / {stats['pixels_nodata']}")
    print(f"shape (height x width): {stats['height']} x {stats['width']}")
    print(f"source CRS: {stats['src_crs']}")
    print(f"output nodata: {stats['nodata']}")
    print("cells outside FCT set to NoData via polygon mask.")


def zip_output() -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(OUTPUT.rglob("*")):
            if path.is_file():
                zf.write(path, arcname=str(Path("output") / path.relative_to(OUTPUT)))
    print(f"\nWrote {ZIP_PATH}")


def fetch_boundaries(
    http: requests.Session,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, dict, str]:
    archive = download_file(COD_AB_URL, CACHE / "nga_admin_boundaries.shp.zip", http)
    extracted = extract_zip(archive, CACHE / "nga_admin_boundaries")
    adm1_path = find_shapefile(extracted, 1)
    adm3_path = find_shapefile(extracted, 3)
    log.info("ADM1 layer: %s", adm1_path.name)
    log.info("ADM3 layer: %s", adm3_path.name)
    adm1 = gpd.read_file(adm1_path)
    adm3 = gpd.read_file(adm3_path)
    fct = dissolve_fct(adm1)
    wards, dropped = clean_wards(adm3, fct)
    label = "FCT wards (COD-AB admin 3)"
    if wards.empty:
        log.warning(
            "COD-AB admin-3 (wards) has partial coverage and does not include FCT "
            "(only Borno/Adamawa/Yobe in current package). Falling back to admin-2 "
            "Area Councils for fct_wards.gpkg."
        )
        adm2_path = find_shapefile(extracted, 2)
        log.info("ADM2 fallback layer: %s", adm2_path.name)
        adm2 = gpd.read_file(adm2_path)
        wards, dropped = clean_wards(adm2, fct)
        dropped["codab_adm3_missing_fct_used_adm2"] = 1
        label = "FCT Area Councils (COD-AB admin 2; admin 3 has no FCT wards)"
    return fct, wards, dropped, label


def fetch_health(http: requests.Session, fct: gpd.GeoDataFrame | None) -> tuple[gpd.GeoDataFrame, dict]:
    area_q, bbox_q = overpass_query(fct)
    errors: list[Exception] = []
    elements: list[dict] = []
    try:
        elements = overpass_elements(http, area_q)
    except Exception as exc:  # noqa: BLE001
        errors.append(exc)
        log.warning("Area Overpass query failed: %s", exc)
    if not elements:
        log.info("Falling back to FCT bounding-box Overpass query")
        try:
            elements = overpass_elements(http, bbox_q)
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)
            log.warning("BBox Overpass query failed: %s", exc)
    if not elements and errors:
        raise RuntimeError(f"Overpass returned no features after errors: {errors[-1]}")
    geojson_path = CACHE / "fct_health_facilities_raw.geojson"
    points = elements_to_gdf(elements)
    geojson_path.write_text(points.to_json())
    log.info("Wrote raw Overpass GeoJSON (%s features) to %s", len(points), geojson_path)
    return clean_facilities(points, fct)


def fetch_worldpop(http: requests.Session) -> Path:
    dest = CACHE / "nga_ppp_2020_constrained.tif"
    last_error: Exception | None = None
    for url in WORLDPOP_URLS:
        try:
            return download_file(url, dest, http)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            log.warning("WorldPop download failed (%s): %s", url, exc)
            if dest.exists() and dest.stat().st_size <= 200:
                dest.unlink()
    raise RuntimeError(f"Could not download WorldPop raster: {last_error}")


def main() -> int:
    setup_logging()
    CACHE.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    http = session()

    print(
        "Output CRS: EPSG:4326. For area/distance later use "
        f"{ANALYSIS_CRS} (WGS84 UTM 32N) or EPSG:26332 (Minna / UTM 32N)."
    )

    fct: gpd.GeoDataFrame | None = None
    wrote_any = False

    try:
        fct, wards, dropped, ward_label = fetch_boundaries(http)
        dest = OUTPUT / "fct_wards.gpkg"
        wards.to_file(dest, layer="fct_wards", driver="GPKG")
        print_vector_summary(ward_label, wards, dropped)
        print(f"saved: {dest}")
        wrote_any = True
    except Exception as exc:  # noqa: BLE001
        log.error("Ward/admin boundary step failed: %s", exc)

    try:
        facilities, dropped = fetch_health(http, fct)
        dest = OUTPUT / "fct_health_facilities.gpkg"
        facilities.to_file(dest, layer="fct_health_facilities", driver="GPKG")
        print_vector_summary("FCT health facilities (OSM Overpass)", facilities, dropped)
        print(f"saved: {dest}")
        wrote_any = True
    except Exception as exc:  # noqa: BLE001
        log.error("Health facility step failed: %s", exc)

    try:
        if fct is None or fct.empty:
            raise RuntimeError("No FCT polygon available; skip population clip.")
        raster_src = fetch_worldpop(http)
        dest = OUTPUT / "fct_population_clipped.tif"
        stats = clip_population(raster_src, fct, dest)
        print_raster_summary("FCT population (WorldPop 2020 constrained 100 m)", stats, dest)
        print(f"saved: {dest}")
        print("dropped: raster cells outside the FCT mask were set to NoData (not deleted as rows).")
        wrote_any = True
    except Exception as exc:  # noqa: BLE001
        log.error("Population raster step failed: %s", exc)

    try:
        if wrote_any and any(OUTPUT.iterdir()):
            zip_output()
        else:
            log.error("No outputs to zip.")
    except Exception as exc:  # noqa: BLE001
        log.error("Zipping output/ failed: %s", exc)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
