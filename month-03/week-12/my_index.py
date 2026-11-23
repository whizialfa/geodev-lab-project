"""Challenge: NDVI for AMAC from Landsat-9 Collection 2 Level-2 red and NIR."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.plot import show

RED = Path("data/raw/week12_amac/B4_red.tif")
NIR = Path("data/raw/week12_amac/B5_nir.tif")
OUT_TIF = Path("data/raw/week12_amac/ndvi_amac.tif")
OUT_PNG = Path("month-03/week-12/my_map.png")

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


with rasterio.open(RED) as src_red, rasterio.open(NIR) as src_nir:
    assert src_red.crs == src_nir.crs
    assert src_red.shape == src_nir.shape
    red = to_reflectance(src_red.read(1))
    nir = to_reflectance(src_nir.read(1))
    profile = src_red.profile.copy()
    transform = src_red.transform

total = nir + red
ndvi = np.where(np.isnan(total) | (total == 0), np.nan, (nir - red) / total)

valid = ndvi[np.isfinite(ndvi)]
print("NDVI range:", round(float(valid.min()), 3), "to", round(float(valid.max()), 3))
print("NDVI mean:", round(float(valid.mean()), 3))
print("share NDVI > 0.3:", round(float((valid > 0.3).mean()) * 100, 1), "%")

profile.update(dtype="float32", count=1, nodata=np.nan, compress="lzw")
with rasterio.open(OUT_TIF, "w", **profile) as dst:
    dst.write(ndvi.astype("float32"), 1)
print("wrote", OUT_TIF)

fig, ax = plt.subplots(figsize=(7, 8))
image = show(np.ma.masked_invalid(ndvi), transform=transform, ax=ax, cmap="RdYlGn", vmin=-0.2, vmax=0.8)
fig.colorbar(image.get_images()[0], ax=ax, shrink=0.7, label="NDVI")
ax.set_title("AMAC NDVI — Landsat-9 2024-11-08")
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")
fig.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
print("saved", OUT_PNG)
