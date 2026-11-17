"""Completed TODO 1 and TODO 2 from Assignment 5, B1."""
import csv
import io

RAW = """station,date,pm25
Adyar,2026-10-01,48
Adyar,2026-10-02,NA
Adyar,2026-10-03,
Guindy,2026-10-01,95
Guindy,2026-10-02,-5
Guindy,2026-10-03,121
Guindy,2026-10-04,1200
"""


def load_clean(text):
    """Return tuples for valid, non-negative PM2.5 readings up to 999."""
    rows = []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        value_text = (row["pm25"] or "").strip()
        if value_text == "" or value_text.upper() == "NA":
            continue
        try:
            value = float(value_text)
        except ValueError:
            continue
        if value < 0 or value > 999:
            continue
        rows.append((row["station"], row["date"], value))
    return rows


def min_max(values):
    """Scale values to 0–1, rounded to three decimals."""
    if not values:
        return []
    low = min(values)
    high = max(values)
    if high == low:
        return [0.0 for value in values]
    return [round((value - low) / (high - low), 3) for value in values]


clean = load_clean(RAW)
print(clean)
print(min_max([pm for _, _, pm in clean]))
