# Week 2 data note — AMAC healthcare access

Study area: **Abuja Municipal Area Council (AMAC)**, Federal Capital Territory, Nigeria. All layers are in **EPSG:4326**. Open `qgis/amac_week2.qgz` in QGIS to view them together.

## 1. AMAC boundary

- **File:** `data/processed/amac_boundary.gpkg` (layer `amac_boundary`)
- **Source:** Dissolved from GRID3 NGA Operational Wards v3.0 (CIESIN / Columbia University, July 2026). [HDX dataset](https://data.humdata.org/dataset/grid3-nga-operational-wards-v3-0)
- **Features:** 1
- **Geometry:** Polygon
- **Key columns:** `name` (Abuja Municipal Area Council), `source` (dissolve note)
- **Gaps:** None in this layer. The polygon is the union of the 12 AMAC operational wards below, so it matches the ward file. GRID3 labels these as operational wards, not a full INEC electoral list.

## 2. AMAC wards

- **File:** `data/processed/amac_wards.gpkg` (layer `amac_wards`)
- **Source:** GRID3 NGA Operational Wards v3.0, filtered to LGA = Municipal Area Council in FCT. [HDX dataset](https://data.humdata.org/dataset/grid3-nga-operational-wards-v3-0)
- **Features:** 12
- **Geometry:** Polygon
- **Key columns:** `ward`, `lga`, `state`, `statecode`, `area_sqkm`, `source`, `date`
- **Wards:** City Center 1, Garki 1, Gui, Gwagwa, Gwarinpa, Jiwa, Kabusa, Karshi 1, Karu, Nyanya 1, Orozo, Wuse
- **Gaps:** No empty names or empty geometries in the 12 AMAC wards. Names such as “City Center 1” and “Nyanya 1” are GRID3 operational units; they may not line up one-to-one with every named electoral ward in AMAC. OCHA COD-AB admin-3 does not include FCT wards, which is why GRID3 v3 was used instead.

## 3. Health facilities

- **File:** `data/processed/amac_health_facilities.gpkg` (layer `amac_health_facilities`)
- **Source:** GRID3 NGA Health Facilities v3.0 (CIESIN / Columbia University, August 2026). [HDX dataset](https://data.humdata.org/dataset/grid3-nga-health-facilities-v3-0)
- **Features:** 249 mapped points in AMAC (from 519 GRID3 records tagged as Municipal Area Council)
- **Geometry:** Point
- **Key columns:** `facility_name`, `facility_type`, `facility_level`, `facility_ownership`, `functional`, `ward_standard`, `nhfr_facility_code`, `latitude`, `longitude`
- **Gaps:**
  - **265** AMAC-tagged records had no coordinates and could not be mapped.
  - **5** records with coordinates sat outside the AMAC polygon and were clipped out.
  - **195 / 249** mapped facilities have a blank `nhfr_facility_code` (no National Health Facility Registry ID).
  - **17** have a blank `facility_type`; **15** have blank `facility_level`, `facility_ownership`, and `functional`.
  - **178** have no `alt_name`; **183** have no `gps_accuracy`.
  - GRID3 `issues` flags **31** mapped points (ward-boundary mismatches or clustering). `functional` is Unknown for 73 facilities.

## 4. Population

- **File:** `data/processed/amac_population_clipped.tif`
- **Source:** WorldPop Nigeria population counts, 2020, constrained, ~100 m. [HDX dataset](https://data.humdata.org/dataset/worldpop-population-counts-for-nigeria) (file `nga_ppp_2020_constrained.tif`)
- **Features:** Raster, 626 × 589 cells. **48,560** cells have population values; **320,154** are NoData (`-99999`). Pixel values sum to about **2.27 million** people inside AMAC.
- **Geometry:** GeoTIFF raster (WGS84)
- **Key columns:** Single band, people per pixel
- **Gaps:** Constrained WorldPop sets unsettled land to NoData, and cells outside the AMAC mask are also NoData. The 2020 vintage will not match a later census. Totals are modelled counts, not an enumerated ward census.

## How the files were prepared

National GRID3 and WorldPop files were downloaded from HDX, clipped to AMAC, and cleaned (empty geometries, blank names, duplicate coordinates). The cleaned layers above are what to open in QGIS.
