"""Challenge: mean NDVI per AMAC study ward. Reproject wards to the raster CRS."""
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask

NDVI = Path("data/raw/week12_amac/ndvi_amac.tif")
WARDS = Path("data/processed/amac_analysis_ready.gpkg")
OUT = Path("month-03/week-12/zonal_stats.csv")

if not NDVI.exists():
    raise SystemExit("Run my_index.py first so ndvi_amac.tif exists.")

wards = gpd.read_file(WARDS, layer="amac_wards")
# Prefer a readable name column
name_col = next(
    (
        c
        for c in ("ward", "wardname", "ward_name", "name", "WardName", "WARDNAME")
        if c in wards.columns
    ),
    None,
)
if name_col is None:
    wards = wards.copy()
    wards["ward"] = [f"ward_{i}" for i in range(len(wards))]
    name_col = "ward"

rows = []
with rasterio.open(NDVI) as src:
    wards = wards.to_crs(src.crs)
    print("wards CRS matched to raster:", src.crs)
    for _, w in wards.iterrows():
        try:
            cells, _ = mask(src, [w.geometry], crop=True, nodata=np.nan)
        except ValueError:
            # ward outside raster extent
            rows.append({name_col: w[name_col], "cells": 0, "mean_ndvi": np.nan})
            continue
        band = cells[0].astype("float32")
        band = np.ma.masked_invalid(band)
        if band.count() == 0:
            rows.append({name_col: w[name_col], "cells": 0, "mean_ndvi": np.nan})
            continue
        rows.append(
            {
                name_col: w[name_col],
                "cells": int(band.count()),
                "mean_ndvi": round(float(band.mean()), 4),
                "min_ndvi": round(float(band.min()), 4),
                "max_ndvi": round(float(band.max()), 4),
            }
        )

stats = pd.DataFrame(rows).sort_values("mean_ndvi", ascending=False)
print(stats.to_string(index=False))
stats.to_csv(OUT, index=False)
print("wrote", OUT)
