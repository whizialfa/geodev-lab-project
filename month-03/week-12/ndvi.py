"""Guided: compute NDVI from the teaching two-band scene and save a GeoTIFF."""
from pathlib import Path

import numpy as np
import rasterio

SCENE = Path("data/raw/week12/scene.tif")
OUT = Path("data/raw/week12/ndvi.tif")

with rasterio.open(SCENE) as src:
    print("bands:", src.count, "descriptions:", src.descriptions)
    red = src.read(1).astype("float32")
    nir = src.read(2).astype("float32")
    profile = src.profile.copy()

total = nir + red
ndvi = np.where(total == 0, np.nan, (nir - red) / np.where(total == 0, 1, total))

print("NDVI range:", round(float(np.nanmin(ndvi)), 2), "to", round(float(np.nanmax(ndvi)), 2))
print("share of cells with NDVI above 0.5:", round(float(np.nanmean(ndvi > 0.5)) * 100, 1), "percent")

profile.update(count=1, dtype="float32", nodata=np.nan, compress="lzw")
with rasterio.open(OUT, "w", **profile) as dst:
    dst.write(ndvi.astype("float32"), 1)
print("wrote", OUT)
