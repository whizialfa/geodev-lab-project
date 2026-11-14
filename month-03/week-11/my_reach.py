import geopandas as gpd

# 2 km straight-line reach matches the healthcare access question:
# which parts of AMAC sit more than 2 km from a mapped GRID3 facility.
# Map plate: scripts/build_week11_reach_plate.py (headless QGIS) → my_reach.png
wards = gpd.read_file("data/processed/amac_wards.gpkg", layer="amac_wards").to_crs(
    epsg=32632
)
facilities = gpd.read_file(
    "data/processed/amac_health_facilities.gpkg", layer="amac_health_facilities"
).to_crs(epsg=32632)

wards["area_km2"] = wards.area / 1_000_000
reach = facilities[["geometry"]].copy()
reach["geometry"] = reach.buffer(2000)
reach = reach.dissolve()

uncovered = gpd.overlay(wards, reach, how="difference")
uncovered["uncovered_km2"] = uncovered.area / 1_000_000
gaps = uncovered.groupby("ward", as_index=False)["uncovered_km2"].sum()
result = wards.merge(gaps, on="ward", how="left")
result["uncovered_km2"] = result["uncovered_km2"].fillna(0)
result["uncovered_pct"] = (result["uncovered_km2"] / result["area_km2"] * 100).round(1)

print(result[["ward", "area_km2", "uncovered_km2", "uncovered_pct"]].round(2))

result.to_file("data/processed/week11_amac_reach.gpkg", layer="ward_reach")
uncovered.to_file("data/processed/week11_amac_reach.gpkg", layer="uncovered")
print("Saved data/processed/week11_amac_reach.gpkg")
print("Map plate: env -u PYTHONPATH /Applications/QGIS.app/Contents/MacOS/bin/python3.9 scripts/build_week11_reach_plate.py")
