# Healthcare Access Gaps in AMAC, FCT, Nigeria

A spatial analysis project examining which wards in Abuja Municipal Area Council (AMAC), FCT, Nigeria have the fewest health facilities relative to their population.

## What this project does
This project compares GRID3 health facility locations against ward-level population in AMAC to identify wards that are underserved. The end goal is a dashboard that recalculates the population-per-facility ratio whenever the underlying data is refreshed, so it stays current rather than being a one-time report.

## Repository contents
- `PROJECT_BRIEF.md` — the question, why it matters, the data needed, where each dataset comes from, and what will be built.
- `DATA_NOTE.md` — Week 2 data note: source links, feature counts, key columns, geometry types, and gaps.
- `data/processed/` — AMAC boundary, 12 GRID3 operational wards, GRID3 health facilities, WorldPop 2020 constrained raster clipped to AMAC.
- `data/amac_healthcare_data.zip` — the same cleaned layers in one archive.
- `qgis/amac_week2.qgz` — QGIS project that opens the four processed layers.
- `dashboard/` — the dashboard build (added once the analysis stage begins).

## Status
Week 2: AMAC study area locked. GRID3 wards/facilities and WorldPop 2020 are downloaded, clipped, documented in `DATA_NOTE.md`, and packaged for QGIS.

## How to use this repository
1. Clone the repo.
2. Open `qgis/amac_week2.qgz` in QGIS (or add the files under `data/processed/` by hand).
3. Read `DATA_NOTE.md` for sources, counts, and data-quality notes.

## Author
Wisdom Emem Akpabio
