# Week 12 raster notes

Rasters stay on this laptop (root `.gitignore`). Nothing below is committed as a GeoTIFF.

## Teaching set (Month 3 learning pack — Ibadan North)

| File | What it is | Notes |
|---|---|---|
| `data/raw/dem.tif` | Pack DEM, 241×315, 30 m, EPSG:32631, nodata −9999 | Used by inspect / read / pixel / sample / clip / zonal / reproject |
| `data/processed/wards.gpkg` | 12 Ibadan North wards (`ward_name`) | Week 10 teaching wards; CRS EPSG:4326 |
| `data/processed/facilities.gpkg` | 41 teaching facilities | Sampled for elevation in `sample_points.py` |
| `data/raw/landsat/LC09_L2SP_191055_20260115_20260117_02_T1_SR_B4.TIF` | Landsat-9 C2 L2 red | Pack scene window |
| `data/raw/landsat/LC09_L2SP_191055_20260115_20260117_02_T1_SR_B5.TIF` | Landsat-9 C2 L2 NIR | Same scene |
| `data/processed/ndvi.tif` | Guided NDVI (`ndvi.py`) | Local output |
| `data/processed/dem_ibadan_north.tif` | DEM clipped to wards | From `clip_raster.py` |
| `data/processed/dem_wgs84.tif` | DEM in EPSG:4326 | From `reproject_raster.py` |

**Pack scene:** LC09_L2SP_191055_20260115_20260117_02_T1 · date **2026-01-15** · path/row **191/055** · scale `DN × 0.0000275 − 0.2`.

## Challenge set (my AMAC project)

| File | What it is | Notes |
|---|---|---|
| `data/raw/week12_amac/B4_red.tif` | Landsat-9 red, windowed to study wards | Scene **LC09_L2SP_189054_20241108_02_T1**, date **2024-11-08**, cloud **0.0%**, EPSG:32632 |
| `data/raw/week12_amac/B5_nir.tif` | Landsat-9 NIR | Same scene |
| `data/raw/week12_amac/ndvi_amac.tif` | NDVI clipped to the ten AMAC study ward polygons | From `my_index.py` |
| `data/raw/week12_amac/dem_amac.tif` | Copernicus GLO-30 DEM | Inspected in `my_inspect.py` |
