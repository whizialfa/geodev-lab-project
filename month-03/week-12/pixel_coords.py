"""Guided: convert between map coordinates and row/column."""
from pathlib import Path

import rasterio

DEM = Path("data/raw/week12/dem.tif")

with rasterio.open(DEM) as src:
    row, col = src.index(776000, 1455000)
    print("row, col:", row, col)
    x_centre, y_centre = src.xy(row, col)
    print("cell centre:", x_centre, y_centre)
    print("elevation there:", round(float(src.read(1)[row, col]), 1))
