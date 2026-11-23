"""Guided: clip the teaching DEM with a study-area circle."""
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask
from shapely.geometry import Point

DEM = Path("data/raw/week12/dem.tif")
OUT = Path("data/raw/week12/dem_cut.tif")
NODATA = -9999.0

area = gpd.GeoDataFrame(
    {"name": ["study area"]},
    geometry=[Point(776000, 1455000).buffer(2500)],
    crs="EPSG:32643",
)

with rasterio.open(DEM) as src:
    assert area.crs == src.crs, "polygon and raster must share a CRS"
    clipped, clipped_transform = mask(src, area.geometry, crop=True, nodata=NODATA)
    profile = src.profile.copy()

clipped_band = np.ma.masked_equal(clipped[0], NODATA)
print(clipped_band.shape, "cells in the box,", clipped_band.count(), "inside the circle")
print("mean elevation:", round(float(clipped_band.mean()), 1))

profile.update(
    height=clipped_band.shape[0],
    width=clipped_band.shape[1],
    transform=clipped_transform,
    compress="lzw",
)
with rasterio.open(OUT, "w", **profile) as dst:
    dst.write(clipped_band.filled(NODATA), 1)
print("wrote", OUT)
