"""Compare Python loops, pandas groupby and SQL GROUP BY."""
import csv
import cProfile
import io
import pstats
import sqlite3
import time
from datetime import date, timedelta
from pathlib import Path


BASE = Path(__file__).parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)


def generate_data(station_count, filename):
    start_day = date(2026, 1, 1)
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["station", "day", "hour", "pm25"])
        for station_number in range(1, station_count + 1):
            station = f"S{station_number:03d}"
            for day_number in range(365):
                day = (start_day + timedelta(days=day_number)).isoformat()
                for hour in range(24):
                    value = 10 + (station_number * 3 + day_number + hour) % 150
                    writer.writerow([station, day, hour, value])


def python_group(filename):
    totals = {}
    with open(filename, "r", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            key = (row["station"], row["day"])
            if key not in totals:
                totals[key] = [0.0, 0]
            totals[key][0] += float(row["pm25"])
            totals[key][1] += 1
    return {key: round(value[0] / value[1], 5)
            for key, value in totals.items()}


def pandas_group(filename):
    import pandas as pd
    frame = pd.read_csv(filename)
    grouped = frame.groupby(["station", "day"])["pm25"].mean()
    return {key: round(float(value), 5) for key, value in grouped.items()}


def sql_group(filename):
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE readings (station TEXT, day TEXT, hour INTEGER, pm25 REAL)"
    )
    with open(filename, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        connection.executemany(
            "INSERT INTO readings VALUES (?, ?, ?, ?)",
            ((row["station"], row["day"], int(row["hour"]), float(row["pm25"]))
             for row in reader)
        )
    result = connection.execute("""
        SELECT station, day, AVG(pm25)
        FROM readings
        GROUP BY station, day
    """).fetchall()
    connection.close()
    return {(station, day): round(value, 5) for station, day, value in result}


def same_results(first, second):
    if first.keys() != second.keys():
        return False
    return all(abs(first[key] - second[key]) < 0.00001 for key in first)


def main():
    rows = []
    for station_count in (1, 12, 120):
        filename = DATA / f"air_{station_count}_stations.csv"
        start = time.perf_counter()
        generate_data(station_count, filename)
        generation_time = time.perf_counter() - start
        row_count = station_count * 365 * 24

        start = time.perf_counter()
        loop_result = python_group(filename)
        loop_time = time.perf_counter() - start

        start = time.perf_counter()
        pandas_result = pandas_group(filename)
        pandas_time = time.perf_counter() - start

        start = time.perf_counter()
        sql_result = sql_group(filename)
        sql_time = time.perf_counter() - start

        correct = same_results(loop_result, pandas_result) and same_results(loop_result, sql_result)
        rows.append((station_count, row_count, round(generation_time, 4),
                     round(loop_time, 4), round(pandas_time, 4),
                     round(sql_time, 4), correct))
        print(
            f"stations={station_count}, rows={row_count}, "
            f"generate={generation_time:.4f}s, Python={loop_time:.4f}s, "
            f"pandas={pandas_time:.4f}s, SQL(load+query)={sql_time:.4f}s, "
            f"same={correct}"
        )

        if station_count == 1:
            print("\nPROFILE OF PYTHON LOOP (one station)")
            profiler = cProfile.Profile()
            profiler.enable()
            python_group(filename)
            profiler.disable()
            pstats.Stats(profiler).sort_stats("cumulative").print_stats(5)

    output = BASE / "timing_results.csv"
    with open(output, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["stations", "rows", "generation_seconds",
                         "python_seconds", "pandas_seconds",
                         "sql_load_and_query_seconds", "same_results"])
        writer.writerows(rows)
    print("\nRaw timings saved to:", output)


if __name__ == "__main__":
    main()
