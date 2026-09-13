# Healthcare Access Gaps in FCT, Nigeria

A spatial analysis project examining which wards in Abuja Municipal Area Council (AMAC), FCT, Nigeria have the fewest health facilities relative to their population.

## What this project does
This project compares GRID3 health facility locations against ward-level population in AMAC to identify wards that are underserved. The end goal is a dashboard that recalculates the population-per-facility ratio whenever the underlying data is refreshed, so it stays current rather than being a one-time report.

## Repository contents
- `PROJECT_BRIEF.md` — the question, why it matters, the data needed, where each dataset comes from, and what will be built.
- `data/` — `amac_healthcare_data.zip` plus cleaned GeoPackage/GeoTIFF extracts under `data/processed/`.
- `data/processed/` — AMAC boundary and 12 operational wards (GRID3 v3), GRID3 health facilities, WorldPop 2020 constrained population clipped to AMAC.
- `dashboard/` — the dashboard build (added once the analysis stage begins).

## Status
Study area narrowed to AMAC. Cleaned GRID3 ward, facility, and WorldPop layers are in `data/processed/`. See `PROJECT_BRIEF.md` for the full scope.

## How to use this repository
Once the dashboard is built, this section will describe how to run it (software required, how to launch it, and where it reads data from). For now, `PROJECT_BRIEF.md` is the place to start.

## Author
Wisdom Emem Akpabio
