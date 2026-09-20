# Week 3 data preparation note — AMAC healthcare access

Study area: Abuja Municipal Area Council (AMAC). The project needs **areas and distances in metres** (ward area, later walking/access work, population per facility), so a geographic CRS is the wrong working system.

## Working CRS

**EPSG:32632** (WGS84 / UTM zone 32N), units metres.

AMAC sits at about 7.1–7.6°E, 8.6–9.1°N. That longitude falls in UTM 32N (6–12°E). Nigeria also uses 31N and 33N, but those would put AMAC near a zone edge or in the wrong zone. I **reprojected** (recalculated coordinates) from EPSG:4326 into 32632; I did not only “assign” 32632, which would have drawn the layer in the Gulf of Guinea.

## What was reprojected and clipped

| Layer | Action |
|---|---|
| AMAC boundary | Reprojected 4326 → 32632 |
| 12 GRID3 operational wards | Reprojected, then clipped to the AMAC polygon |
| 249 GRID3 health facilities | Reprojected, then clipped to the AMAC polygon |
| WorldPop 2020 constrained raster | Left in 4326 for zonal sums (pixel counts stay correct); ward `pop_2020` was taken from that raster |

Clipped output is one GeoPackage:

**`data/processed/amac_analysis_ready.gpkg`**

Layers: `amac_boundary`, `amac_wards`, `amac_health_facilities`. Wards now include `area_m2`, `area_km2`, `pop_2020`, `n_facilities`, and `pop_per_facility`.

Open in QGIS: `qgis/amac_week3.qgz`.

## Five quality checks

### 1. Valid geometry (no empty or self-crossing shapes)
**Pass.** After `make_valid`, invalid counts were 0 / 0 / 0 for boundary, wards, and facilities. No empty geometries.

### 2. Duplicate features
**Pass; clustering flagged, not deleted.** No duplicate `unique_id`, no two facilities in the same metre, no duplicate ward names. The source GRID3 `issues` field still marks 31 facilities as clustered or near a ward edge; those rows were **kept and flagged** so a later map can show uncertainty instead of silently dropping clinics.

### 3. Coverage of the whole study area
**Pass.** AMAC area = ward union = **1,446.57 km²**; symmetric difference after clip = 0. Re-clipping after reprojection removed **0** extra facilities and **0** wards. All 12 named AMAC operational wards are present (City Center 1, Garki 1, Gui, Gwagwa, Gwarinpa, Jiwa, Kabusa, Karshi 1, Karu, Nyanya 1, Orozo, Wuse).

### 4. Missing values in key attributes
**Flagged, not dropped.** Facility names are complete. **17 / 249** facilities have a blank `facility_type`; **195 / 249** have a blank `nhfr_facility_code`. Those records stay in the GeoPackage because they still have coordinates and a name. No ward has zero population or zero mapped facilities. GRID3 still omits **265** AMAC-tagged facilities that had no coordinates (Week 2); they cannot be added without XY.

### 5. Coordinates sit in Nigeria (not the Gulf of Guinea)
**Pass.** After true reprojection, AMAC bounds are about **292,000–346,000 E** and **953,000–1,011,000 N** metres in UTM 32N, which is FCT, not the ocean. If the file had only been labelled 32632 while still storing degrees, it would have drawn near 7 m, 9 m off West Africa.

## Problems and decisions

| Problem | Decision |
|---|---|
| Layer was still in EPSG:4326 (square degrees) | Reprojected to EPSG:32632 so area and distance are in metres |
| GRID3 police-style clustering flags on 31 facilities | Flagged via existing `issues` / `flag_count`; not deleted |
| 17 blank facility types; 195 blank NHFR codes | Flagged in this note; rows kept |
| 265 facilities with no coordinates | Cannot map; already excluded in Week 2; still a completeness gap |
| Operational wards ≠ full INEC list | Flagged; analysis uses GRID3 v3 as the stated ward units |

No geometry repairs beyond `make_valid` were required. No features were invented to fill gaps.
