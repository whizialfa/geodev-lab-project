import geopandas as gpd

path = "data/processed/amac_wards.gpkg"
print(gpd.list_layers(path))
wards = gpd.read_file(path, layer="amac_wards")
print(wards.head())
print("Rows and columns:", wards.shape)
print(wards.geom_type.value_counts())
print("CRS:", wards.crs)
print("Bounds:", wards.total_bounds)
