"""Guided: plot teaching NDVI and save ndvi_map.png."""
from pathlib import Path

import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show

NDVI = Path("data/raw/week12/ndvi.tif")
OUT = Path("month-03/week-12/ndvi_map.png")

if not NDVI.exists():
    raise SystemExit("Run ndvi.py first so data/raw/week12/ndvi.tif exists.")

with rasterio.open(NDVI) as src:
    arr = src.read(1, masked=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    image = show(arr, transform=src.transform, ax=ax, cmap="RdYlGn", vmin=-0.2, vmax=0.9)
    fig.colorbar(image.get_images()[0], ax=ax, shrink=0.8, label="NDVI")
    ax.set_title("Teaching scene NDVI")
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")
    fig.savefig(OUT, dpi=130, bbox_inches="tight")
    print("saved", OUT)
