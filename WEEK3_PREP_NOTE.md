# Week 3 data preparation note — AMAC + Bwari healthcare access

Study area: the **seven AMAC wards** used on the 15-minute-cities Abuja plates, plus **all of Bwari Area Council**.

The seven AMAC wards are **Gwarinpa, Wuse, Nyanya, Karu, City Centre, Garki, and Kabusa**. Bwari’s ten GRID3 operational wards are **Bwari Central, Byazhin, Dutse, Igu, Kawu, Kubwa, Kuduru, Shere, Ushafa, and Usuma**. Gui, Orozo, Gwagwa, Jiwa, and Karshi stay outside this cut.

The project needs **areas and distances in metres** (ward area, later walking/access work, population per facility), so a geographic CRS is the wrong working system.

## Working CRS

**EPSG:32632** (WGS84 / UTM zone 32N), units metres.

The study area sits at about 7.2–7.7°E, 8.9–9.4°N. That longitude falls in UTM 32N (6–12°E). Nigeria also uses 31N and 33N, but those would put this area near a zone edge or in the wrong zone. I **reprojected** (recalculated coordinates) from EPSG:4326 into 32632; I did not only “assign” 32632, which would have drawn the layer in the Gulf of Guinea.

## What was reprojected and clipped

| Layer | Action |
|---|---|
| Study boundary | Union of the seven AMAC wards and ten Bwari wards, then reprojected 4326 → 32632 |
| 17 wards | Seven from the 15-minute Abuja plate locators; ten from GRID3 v3 where LGA = Bwari; then reprojected |
| GRID3 health facilities | Reprojected, then clipped to that union (**324** mapped points) |
| WorldPop 2020 constrained raster | Left in 4326 for zonal sums; ward `pop_2020` was taken from the national raster so Bwari (north of the old AMAC clip) is included |

Clipped output is one GeoPackage:

**`data/processed/amac_analysis_ready.gpkg`**

Layers: `amac_boundary`, `amac_wards`, `amac_health_facilities`. Wards include `lga`, `source_cut`, `area_m2`, `area_km2`, `pop_2020`, `n_facilities`, and `pop_per_facility`.

Open in QGIS: `qgis/amac_week3.qgz`.

## Five quality checks

### 1. Valid geometry (no empty or self-crossing shapes)
**Pass.** After `make_valid`, invalid counts were 0 / 0 / 0 for boundary, wards, and facilities. No empty geometries.

### 2. Duplicate features
**Pass; clustering flagged, not deleted.** No duplicate `unique_id`, no two facilities in the same centimetre, no duplicate ward names. GRID3 `issues` still marks **55** of the 324 facilities as clustered or near a ward edge; those rows were **kept and flagged**.

### 3. Coverage of the whole study area
**Pass for this cut.** Study area = ward union = **1,619.65 km²**; symmetric difference after clip = 0. All 17 named wards are present (7 AMAC plate + 10 Bwari). The outline is larger than the seven-ward plate (~611 km²) **because Bwari was added**, not because of a dissolve error.

### 4. Missing values in key attributes
**Flagged, not dropped.** Facility names are complete. **30 / 324** facilities have a blank `facility_type`; **242 / 324** have a blank `nhfr_facility_code`. No ward has zero population or zero mapped facilities. GRID3 lists **147** facilities tagged Bwari, of which **25** have no coordinates and could not be mapped. Those remain a completeness gap.

### 5. Coordinates sit in Nigeria (not the Gulf of Guinea)
**Pass.** After true reprojection, bounds are about **304,000–358,000 E** and **981,000–1,040,000 N** metres in UTM 32N, which is FCT (AMAC plus Bwari to the north), not the ocean. If the file had only been labelled 32632 while still storing degrees, it would have drawn near 7 m, 9 m off West Africa.

## Problems and decisions

| Problem | Decision |
|---|---|
| Layer was still in EPSG:4326 (square degrees) | Reprojected to EPSG:32632 so area and distance are in metres |
| Whole AMAC includes peri-urban wards not used on the 15-minute Abuja map | AMAC side kept to the seven plate wards; Gui, Orozo, Gwagwa, Jiwa, and Karshi stay out |
| Bwari sits north of the Week 2 AMAC population clip | Zonal population taken from the national WorldPop raster; Bwari is included |
| 13 mapped points inside the outline are tagged Tafa, Karu (Nasarawa), or Gurara | **Kept** because the clip is spatial; LGA tags are left as GRID3 recorded them |
| GRID3 clustering flags on 55 facilities | Flagged via existing `issues`; not deleted |
| 30 blank facility types; 242 blank NHFR codes; 25 unmapped Bwari records | Flagged in this note; mapped rows kept; unmapped rows cannot be added without XY |

No geometry repairs beyond `make_valid` were required. No features were invented to fill gaps.
