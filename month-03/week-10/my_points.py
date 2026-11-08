import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

table = pd.read_csv("data/raw/amac_facilities.csv")
print(table.head(3))
print("Rows:", len(table))

facilities = gpd.GeoDataFrame(
    table,
    geometry=gpd.points_from_xy(table["longitude"], table["latitude"]),
    crs="EPSG:4326",
)
print(facilities.head(3))
print(facilities.crs)
facilities.to_file("data/processed/amac_facilities_from_csv.gpkg", layer="facilities")
print("Saved", len(facilities), "facilities")

wards = gpd.read_file("data/processed/amac_wards.gpkg", layer="amac_wards")
fig, ax = plt.subplots(figsize=(7, 8))
wards.plot(ax=ax, color="#E6F2F3", edgecolor="#037E8E")
facilities.plot(ax=ax, color="#094923", markersize=8)
ax.set_title("AMAC health facilities from CSV")
ax.set_axis_off()
fig.savefig("month-03/week-10/my_points_check.png", dpi=150, bbox_inches="tight")
print("Check map saved")
