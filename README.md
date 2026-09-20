# Healthcare Access Gaps in AMAC, FCT, Nigeria

A spatial analysis project examining which wards in Abuja Municipal Area Council (AMAC), FCT, Nigeria have the fewest health facilities relative to their population.

## What this project does
This project compares GRID3 health facility locations against ward-level population in AMAC to identify wards that are underserved. The end goal is a dashboard that recalculates the population-per-facility ratio whenever the underlying data is refreshed, so it stays current rather than being a one-time report.

## Repository contents
- `PROJECT_BRIEF.md` — the question, why it matters, the data needed, where each dataset comes from, and what will be built.
- `DATA_NOTE.md` — Week 2 data note: source links, feature counts, key columns, geometry types, and gaps.
- `WEEK3_PREP_NOTE.md` — Week 3: working CRS (EPSG:32632), clip, five quality checks, path to the analysis-ready GeoPackage.
- `data/processed/amac_analysis_ready.gpkg` — analysis-ready layers in UTM 32N: seven AMAC plate wards plus ten Bwari wards, 324 facilities.
- `data/processed/` — also the Week 2 4326 extracts and WorldPop raster.
- `data/amac_healthcare_data.zip` — Week 2 archive.
- `qgis/amac_week3.qgz` — QGIS project for the analysis-ready GeoPackage.
- `qgis/amac_week2.qgz` — QGIS project for the Week 2 geographic layers.
- `dashboard/` — the dashboard build (added once the analysis stage begins).

## Status
Week 3: layers reprojected to EPSG:32632, clipped to the seven 15-minute Abuja wards plus Bwari Area Council, saved as `data/processed/amac_analysis_ready.gpkg`. Quality checks are in `WEEK3_PREP_NOTE.md`.

## How to use this repository
1. Clone the repo.
2. Open `qgis/amac_week3.qgz` in QGIS, or add the three layers from `data/processed/amac_analysis_ready.gpkg`.
3. Read `WEEK3_PREP_NOTE.md` for CRS choice, clip, and the five checks.

## Author
Wisdom Emem Akpabio
