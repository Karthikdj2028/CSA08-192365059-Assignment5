"""Acquire, clean, store, query and chart the sample air-quality data."""
import csv
import sqlite3
from datetime import date
from pathlib import Path

BASE = Path(__file__).parent
DATA_FILE = BASE / "data" / "raw_readings.csv"
OUTPUT = BASE / "output"
CHARTS = BASE / "charts"
DB_FILE = BASE / "air_quality.db"
TEMP_UNITS = {"Adyar": "C", "Guindy": "C", "Velachery": "F", "T Nagar": "F"}


def clean_number(text, low, high):
    if text is None or text.strip() == "" or text.strip().upper() == "NA":
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    if value < low or value > high:
        return None
    return value


def clean_temperature(text, unit):
    value = clean_number(text, -100, 250)
    if value is None:
        return None
    if unit == "F":
        value = (value - 32) * 5 / 9
    if value < -50 or value > 60:
        return None
    return round(value, 2)


def has_bad_text_or_range(text, low, high):
    if text is None or text.strip() == "" or text.strip().upper() == "NA":
        return False
    try:
        value = float(text)
    except ValueError:
        return True
    return value < low or value > high


def load_clean():
    cleaned = []
    errors = []
    seen = set()
    raw_count = 0

    with open(DATA_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        required = ["station", "date", "hour", "pm25", "pm10", "no2", "temperature"]
        if reader.fieldnames != required:
            raise ValueError("CSV header does not match the required columns")

        for line_number, row in enumerate(reader, start=2):
            raw_count += 1
            station = (row["station"] or "").strip().title()
            day = (row["date"] or "").strip()
            try:
                date.fromisoformat(day)
            except ValueError:
                errors.append((line_number, "invalid date; row skipped"))
                continue

            try:
                hour = int(row["hour"])
            except (TypeError, ValueError):
                errors.append((line_number, "invalid hour; row skipped"))
                continue

            if not station or hour < 0 or hour > 23:
                errors.append((line_number, "missing station or invalid hour; row skipped"))
                continue

            pm25 = clean_number(row["pm25"], 0, 999)
            if pm25 is None:
                errors.append((line_number, "missing or impossible PM2.5; row skipped"))
                continue

            key = (station, day, hour)
            if key in seen:
                errors.append((line_number, "duplicate station/date/hour; later row skipped"))
                continue
            seen.add(key)

            pm10 = clean_number(row["pm10"], 0, 2000)
            no2 = clean_number(row["no2"], 0, 1000)
            unit = TEMP_UNITS.get(station, "C")
            temp_c = clean_temperature(row["temperature"], unit)

            for field, text, low, high in (
                ("PM10", row["pm10"], 0, 2000),
                ("NO2", row["no2"], 0, 1000),
                ("temperature", row["temperature"], -100, 250)
            ):
                if has_bad_text_or_range(text, low, high):
                    errors.append((line_number, f"invalid {field}; stored as NULL"))

            if pm10 is None and (row["pm10"] or "").strip() == "":
                errors.append((line_number, "missing PM10; stored as NULL"))
            if no2 is None and (row["no2"] or "").strip() == "":
                errors.append((line_number, "missing NO2; stored as NULL"))
            if temp_c is None and (row["temperature"] or "").strip() == "":
                errors.append((line_number, "missing temperature; stored as NULL"))

            cleaned.append((station, day, hour, pm25, pm10, no2, temp_c))

    return raw_count, cleaned, errors


def store_sqlite(rows):
    if DB_FILE.exists():
        DB_FILE.unlink()
    connection = sqlite3.connect(DB_FILE)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("""
        CREATE TABLE stations (
            station_id INTEGER PRIMARY KEY,
            station_name TEXT NOT NULL UNIQUE,
            temperature_unit TEXT NOT NULL
        )
    """)
    connection.execute("""
        CREATE TABLE readings (
            station_id INTEGER NOT NULL,
            day TEXT NOT NULL,
            hour INTEGER NOT NULL,
            pm25 REAL NOT NULL,
            pm10 REAL,
            no2 REAL,
            temperature_c REAL,
            PRIMARY KEY (station_id, day, hour),
            FOREIGN KEY (station_id) REFERENCES stations(station_id)
        )
    """)

    stations = sorted({row[0] for row in rows})
    connection.executemany(
        "INSERT INTO stations (station_name, temperature_unit) VALUES (?, ?)",
        [(name, TEMP_UNITS.get(name, "C")) for name in stations]
    )
    station_ids = dict(connection.execute(
        "SELECT station_name, station_id FROM stations"
    ).fetchall())
    values = [
        (station_ids[station], day, hour, pm25, pm10, no2, temp)
        for station, day, hour, pm25, pm10, no2, temp in rows
    ]
    connection.executemany("INSERT INTO readings VALUES (?, ?, ?, ?, ?, ?, ?)", values)
    connection.execute("CREATE INDEX idx_station_day ON readings(station_id, day)")
    connection.commit()
    return connection


def make_charts(connection):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed. Run: python -m pip install -r requirements.txt")
        return

    CHARTS.mkdir(parents=True, exist_ok=True)

    trend = connection.execute("""
        SELECT day, AVG(pm25) FROM readings
        WHERE station_id = (SELECT station_id FROM stations WHERE station_name = 'Adyar')
        GROUP BY day ORDER BY day
    """).fetchall()
    if trend:
        plt.figure()
        plt.plot([r[0] for r in trend], [r[1] for r in trend], marker="o")
        plt.title("Adyar PM2.5 Trend")
        plt.xlabel("Date")
        plt.ylabel("PM2.5 (micrograms/m3)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(CHARTS / "pm25_trend.png")
        plt.close()

    station_means = connection.execute("""
        SELECT s.station_name, AVG(r.pm25)
        FROM readings r JOIN stations s ON r.station_id = s.station_id
        GROUP BY s.station_name ORDER BY s.station_name
    """).fetchall()
    if station_means:
        plt.figure()
        plt.bar([r[0] for r in station_means], [r[1] for r in station_means])
        plt.title("Average PM2.5 by Station")
        plt.xlabel("Station")
        plt.ylabel("Mean PM2.5 (micrograms/m3)")
        plt.tight_layout()
        plt.savefig(CHARTS / "station_comparison.png")
        plt.close()

    pairs = connection.execute(
        "SELECT temperature_c, pm25 FROM readings WHERE temperature_c IS NOT NULL"
    ).fetchall()
    if pairs:
        plt.figure()
        plt.scatter([r[0] for r in pairs], [r[1] for r in pairs])
        plt.title("Temperature and PM2.5")
        plt.xlabel("Temperature (C)")
        plt.ylabel("PM2.5 (micrograms/m3)")
        plt.tight_layout()
        plt.savefig(CHARTS / "temperature_vs_pm25.png")
        plt.close()

    hours = connection.execute(
        "SELECT hour, AVG(pm25) FROM readings GROUP BY hour ORDER BY hour"
    ).fetchall()
    if hours:
        plt.figure()
        plt.bar([r[0] for r in hours], [r[1] for r in hours])
        plt.title("Average PM2.5 by Hour")
        plt.xlabel("Hour of Day")
        plt.ylabel("Mean PM2.5 (micrograms/m3)")
        plt.tight_layout()
        plt.savefig(CHARTS / "worst_hours.png")
        plt.close()


def main():
    OUTPUT.mkdir(exist_ok=True)
    raw_count, rows, errors = load_clean()
    print("Raw rows:", raw_count)
    print("Clean rows:", len(rows))
    print("Rejected, corrected or duplicate records:", len(errors))

    with open(OUTPUT / "cleaned_readings.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["station", "date", "hour", "pm25", "pm10", "no2", "temperature_c"])
        writer.writerows(rows)
    with open(OUTPUT / "errors.log", "w", encoding="utf-8") as file:
        for line_number, message in errors:
            file.write(f"Line {line_number}: {message}\n")

    connection = store_sqlite(rows)
    print("\nDAILY SUMMARY")
    for result in connection.execute("""
        SELECT s.station_name, r.day, MIN(r.pm25), MAX(r.pm25),
               ROUND(AVG(r.pm25), 2), COUNT(r.pm25)
        FROM readings r JOIN stations s ON r.station_id = s.station_id
        GROUP BY s.station_name, r.day ORDER BY s.station_name, r.day
    """):
        print(result)

    print("\nAverage PM2.5 at Adyar:")
    print(connection.execute("""
        SELECT ROUND(AVG(pm25), 2) FROM readings
        WHERE station_id = (SELECT station_id FROM stations WHERE station_name = ?)
    """, ("Adyar",)).fetchone()[0])

    print("\nMaximum PM10 by station:")
    for result in connection.execute("""
        SELECT s.station_name, MAX(r.pm10)
        FROM readings r JOIN stations s ON r.station_id = s.station_id
        GROUP BY s.station_name
    """):
        print(result)

    make_charts(connection)
    connection.close()
    print("\nCleaned CSV, SQLite database, charts and error log have been saved.")


if __name__ == "__main__":
    main()
