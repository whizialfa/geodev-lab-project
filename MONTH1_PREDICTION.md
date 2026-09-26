# Prediction — written before the Month 1 spatial join

Question this operation answers: which of the 17 study-area wards have the fewest mapped health facilities relative to their population?

Operation to run: **count points in polygon** (spatial join of GRID3 facilities to wards, then a count per ward). Both layers already sit in **EPSG:32632**. Output will be a GeoPackage of 17 ward polygons with `n_facilities` and `pop_per_facility`.

## What I expect

- **Row count:** 17 ward polygons out, one per input ward. Not 324. Not 1.
- **Facility total:** about **324** mapped points in the analysis-ready file. If every point falls strictly inside one ward, the 17 counts should sum to 324. A handful may sit on a shared edge and fail a `within` join; I expect that leftover to be small (0–10), not hundreds.
- **Rough values:** no ward should be empty of clinics from last week’s inventory, but rural Bwari (Igu, Kawu, Shere) should sit at the low end of the count (single digits to low teens). Gwarinpa, Kabusa, Dutse and Kubwa should sit at the high end (tens of clinics). People-per-facility should be worst where population is largest: Gwarinpa and Kabusa, not the small northern Bwari wards.
- **Geometry:** 0 empty polygons. 0 empty points in the join table.
- **Map:** the darkest (most people per clinic) patches should be the big southern AMAC wards, not Kubwa.

I am not using the `n_facilities` column already stored on the Week 3 wards. That column is stripped and the join is run again so this week’s result is a new table.
