# Project Brief: Healthcare Access Gaps in AMAC, FCT

## Part 1: The question
Which wards in Abuja Municipal Area Council (AMAC) have the fewest health facilities relative to their population?

## Part 2: Why it matters
Health planners and NGOs working in AMAC need to know where facility investment would relieve the most pressure, rather than spreading resources evenly across wards that do not need it equally. Wards with high population but few facilities are the ones most likely to be underserved, and flagging them gives a starting point for targeted intervention rather than guesswork.

## Part 3: The data I need
- Health facility locations inside AMAC
- Ward boundaries for AMAC
- Population counts that can be summed to those wards

## Part 4: Where each dataset comes from
- Health facility locations: GRID3 NGA Health Facilities v3.0 (HDX) — https://data.humdata.org/dataset/grid3-nga-health-facilities-v3-0
- Ward boundaries (and the AMAC outline, dissolved from those wards): GRID3 NGA Operational Wards v3.0 (HDX) — https://data.humdata.org/dataset/grid3-nga-operational-wards-v3-0
- Population counts: WorldPop Nigeria Population Counts, 2020 constrained 100 m (HDX) — https://data.humdata.org/dataset/worldpop-population-counts-for-nigeria

Week 2 extracts of these layers are in `data/processed/` and described in `DATA_NOTE.md`.

## Part 5: What I would build
A dashboard that recalculates each AMAC ward's population-per-facility ratio whenever the underlying facility or population data is refreshed, rather than a static map. It would rank wards from most to least underserved so a health planner could open it and immediately see which wards need attention without waiting on a new report each time the data changes.
