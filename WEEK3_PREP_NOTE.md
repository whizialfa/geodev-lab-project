# Week 3 data preparation note — FCT healthcare access

Study area: the **ten FCT wards** used in my 15-minute-city work on Abuja. Seven are in AMAC: **Gwarinpa, Wuse, Nyanya, Karu, City Centre, Garki and Kabusa**. Three are the built-up part of Bwari: **Kubwa, Dutse and Usuma**. The rest of AMAC (Gui, Orozo, Gwagwa, Jiwa, Karshi) and rural Bwari stay outside this cut, as they do on the 15-minute maps.

The project needs **areas and distances in metres** (ward area, later walking/access work, people per facility), so a geographic CRS is the wrong working system.

## Working CRS

**EPSG:32632** (WGS84 / UTM zone 32N), units metres.

The study area sits at about 7.3–7.6°E, 8.9–9.2°N. That longitude falls in UTM 32N (6–12°E). Nigeria also uses 31N and 33N, but those would put this area near a zone edge or in the wrong zone. I **reprojected** (recalculated coordinates) from EPSG:4326 into 32632; I did not only “assign” 32632, which would have drawn the layer in the Gulf of Guinea.

## What was reprojected and clipped

| Layer | Action |
|---|---|
| Study boundary | Union of the ten wards, then reprojected 4326 → 32632 |
| 10 wards | The same GRID3 ward polygons as the 15-minute Abuja maps, then reprojected |
| GRID3 health facilities | Reprojected, then clipped to the ten-ward outline (**259** mapped points) |
| WorldPop 2020 constrained raster | Left in 4326 for zonal sums; ward `pop_2020` comes from the national raster |

Clipped output is one GeoPackage:

**`data/processed/amac_analysis_ready.gpkg`**

Layers: `amac_boundary`, `amac_wards`, `amac_health_facilities`. Wards carry `ward`, `lga`, `area_m2`, `area_km2` and `pop_2020`.

## Five quality checks

### 1. Valid geometry (no empty or self-crossing shapes)
**Pass.** After `make_valid`, invalid counts were 0 / 0 / 0 for boundary, wards and facilities. No empty geometries.

### 2. Duplicate features
**Pass; flags kept.** No duplicate `unique_id`, no two facilities at the same point, no duplicate ward names. GRID3 flags **44** of the 259 facilities (clustering or near a ward edge). Those rows were **kept**, not deleted.

### 3. Coverage of the whole study area
**Pass.** Study area = ward union = **793.01 km²**; symmetric difference after the clip = 0. All ten named wards are present.

### 4. Missing values in key attributes
**Flagged, not dropped.** Facility names are complete. **25 / 259** have a blank `facility_type`; **188 / 259** have a blank `nhfr_facility_code`. No ward has zero population. GRID3 lists 519 facilities tagged AMAC, of which **265** have no coordinates, and 147 tagged Bwari, of which **25** have no coordinates. Those cannot be mapped and remain a completeness gap.

### 5. Coordinates sit in Nigeria (not the Gulf of Guinea)
**Pass.** After true reprojection, bounds are about **304,000–345,000 E** and **981,000–1,017,000 N** metres in UTM 32N, which is central FCT. If the file had only been labelled 32632 while still storing degrees, it would have drawn a few metres from the zone origin, off West Africa.

## Problems and decisions

| Problem | Decision |
|---|---|
| Layers were in EPSG:4326 (degrees) | Reprojected to EPSG:32632 so area and distance are in metres |
| Whole AMAC includes peri-urban wards not on the 15-minute map | Study area set to the same ten wards as the 15-minute work |
| 11 mapped points inside the outline are tagged Tafa or Karu (Nasarawa) | **Kept**: the clip is spatial, and the points sit inside the ten wards |
| 44 GRID3-flagged facilities | Kept and flagged via the existing `issues` field |
| 25 blank facility types; 188 blank NHFR codes; 290 AMAC/Bwari records with no coordinates | Flagged here; mapped rows kept; unmapped rows cannot be added without coordinates |

No geometry repairs beyond `make_valid` were needed. No features were invented to fill gaps.
