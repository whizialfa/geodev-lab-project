"""Guided: open the teaching DEM and print its metadata."""
from pathlib import Path

import rasterio

DEM = Path("data/raw/week12/dem.tif")

with rasterio.open(DEM) as src:
    print("size:", src.width, "x", src.height, "bands:", src.count)
    print("dtype:", src.dtypes[0])
    print("crs:", src.crs, "| epsg:", src.crs.to_epsg())
    print("nodata:", src.nodata)
    print("cell size:", src.res)
    print("bounds:", src.bounds)
    print("transform:", src.transform)
    print("meta keys:", sorted(src.meta))
