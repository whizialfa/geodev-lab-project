# Week 12: rasters with Rasterio

## Scene

- **Scene:** LC09_L2SP_189054_20241108_02_T1 (Landsat-9 Collection 2 Level-2)
- **Date:** 2024-11-08
- **Cloud cover:** 0.0%
- **Path/row:** 189 / 054
- **CRS of clipped bands:** EPSG:32632 (same as the AMAC project)

Rasters are not in git. See [data-notes.md](data-notes.md).

## What this folder contains

**Guided (teaching DEM + scene)**

- `inspect_raster.py`, `read_values.py`, `pixel_coords.py`, `sample_points.py`
- `ndvi.py`, `plot_raster.py` → `ndvi_map.png`
- `clip_raster.py`, `zonal_stats.py` → `teaching_zonal_stats.csv`
- `reproject_raster.py`

**Challenge (AMAC)**

- `my_inspect.py` — Landsat red band + Copernicus DEM metadata
- `my_index.py` — NDVI for the study wards → `my_map.png`
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
uv run month-03/week-12/my_zonal.py
```

## What I found

On 8 November 2024 (cloud-free), mean NDVI is highest in Dutse and Kabusa and lowest in Usuma and Nyanya among the ten study wards. Built-up central wards sit in the middle. The map is greenness, not a clinic map — it sits beside the people-per-clinic story as a land-cover context layer.

## Limitation

NDVI at 30 m mixes roofs, trees and bare ground in one cell. Collection 2 scale/offset and a simple 0–1 reflectance mask are used; no full QA_PIXEL cloud mask was applied beyond choosing a 0% cloud scene.
