"""Challenge: NDVI for AMAC, clipped to the ten study ward polygons.

Map PNG is built by scripts/build_week12_ndvi_plate.py (headless QGIS), not matplotlib.
"""
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask

RED = Path("data/raw/week12_amac/B4_red.tif")
NIR = Path("data/raw/week12_amac/B5_nir.tif")
WARDS = Path("data/processed/amac_analysis_ready.gpkg")
OUT_TIF = Path("data/raw/week12_amac/ndvi_amac.tif")

# USGS Landsat Collection 2 Level-2 surface reflectance
SCALE = 0.0000275
OFFSET = -0.2


def to_reflectance(dn: np.ndarray) -> np.ndarray:
    """uint16 DN → float32 reflectance; hide fill and out-of-range values."""
    arr = dn.astype("float32")
    refl = arr * SCALE + OFFSET
    bad = (dn == 0) | (refl < 0) | (refl > 1)
    refl[bad] = np.nan
    return refl


wards = gpd.read_file(WARDS, layer="amac_wards")

with rasterio.open(RED) as src_red, rasterio.open(NIR) as src_nir:
    assert src_red.crs == src_nir.crs
    assert src_red.shape == src_nir.shape
    red = to_reflectance(src_red.read(1))
    nir = to_reflectance(src_nir.read(1))
    profile = src_red.profile.copy()
    transform = src_red.transform
    crs = src_red.crs

total = nir + red
ndvi = np.where(np.isnan(total) | (total == 0), np.nan, (nir - red) / total).astype("float32")

# Write full window first, then clip to the dissolved study wards (not a bbox).
profile.update(dtype="float32", count=1, nodata=np.nan, compress="lzw")
tmp = OUT_TIF.with_name("ndvi_amac_window.tif")
with rasterio.open(tmp, "w", **profile) as dst:
    dst.write(ndvi, 1)

wards_r = wards.to_crs(crs)
study = wards_r.union_all()
with rasterio.open(tmp) as src:
    clipped, clip_transform = mask(src, [study.__geo_interface__], crop=True, nodata=np.nan)
    out_profile = src.profile.copy()
    out_profile.update(
        height=clipped.shape[1],
        width=clipped.shape[2],
        transform=clip_transform,
        compress="lzw",
    )
    with rasterio.open(OUT_TIF, "w", **out_profile) as dst:
        dst.write(clipped[0], 1)
        dst.set_band_description(1, "NDVI")

valid = clipped[0][np.isfinite(clipped[0])]
print("NDVI clipped to study wards")
print("NDVI range:", round(float(valid.min()), 3), "to", round(float(valid.max()), 3))
print("NDVI mean:", round(float(valid.mean()), 3))
print("share NDVI > 0.3:", round(float((valid > 0.3).mean()) * 100, 1), "%")
print("wrote", OUT_TIF)
print("Map: run scripts/build_week12_ndvi_plate.py with QGIS python3.9")
