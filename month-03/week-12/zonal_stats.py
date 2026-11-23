"""Guided: mean elevation per teaching district."""
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask

DEM = Path("data/raw/week12/dem.tif")
DISTRICTS = Path("month-03/week-12/districts.gpkg")
OUT = Path("month-03/week-12/teaching_zonal_stats.csv")
NODATA = -9999.0

districts = gpd.read_file(DISTRICTS)
rows = []
with rasterio.open(DEM) as src:
    assert districts.crs == src.crs, "districts and DEM must share a CRS"
    for _, d in districts.iterrows():
        cells, _ = mask(src, [d.geometry], crop=True, nodata=NODATA)
        cells = np.ma.masked_equal(cells[0], NODATA)
        rows.append(
            {
                "district": d["district"],
                "cells": int(cells.count()),
                "mean_m": round(float(cells.mean()), 1),
                "max_m": round(float(cells.max()), 1),
            }
        )

stats = pd.DataFrame(rows)
print(stats)
stats.to_csv(OUT, index=False)
print("wrote", OUT)
