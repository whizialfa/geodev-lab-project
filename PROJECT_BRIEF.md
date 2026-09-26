# Project Brief: Healthcare Access Gaps in Central Abuja, FCT

## Part 1: The question
Which wards in central Abuja have the fewest health facilities relative to their population?

When I wrote this brief in Week 1, the study area was all of Abuja Municipal Area Council (AMAC). In Week 3 I narrowed it to the ten FCT wards I use in my 15-minute-city work, because those are where Abuja's people actually live. Seven are in AMAC: Gwarinpa, Wuse, Nyanya, Karu, City Centre, Garki and Kabusa. Three are the built-up part of Bwari: Kubwa, Dutse and Usuma. The rural AMAC wards (Gui, Orozo, Gwagwa, Jiwa, Karshi) are mostly empty land and would dilute the comparison.

## Part 2: Why it matters
Health planners and NGOs working in Abuja need to know where facility investment would relieve the most pressure, rather than spreading resources evenly across wards that do not need it equally. Wards with high population but few facilities are the ones most likely to be underserved, and flagging them gives a starting point for targeted intervention rather than guesswork.

## Part 3: The data I need
- Health facility locations
- Ward boundaries
- Population counts that can be summed to those wards

## Part 4: Where each dataset comes from
- Health facility locations: GRID3 NGA Health Facilities v3.0 (HDX) — https://data.humdata.org/dataset/grid3-nga-health-facilities-v3-0
- Ward boundaries, Weeks 1–2 (all 12 AMAC wards and the AMAC outline): GRID3 NGA Operational Wards v3.0 (HDX) — https://data.humdata.org/dataset/grid3-nga-operational-wards-v3-0
- Ward boundaries, Weeks 3–4 (the ten study wards, the same polygons as my 15-minute-city maps): GRID3 NGA Operational Wards v1.0, the vaccination ward boundaries, December 2020 (GRID3 Nigeria data page) — https://grid3.org/geospatial-data-nigeria
- Population counts: WorldPop Nigeria Population Counts, 2020 constrained 100 m (HDX) — https://data.humdata.org/dataset/worldpop-population-counts-for-nigeria

Week 2 extracts are described in `DATA_NOTE.md`. The prepared ten-ward data is described in `WEEK3_PREP_NOTE.md`.

## Part 5: What I would build
A dashboard that recalculates each ward's population-per-facility ratio whenever the underlying facility or population data is refreshed, rather than a static map. It would rank wards from most to least underserved so a health planner could open it and immediately see which wards need attention without waiting on a new report each time the data changes.
