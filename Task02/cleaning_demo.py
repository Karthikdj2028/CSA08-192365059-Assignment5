"""Demonstrate cleaning, Fahrenheit conversion and normalisation."""
from statistics import mean, median, pstdev


def read_number(value):
    text = str(value).strip()
    if text == "" or text.upper() == "NA":
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if number < 0 or number > 999:
        return None
    return number


def fill_missing_with_median(values):
    valid = [value for value in values if value is not None]
    if not valid:
        return values
    middle = median(valid)
    return [middle if value is None else value for value in values]


def to_celsius(value, unit):
    if value is None:
        return None
    if unit.upper() == "F":
        return round((value - 32) * 5 / 9, 2)
    return value


def min_max(values):
    low = min(values)
    high = max(values)
    if high == low:
        return [0.0 for value in values]
    return [round((value - low) / (high - low), 3) for value in values]


def z_score(values):
    average = mean(values)
    deviation = pstdev(values)
    if deviation == 0:
        return [0.0 for value in values]
    return [round((value - average) / deviation, 3) for value in values]


if __name__ == "__main__":
    raw = ["48", "NA", "", "95", "-5", "121", "1500"]
    cleaned = [read_number(value) for value in raw]
    filled = fill_missing_with_median(cleaned)
    print("Raw PM2.5:", raw)
    print("Clean values (invalid/missing -> None):", cleaned)
    print("Median-filled values:", filled)
    print("Min-max:", min_max(filled))
    print("Z-score:", z_score(filled))
    print("86 F in Celsius:", to_celsius(86, "F"))
    print("Station name:", "  adyar ".strip().title())
