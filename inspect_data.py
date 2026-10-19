# Week 8: open a CSV, clean two numeric columns, print a summary for each
import csv


def to_number(raw):
    """Turn a cell into a float, or return None if the cell is empty."""
    if raw is None:
        return None
    text = raw.strip()
    if text == "":
        return None
    return float(text.replace(",", ""))


def summarise(values):
    """Build a small dictionary of count, min, max, sum and mean."""
    count = len(values)
    total = sum(values)
    return {
        "count": count,
        "min": min(values),
        "max": max(values),
        "sum": total,
        "mean": total / count,
    }


with open("abujawards.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    pop_values = []
    facility_values = []
    for row in reader:
        pop = to_number(row["pop_2020"])
        if pop is None:
            continue
        facilities = to_number(row["n_facilities"])
        if facilities is None:
            continue
        pop_values.append(pop)
        facility_values.append(facilities)

print("pop_2020", summarise(pop_values))
print("n_facilities", summarise(facility_values))
