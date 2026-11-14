import geopandas as gpd

wards = gpd.read_file("data/processed/amac_wards.gpkg", layer="amac_wards")
invalid_before = (~wards.geometry.is_valid).sum()
print("Invalid geometries before:", invalid_before)

fixed = wards.copy()
fixed["geometry"] = fixed.geometry.make_valid()
invalid_after = (~fixed.geometry.is_valid).sum()
print("Invalid geometries after:", invalid_after)

if invalid_before == 0:
    print("No invalid polygons in amac_wards; make_valid left the layer unchanged.")

fixed.to_file("data/processed/week11_amac_wards_valid.gpkg", layer="amac_wards")
print("Saved data/processed/week11_amac_wards_valid.gpkg")
