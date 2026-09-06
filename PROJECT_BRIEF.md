# Project Brief: Healthcare Access Gaps in FCT

## Part 1: The question
Which wards in FCT have the fewest health facilities relative to their population?

## Part 2: Why it matters
Health planners and NGOs working in FCT need to know where facility investment would relieve the most pressure, rather than spreading resources evenly across wards that don't need it equally. Wards with high population but few facilities are the ones most likely to be underserved, and flagging them gives a starting point for targeted intervention rather than guesswork.

## Part 3: The data I need
- Health facility locations for FCT
- Ward boundaries for FCT
- Ward-level population counts for FCT

## Part 4: Where each dataset comes from
- Health facility locations: Nigeria Health Facilities (HDX) — https://data.humdata.org/dataset/nigeria-health-facilities
- Ward boundaries: Nigeria Subnational Administrative Boundaries, OCHA COD-AB — https://data.humdata.org/dataset/cod-ab-nga
- Population counts: WorldPop Nigeria Population Counts, 2020 constrained 100m — https://data.humdata.org/dataset/worldpop-population-counts-for-nigeria

## Part 5: What I would build
A dashboard that recalculates each ward's population-per-facility ratio whenever the underlying facility or population data is refreshed, rather than a static map. It would rank wards from most to least underserved and let a user filter by Area Council, so a health planner could open it and immediately see which wards need attention without waiting on a new report each time the data changes.
