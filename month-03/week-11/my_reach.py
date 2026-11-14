import geopandas as gpd
import matplotlib.pyplot as plt

# 2 km straight-line reach matches the healthcare access question:
# which parts of AMAC sit more than 2 km from a mapped GRID3 facility.
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
result["uncovered_pct"] = (
    result["uncovered_km2"] / result["area_km2"] * 100
).round(1)

print(result[["ward", "area_km2", "uncovered_km2", "uncovered_pct"]].round(2))

result.to_file("data/processed/week11_amac_reach.gpkg", layer="ward_reach")
uncovered.to_file("data/processed/week11_amac_reach.gpkg", layer="uncovered")
print("Saved data/processed/week11_amac_reach.gpkg")

fig, ax = plt.subplots(figsize=(8, 9))
result.plot(ax=ax, color="#E6F2F3", edgecolor="#037E8E")
uncovered.plot(ax=ax, color="#C44E52", edgecolor="none", alpha=0.85)
facilities.plot(ax=ax, color="#094923", markersize=6)
ax.set_title("AMAC areas more than 2 km from a mapped health facility")
ax.set_axis_off()
fig.savefig("month-03/week-11/my_reach.png", dpi=150, bbox_inches="tight")
print("Map saved")
