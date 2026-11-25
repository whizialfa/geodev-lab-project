"""Guided: compare raw vs masked means on the teaching DEM."""
from pathlib import Path

import rasterio

DEM = Path("data/raw/week12/dem.tif")

with rasterio.open(DEM) as src:
    raw = src.read(1)
    masked = src.read(1, masked=True)

print("raw minimum:", raw.min())
print("mean with NoData included:", round(float(raw.mean()), 1))
print("mean with NoData masked:", round(float(masked.mean()), 1))
print("valid cells:", masked.count(), "of", masked.size)
