# A1 – Design the Data Acquisition

## A1.1 Source inspection

Each station sends a daily CSV file. A row contains station name, date, hour, PM2.5, PM10, NO2 and temperature. The first row is a header. Example:

station,date,hour,pm25,pm10,no2,temperature

Expected data-quality problems:
- Missing station/date/hour: blank field, so the row cannot be identified reliably.
- Missing measurement: blank or NA, for example PM2.5 = NA.
- Negative sensor reading: PM2.5 = -5.
- Impossibly large reading: PM2.5 = 1500 when the agreed accepted range is 0–999.
- Duplicate record: same station, date and hour occurs twice.
- Unit mismatch: temperature 86 at a Fahrenheit station means 30 Celsius.
- Wrong type: text such as "high" in a numeric field.
- Wrong date/hour format: a date that cannot be parsed or hour outside 0–23.
- Wrong header or delimiter: CSV columns cannot be mapped correctly.

## A1.2 SQLite storage design

stations stores one row per monitoring station. station_id is the integer primary key; station_name is unique; temperature_unit records the source unit.

readings stores one hourly observation. Its composite primary key is station_id + day + hour, so the same station-hour cannot be inserted twice. station_id is also a foreign key. Missing optional measurements are stored as NULL.

CSV mapping:
- station name is looked up in stations to obtain station_id.
- date becomes day in ISO format YYYY-MM-DD.
- hour becomes an integer from 0 to 23.
- PM2.5, PM10 and NO2 become REAL values or NULL.
- temperature is converted to Celsius before storing as temperature_c.

The table definition is in schema.sql. An index on station_id and day supports common station/day filters.

## A1.3 CSV versus SQL questions

1. Average PM2.5 for one station in October: CSV requires opening and scanning the files and selecting matching rows; SQL uses WHERE station_id = ? AND day BETWEEN ? AND ? with AVG(pm25).
2. Find the maximum PM10 per station: CSV requires a loop and dictionary of maximums; SQL uses GROUP BY station_id and MAX(pm10).
3. Find the worst hour of a day: CSV requires grouping records by hour; SQL uses GROUP BY hour and ORDER BY AVG(pm25) DESC.

CSV is useful as the incoming source and for exchange. SQLite is better for repeated questions, joins, aggregation and indexes.

## Alternative: CSV and pandas for each question

A full CSV scan is O(n) for n readings for every question. A database index can reduce a selective search to approximately O(log n + matching rows). CSV files need disk storage; pandas must load relevant data into memory for every question. SQLite stores the cleaned data on disk and reads the selected records. Pandas is still useful for one-time analysis or vectorised cleaning.
