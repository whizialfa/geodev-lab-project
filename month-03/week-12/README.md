# Week 12: rasters with Rasterio

## Teaching scene (guided)

- **Scene:** LC09_L2SP_191055_20260115_20260117_02_T1 (Landsat-9 Collection 2 Level-2)
- **Date:** 2026-01-15
- **Path/row:** 191 / 055
- **Area:** Ibadan North (pack DEM + wards)

## Challenge scene (AMAC)

- **Scene:** LC09_L2SP_189054_20241108_02_T1
- **Date:** 2024-11-08
- **Cloud cover:** 0.0%
- **Path/row:** 189 / 054
- **CRS:** EPSG:32632

Rasters are not in git. See [data-notes.md](data-notes.md).

## What this folder contains

**Guided (pack teaching data)**

- `inspect_raster.py`, `read_values.py`, `pixel_coords.py`, `sample_points.py`
- `ndvi.py`, `plot_raster.py` → `ndvi_map.png`
- `clip_raster.py`, `zonal_stats.py`, `reproject_raster.py`

**Challenge (AMAC Months 1–2 data)**

- `my_inspect.py` — Landsat red + Copernicus DEM
- `my_index.py` — NDVI clipped to study ward polygons
- `scripts/build_week12_ndvi_plate.py` — A3 QGIS plate → `my_map.png`
- `my_zonal.py` — mean NDVI per ward → `zonal_stats.csv`

## How to run

From the repository root:

```bash
uv run month-03/week-12/inspect_raster.py
uv run month-03/week-12/read_values.py
uv run month-03/week-12/pixel_coords.py
uv run month-03/week-12/sample_points.py
uv run month-03/week-12/ndvi.py
uv run month-03/week-12/plot_raster.py
uv run month-03/week-12/clip_raster.py
uv run month-03/week-12/zonal_stats.py
uv run month-03/week-12/reproject_raster.py
uv run month-03/week-12/my_inspect.py
uv run month-03/week-12/my_index.py
env -u PYTHONPATH /Applications/QGIS.app/Contents/MacOS/bin/python3.9 scripts/build_week12_ndvi_plate.py
uv run month-03/week-12/my_zonal.py
```

## What I found

On the pack Ibadan North scene, NDVI separates vegetated cells from built ground after the Collection 2 scale/offset. On AMAC (8 Nov 2024, cloud-free), ward mean NDVI is highest in Dutse and Kabusa and lowest in Usuma and Nyanya.

## Limitation

Guided Landsat bands are the pack’s clipped window, not a full scene. AMAC NDVI is clipped to the ten study wards; 30 m cells still mix roofs and trees.
