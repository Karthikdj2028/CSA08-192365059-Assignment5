"""Demonstrate cleaning, Fahrenheit conversion and normalisation."""
from statistics import mean, median, pstdev


def read_number(value):
    text = str(value).strip()
    if text == "" or text.upper() == "NA":
        return None, "missing"
    try:
        number = float(text)
    except ValueError:
        return None, "invalid"
    if number < 0 or number > 999:
        return None, "invalid"
    return number, "valid"


def fill_missing_with_median(parsed):
    valid = [value for value, status in parsed if status == "valid"]
    if not valid:
        return [None for value, status in parsed]
    middle = median(valid)
    # Only missing values are filled. Impossible values stay None.
    return [middle if status == "missing" else value
            for value, status in parsed]


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
    parsed = [read_number(value) for value in raw]
    filled = fill_missing_with_median(parsed)
    valid_values = [value for value in filled if value is not None]

    print("Raw PM2.5:", raw)
    print("Parsed values and status:", parsed)
    print("After missing-value median fill:", filled)
    print("Invalid sensor faults remain None.")
    print("Min-max:", min_max(valid_values))
    print("Z-score:", z_score(valid_values))
    print("86 F in Celsius:", to_celsius(86, "F"))
    print("Station name:", "  adyar ".strip().title())
