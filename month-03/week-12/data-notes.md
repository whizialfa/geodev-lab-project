# Week 12 raster notes

Rasters stay on this laptop (see root `.gitignore` for `*.tif`). Nothing below is committed as a GeoTIFF.

## Teaching set (`data/raw/week12/`)

| File | What it is | CRS | Notes |
|---|---|---|---|
| `dem.tif` | Synthetic 400×400 DEM, 30 m cells | EPSG:32643 | Nodata −9999 in a NE patch; used by inspect / read / sample / clip / zonal / reproject |
| `scene.tif` | Synthetic 2-band red+NIR scene, 10 m | EPSG:32643 | Float reflectance already; used by `ndvi.py` |
| `ndvi.tif` | Teaching NDVI written by `ndvi.py` | EPSG:32643 | Local output only |
| `dem_cut.tif` | DEM clipped to a 2.5 km circle | EPSG:32643 | Written by `clip_raster.py` |
| `dem_wgs84.tif` | DEM reprojected to lon/lat | EPSG:4326 | Written by `reproject_raster.py` |
| `districts.gpkg` | Two rectangle districts (vector) | EPSG:32643 | Committed if small; used by guided zonal |

## My AMAC set (`data/raw/week12_amac/`)

| File | What it is | Source | Notes |
|---|---|---|---|
| `B4_red.tif` | Landsat-9 C2 L2 Band 4 (red), windowed to study wards | Planetary Computer STAC `landsat-c2-l2` | Scene **LC09_L2SP_189054_20241108_02_T1**, date **2024-11-08**, cloud cover **0.0%**, WRS 189/054, CRS EPSG:32632 |
| `B5_nir.tif` | Landsat-9 C2 L2 Band 5 (NIR) | same scene | Same window and CRS as B4 |
| `ndvi_amac.tif` | NDVI = (NIR−Red)/(NIR+Red) after scale 0.0000275 and offset −0.2, **masked to the ten study ward polygons** | computed by `my_index.py` | Local output; outside wards is nodata |
| `dem_amac.tif` | Copernicus GLO-30 DEM mosaic clipped to ward bbox | Planetary Computer `cop-dem-glo-30` | EPSG:4326; inspected in `my_inspect.py` |
| `scene_meta.json` | Scene id, date, cloud cover | STAC properties | Helper; not required for marking |

Scale/offset for Collection 2 Level-2 surface reflectance: `reflectance = DN × 0.0000275 − 0.2` (USGS). Convert to `float32` before applying.
