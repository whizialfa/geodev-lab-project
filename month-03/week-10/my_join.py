import re

import pandas as pd
import geopandas as gpd

wards = gpd.read_file("data/processed/amac_wards.gpkg", layer="amac_wards")
pop = pd.read_csv("data/raw/abujawards.csv")

# pop_2020 and pop_per_facility arrived as text with commas
pop["pop_2020"] = (
    pop["pop_2020"].astype(str).str.replace(",", "", regex=False).astype(int)
)

first_try = wards.merge(pop, left_on="ward", right_on="ward", how="left")
matched = first_try["pop_2020"].notna().sum()
print("Matched on first try:", matched, "of", len(wards))


def clean_name(name):
    text = str(name).strip().upper().replace("-", " ")
    text = text.replace("CENTER", "CENTRE")
    text = re.sub(r"\s+\d+$", "", text)  # "Garki 1" -> "Garki"
    return text


wards = wards.copy()
pop = pop.copy()
wards["join_key"] = wards["ward"].apply(clean_name)
pop["join_key"] = pop["ward"].apply(clean_name)

joined = wards.merge(pop[["join_key", "pop_2020", "n_facilities", "lga"]], on="join_key", how="left")
matched = joined["pop_2020"].notna().sum()
print("Matched after cleaning:", matched, "of", len(wards))
print(joined[["ward", "join_key", "pop_2020", "n_facilities"]])

joined.to_file("data/processed/amac_wards_joined.gpkg", layer="wards_joined")
print("Saved joined wards")
