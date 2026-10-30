# Week 9: three small functions, then summarise_all wires them together
import csv


def read_rows(filename):
    """Open a CSV and return its rows as dictionaries."""
    with open(filename, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def clean_values(rows, column):
    """Pull one column, skip empty cells, turn the rest into numbers."""
    values = []
    for row in rows:
        raw = row[column].strip()
        if raw == "":
            continue
        values.append(float(raw.replace(",", "")))
    return values


def summarise_values(values):
    """Return count, smallest, largest and average, or an empty report."""
    if len(values) == 0:
        return {
            "count": 0,
            "smallest": None,
            "largest": None,
            "average": None,
        }
    return {
        "count": len(values),
        "smallest": min(values),
        "largest": max(values),
        "average": sum(values) / len(values),
    }


def summarise_all(filename, columns):
    """Read the file once and summarise every named column."""
    rows = read_rows(filename)
    report = {}
    for column in columns:
        values = clean_values(rows, column)
        report[column] = summarise_values(values)
    return report


report = summarise_all("abujawards.csv", ["pop_2020", "n_facilities"])
for column, stats in report.items():
    print(column, stats)
