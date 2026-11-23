"""Guided: reproject the teaching DEM to EPSG:4326 with bilinear resampling."""
from pathlib import Path

import rasterio
from rasterio.warp import Resampling, calculate_default_transform, reproject

DEM = Path("data/raw/week12/dem.tif")
OUT = Path("data/raw/week12/dem_wgs84.tif")
DST_CRS = "EPSG:4326"

with rasterio.open(DEM) as src:
    new_transform, new_width, new_height = calculate_default_transform(
        src.crs, DST_CRS, src.width, src.height, *src.bounds
    )
    profile = src.profile.copy()
    profile.update(
        crs=DST_CRS,
        transform=new_transform,
        width=new_width,
        height=new_height,
        compress="lzw",
    )
    with rasterio.open(OUT, "w", **profile) as dst:
        reproject(
            source=rasterio.band(src, 1),
            destination=rasterio.band(dst, 1),
            resampling=Resampling.bilinear,
        )

with rasterio.open(OUT) as out:
    print(out.width, out.height, out.crs.to_epsg())
    print([round(v, 6) for v in out.bounds])
print("wrote", OUT)
