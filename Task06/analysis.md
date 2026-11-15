# B1 – Implement and validate the cleaning pipeline

The program reads the raw CSV with csv.DictReader. It converts numeric values, treats blank/NA/negative/out-of-range readings as missing, and skips a row when PM2.5 is missing or impossible because PM2.5 is the required analysis measure. Other invalid optional measurements are stored as NULL. Temperature from Velachery and T Nagar is converted from Fahrenheit to Celsius. A set of (station, date, hour) keys removes duplicate records.

The clean rows are written to cleaned_readings.csv and inserted into SQLite using executemany(). The database has stations and readings tables, a composite primary key and an index on station_id/day.

SQL summaries answer:
1. Daily minimum, maximum, mean and valid reading count per station.
2. Average PM2.5 for Adyar.
3. Maximum PM10 per station.

Four charts are saved with titles and labelled axes: Adyar trend, station comparison, temperature-vs-PM2.5 scatter and average PM2.5 by hour.

Compare the printed raw row count, clean row count and errors.log against the sample input. If a design rule changes, update this note and explain why.
