# Week 11: CRS and spatial operations

## EPSG code

I used **EPSG:32632** (WGS 84 / UTM zone 32N) for the AMAC challenge. `estimate_utm_crs()` suggested it, and central Abuja sits near 7.5°E, inside zone 32. Teaching scripts stay on **EPSG:32631** for Ibadan North.

## What this folder contains

- Eight guided scripts on the Ibadan North teaching data (wrong vs right area, set_crs vs to_crs, one-point transform, buffer/count, coverage gap, nearest, clip/dissolve, fix geometry)
- Challenge scripts on AMAC wards and GRID3 facilities: `my_crs.py`, `my_count.py`, `my_reach.py`, `my_validity.py`
- `my_reach.png`: AMAC wards with areas more than 2 km from a mapped facility highlighted
- Result layers in `data/processed/week11_amac_reach.gpkg` and `week11_amac_wards_valid.gpkg`

## How to run it

From the repository root:

```bash
uv run month-03/week-11/area_wrong_and_right.py
uv run month-03/week-11/spatial_ops.py
uv run month-03/week-11/my_crs.py
uv run month-03/week-11/my_count.py
uv run month-03/week-11/my_reach.py
uv run month-03/week-11/my_validity.py
```

## What I found

AMAC wards reproject cleanly to EPSG:32632. The facility count check joins mapped points into wards with zeros filled for empty wards. The 2 km dissolved reach leaves uncovered pockets mainly in larger or more peripheral wards; the map paints those gaps in red over the ward outlines.

## Limitation

The 2 km buffers are straight-line distance, not walking distance on the street network, and they only cover GRID3 facilities that have coordinates. Half of AMAC’s GRID3 records still have no coordinates, so the map understates how much of the council is actually far from care.
