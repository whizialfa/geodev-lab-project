# Month 1 summary

Which of the ten FCT wards in my 15-minute-city study have the fewest mapped health facilities relative to their population?

The ten are Gwarinpa, Wuse, Nyanya, Karu, City Centre, Garki and Kabusa in AMAC, plus Kubwa, Dutse and Usuma in Bwari.

## Operation

I ran **count points in polygon**: a spatial join of GRID3 health facilities to the ten wards, then a count per ward and people per mapped clinic. Both layers are in **EPSG:32632** (UTM 32N, metres). A name join would miss spelling differences (“City Center 1” vs “City Centre”) and would trust the facility’s own ward tag. A buffer answers “how far”, not “how many clinics per ward”. Output: `data/processed/month1_ward_facility_counts.gpkg`. Map: `maps/people_per_facility.png`. The prediction written before the run is `MONTH1_PREDICTION.md`.

## Expected, then got

**Predicted:** 10 ward rows; about 250–270 facilities; counts summing to the facilities clipped in, with at most a handful unmatched on an edge; 0 empty geometries; Gwarinpa holding the most clinics; Kabusa and Gwarinpa worst on people per clinic (above 10,000); Karu and Nyanya best (under 3,000).

**Got, checked four ways:**

1. **Map.** The darkest wards are Kabusa and Gwarinpa in the south-west. Nyanya and Karu in the east are palest. The Bwari satellite sits in the middle bands. That matches the prediction.
2. **Row count.** 10 ward polygons out. 259 facilities in. The ten counts **sum to 259**. Unmatched under `within`: **0**.
3. **One feature by hand.** Asher Hospital Kubwa sits at 9.1515°N, 7.3263°E, which is 316,088 E, 1,012,028 N in UTM 32N. GRID3 tags it Kubwa, Bwari, and the point falls inside the Kubwa polygon. Kubwa’s join count (24) also matches a separate `within` count on that polygon.
4. **Empty geometry.** 0 empty ward polygons, 0 empty facility points, 0 invalid geometries.

| Ward | Clinics | People (2020) | People per clinic |
|---|---|---|---|
| Kabusa | 30 | 434,789 | 14,493 |
| Gwarinpa | 51 | 582,288 | 11,417 |
| Garki | 23 | 247,312 | 10,753 |
| Dutse | 21 | 221,209 | 10,534 |
| Wuse | 20 | 195,387 | 9,769 |
| City Centre | 33 | 230,486 | 6,984 |
| Kubwa | 24 | 139,993 | 5,833 |
| Usuma | 19 | 75,943 | 3,997 |
| Karu | 25 | 66,173 | 2,647 |
| Nyanya | 13 | 31,328 | 2,410 |

## What surprised me

Gwarinpa has the **most** clinics of any ward (51) and is still the second worst, because it also holds the most people. Counting clinics alone would have called it well served. Dutse, in Bwari, is almost as pressured as Garki, which is still thought of as the planned core. Eleven points inside the outline are tagged Tafa or Karu (Nasarawa) in GRID3; the join counted them because it goes by location, not by the tag.

## Data I still need

- A street network in the same CRS, so I can measure how far people walk to a clinic rather than how many clinics sit in their ward.
- Coordinates for the 265 AMAC and 25 Bwari GRID3 records that never mapped.
- A newer population layer than WorldPop 2020 if the dashboard is meant to stay current.
- Facility type filled in for the 25 blank rows, so primary care can be separated from other sites.
