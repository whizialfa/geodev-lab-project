import geopandas as gpd

wards = gpd.read_file("data/processed/amac_wards.gpkg", layer="amac_wards")
facilities = gpd.read_file(
    "data/processed/amac_health_facilities.gpkg", layer="amac_health_facilities"
)

print("Wards CRS:", wards.crs)
print("Facilities CRS:", facilities.crs)
print("Suggested UTM:", wards.estimate_utm_crs())

wards_utm = wards.to_crs(epsg=32632)
facilities_utm = facilities.to_crs(epsg=32632)
wards_utm["area_km2"] = wards_utm.area / 1_000_000

print(wards_utm[["ward", "area_km2"]].round(2))
print("AMAC wards total area:", round(wards_utm["area_km2"].sum(), 1), "km2")
print("Facilities after reproject:", len(facilities_utm), facilities_utm.crs)
