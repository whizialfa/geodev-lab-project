# Week 10: GeoPandas, layers as tables

## What this folder contains

- Eight guided scripts on the Ibadan North teaching data (explore, filter, geometries, CSV to points, join, map, save)
- `facilities_map.png` and `wards_table.csv` from those scripts
- Challenge scripts on my AMAC ward and facility data: `my_explore.py`, `my_points.py`, `my_join.py`, `my_map.py`
- `my_map.png`: AMAC wards with health facilities plotted from a CSV

## How to run it

From the repository root:

```bash
uv run month-03/week-10/explore_pandas.py
uv run month-03/week-10/join_population.py
uv run month-03/week-10/make_map.py
uv run month-03/week-10/my_explore.py
uv run month-03/week-10/my_points.py
uv run month-03/week-10/my_join.py
uv run month-03/week-10/my_map.py
```

## What I found

The teaching join matched 9 of 12 wards on raw names and all 12 after stripping, uppercasing and replacing hyphens. On my AMAC wards, only exact names like Gwarinpa matched first; after cleaning (`Center`/`Centre`, trailing ward numbers) seven of twelve wards joined to `abujawards.csv`. The remaining five are AMAC wards outside the ten-ward study table. Bounds for `amac_wards` sit around lon 7.11–7.60 and lat 8.62–9.14, which is central Abuja as expected.

## What went wrong and how I fixed it

The first AMAC join looked almost empty because GRID3 labels wards `Garki 1` and `City Center 1` while my table uses `Garki` and `City Centre`. A shared `clean_name` function fixed the mismatch without editing the CSVs by hand.
