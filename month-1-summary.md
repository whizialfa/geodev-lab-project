# Month 1 summary

Which of the seven lived-in AMAC wards plus Bwari Area Council have the fewest mapped health facilities relative to their population?

## Operation

I counted **points in polygon**: a spatial join of GRID3 health facilities to the 17 study-area wards, then a count per ward and people per mapped clinic. Both layers were already in **EPSG:32632** (UTM 32N, metres). A name join would have missed the hyphen/space problem and would not have placed untagged points. A buffer would have answered “how far”, not “how many clinics per ward”. The output is `data/processed/month1_ward_facility_counts.gpkg`. The map is `maps/people_per_facility.png`. The prediction written before the run is `MONTH1_PREDICTION.md`.

## Expected, then got

**Predicted:** 17 ward rows; about 324 facilities; the 17 counts summing to 324 if every point fell inside one polygon, with at most a handful unmatched on an edge; 0 empty geometries; Gwarinpa and Kabusa worst on people per clinic; Igu, Kawu and Shere lowest on the raw count.

**Got, checked four ways:**

1. **Map.** Darkest fill is Kabusa and Gwarinpa in the south. Northern Bwari is pale. That matches the prediction that the pressure is in the large AMAC wards, not Kubwa.
2. **Row count.** 17 ward polygons out. 324 facilities in. The 17 counts **sum to 324**. Unmatched under `within`: **0**. Matches the 17-row prediction; the leftover I allowed for (0–10) was 0.
3. **One feature by hand.** Kubwa: join said 26 clinics. An independent `within` on the same polygon also said 26. Sample names on that polygon: Miracle Seed Clinic And Maternity, Nigeria Police Hospital, Asher Hospital Kubwa, NYSC Clinic, Oiza Clinic.
4. **Empty geometry.** 0 empty ward polygons, 0 empty facility points, 0 invalid geometries.

Kabusa is 14,493 people per mapped clinic (30 clinics, ~435,000 people). Gwarinpa is 11,417 (51 clinics, ~582,000). Igu is 1,156 (4 clinics, ~4,600 people).

## What surprised me

Igu and Kawu look well served on this ratio only because almost nobody lives there. Counting clinics alone would have ranked them as the gap. Relative to population they are the least pressured wards in the cut. Garki, still treated as the planned core, is 10,753 people per clinic — close to Gwarinpa — so the core is not spare capacity. Thirteen points inside the outline are tagged Tafa, Nasarawa Karu, or Gurara; they still counted because the join is spatial, not a name match.

## Data I still need

Walking distances, not just a headcount: a street network in the same CRS so I can ask how far people are from a clinic, not only how many clinics sit in the ward. A completeness check on the 25 Bwari records with no coordinates, and on the 265 AMAC-tagged records that never mapped. A later population vintage than WorldPop 2020 if the dashboard is meant to stay current. Facility type filled in for the 30 blank rows, so primary care can be separated from other sites.
