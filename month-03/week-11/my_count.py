import geopandas as gpd

wards = gpd.read_file("data/processed/amac_wards.gpkg", layer="amac_wards").to_crs(
    epsg=32632
)
facilities = gpd.read_file(
    "data/processed/amac_health_facilities.gpkg", layer="amac_health_facilities"
).to_crs(epsg=32632)

joined = gpd.sjoin(
    facilities, wards[["ward", "geometry"]], how="inner", predicate="within"
)
counts = joined.groupby("ward").size().rename("facility_count").reset_index()
wards = wards.merge(counts, on="ward", how="left")
wards["facility_count"] = wards["facility_count"].fillna(0).astype(int)

print(wards[["ward", "facility_count"]])
print("Total counted:", wards["facility_count"].sum(), "of", len(facilities))
