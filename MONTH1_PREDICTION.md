# Prediction — written before the Month 1 spatial join

Question this operation answers: which of the 10 FCT wards used in my 15-minute-city work have the fewest mapped health facilities relative to their population?

The 10 wards are Gwarinpa, Wuse, Nyanya, Karu, City Centre, Garki and Kabusa (AMAC), plus Kubwa, Dutse and Usuma (the built-up part of Bwari).

Operation to run: **count points in polygon** (spatial join of GRID3 facilities to wards, then a count per ward). Both layers sit in **EPSG:32632**. Output will be a GeoPackage of 10 ward polygons with `n_facilities` and `pop_per_facility`.

## What I expect

- **Row count:** 10 ward polygons out, one per input ward. Not the number of facilities, and not 1.
- **Facility total:** roughly **250–270** mapped points inside the ten-ward outline. The counts should sum to the number of facilities clipped in. A few points on a shared edge could fail a `within` join; I expect 0–10, not dozens.
- **Rough values:** no ward should have zero clinics. Gwarinpa should hold the most (around 50). Nyanya and Usuma should be at the low end of the raw count (10–20). On people per clinic, Kabusa and Gwarinpa should be worst (above 10,000), and Karu and Nyanya best (under 3,000).
- **Geometry:** 0 empty polygons, 0 empty points.
- **Map:** the darkest wards should be the large south-western AMAC wards (Gwarinpa, Kabusa), not the Bwari satellite.

An earlier run on a wider 17-ward cut informs these numbers, so this is not a blind guess on the counts. The row count and the empty-geometry expectation are what the checks test.
