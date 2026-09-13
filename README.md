# Healthcare Access Gaps in FCT, Nigeria

A spatial analysis project examining which wards in FCT, Nigeria have the fewest health facilities relative to their population.

## What this project does
This project compares health facility locations against ward-level population in FCT to identify wards that are underserved. The end goal is a dashboard that recalculates the population-per-facility ratio whenever the underlying data is refreshed, so it stays current rather than being a one-time report.

## Repository contents
- `PROJECT_BRIEF.md` — the question, why it matters, the data needed, where each dataset comes from, and what will be built.
- `data/` — `fct_healthcare_data.zip` plus cleaned GeoPackage/GeoTIFF extracts under `data/processed/`.
- `scripts/fetch_fct_data.py` — downloads, crops, and zips the FCT boundary, OSM health, and WorldPop layers.
- `dashboard/` — the dashboard build (added once the analysis stage begins).

## Status
Week 1: question and datasets confirmed. Cleaned FCT extracts are in `data/processed/` (run `python scripts/fetch_fct_data.py` to refresh). See `PROJECT_BRIEF.md` for the full scope and data sources.

## How to use this repository
Once the dashboard is built, this section will describe how to run it (software required, how to launch it, and where it reads data from). For now, `PROJECT_BRIEF.md` is the place to start.

## Author
Wisdom Emem Akpabio
