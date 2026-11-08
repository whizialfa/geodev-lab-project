import geopandas as gpd
import matplotlib.pyplot as plt

wards = gpd.read_file("data/processed/amac_wards_joined.gpkg", layer="wards_joined")
facilities = gpd.read_file(
    "data/processed/amac_facilities_from_csv.gpkg", layer="facilities"
)

fig, ax = plt.subplots(figsize=(7, 8))
wards.plot(ax=ax, color="#E6F2F3", edgecolor="#037E8E")
facilities.plot(ax=ax, color="#094923", markersize=8)
ax.set_title("Health facilities in AMAC wards")
ax.set_axis_off()
fig.savefig("month-03/week-10/my_map.png", dpi=150, bbox_inches="tight")
print("Map saved")
