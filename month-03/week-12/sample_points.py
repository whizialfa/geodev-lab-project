"""Guided: sample the DEM at a list of map points."""
from pathlib import Path

import rasterio

DEM = Path("data/raw/week12/dem.tif")

points = [(776000, 1455000), (780500, 1459000), (772000, 1452000)]

with rasterio.open(DEM) as src:
    values = [v[0] for v in src.sample(points)]
    print("points:", points)
    print("sampled:", [round(float(v), 1) for v in values])
    print("nodata:", src.nodata)
