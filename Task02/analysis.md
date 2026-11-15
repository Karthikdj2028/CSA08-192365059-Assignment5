# A2 – Cleaning and normalisation design

## Cleaning rules

- Blank and NA readings: convert to missing (NULL). For an offline daily summary, fill a short gap with the previous value only when the sensor is known to be stable; otherwise use the station's monthly median. If no valid station value exists, keep NULL rather than inventing a reading.
- Impossible values: negative pollution readings or readings above the agreed sensor limit are sensor faults. Set them to NULL and log the row; do not include them in averages.
- Duplicate rows: keep the first row for a station/date/hour key and log later duplicates. The composite database key also prevents duplicates.
- Fahrenheit temperatures: convert to Celsius with (F - 32) * 5 / 9 before storage. Record the station's source unit in the stations table.
- Invalid number text: set to NULL and log the source value.

## Normalisation

Min-max normalisation maps values to 0–1:
x' = (x - minimum) / (maximum - minimum).
It is easy to compare values on the same dataset but is affected by outliers. When all values are equal, return zero to avoid division by zero.

Z-score standardisation uses (x - mean) / standard deviation. It shows how many standard deviations a value is from the mean and is useful for comparing unusual readings. It can be negative and is sensitive to outliers.

## Standard formats

- Dates: YYYY-MM-DD.
- Station names: trim outer spaces and store the canonical spelling.
- Numbers: store numeric values as REAL; do not keep number strings. Temperature is always Celsius in the cleaned table.
- Missing data: SQL NULL.

## Alternative: drop missing values

Dropping missing readings is O(n) and uses O(1) extra space in a streaming pass. Forward fill is also O(n) and needs the previous valid value. Computing a median by sorting valid values takes O(n log n) time and O(n) storage. Dropping can lower or raise daily averages if missingness is not random; it also reduces the count of valid readings. Filling can preserve the number of time slots but may hide a sensor outage, so the report should include a missing-value count.
