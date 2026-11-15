"""Test damaged source files, SQL injection and batch insertion."""
import csv
import sqlite3
import tempfile
import time
from pathlib import Path

EXPECTED = ["station", "date", "pm25"]


def inspect_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != EXPECTED:
            raise ValueError("missing or incorrect CSV columns")
        return list(reader)


def simple_score(text):
    positive = {"good", "clean", "helpful"}
    negative = {"bad", "dirty", "smoke"}
    words = text.lower().replace(",", " ").replace(".", " ").split()
    total = 0
    for index, word in enumerate(words):
        value = 1 if word in positive else -1 if word in negative else 0
        if index > 0 and words[index - 1] == "not":
            value = -value
        total += value
    return total


def insert_with_execute(rows):
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE readings (station TEXT, day TEXT, pm25 REAL)")
    start = time.perf_counter()
    for row in rows:
        connection.execute("INSERT INTO readings VALUES (?, ?, ?)", row)
    connection.commit()
    elapsed = time.perf_counter() - start
    connection.close()
    return elapsed


def insert_with_many(rows):
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE readings (station TEXT, day TEXT, pm25 REAL)")
    start = time.perf_counter()
    connection.executemany("INSERT INTO readings VALUES (?, ?, ?)", rows)
    connection.commit()
    elapsed = time.perf_counter() - start
    connection.close()
    return elapsed


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as folder:
        folder = Path(folder)
        (folder / "missing_column.csv").write_text(
            "station,date\nAdyar,2026-10-01\n", encoding="utf-8")
        (folder / "wrong_delimiter.csv").write_text(
            "station;date;pm25\nAdyar;2026-10-01;48\n", encoding="utf-8")
        (folder / "empty.csv").write_text("", encoding="utf-8")
        (folder / "utf16.csv").write_bytes(
            "station,date,pm25\nAdyar,2026-10-01,48\n".encode("utf-16"))

        print("ADVERSARIAL CSV FILES")
        for name in ("missing_column.csv", "wrong_delimiter.csv", "empty.csv", "utf16.csv"):
            try:
                print(name, "rows:", inspect_csv(folder / name))
            except (ValueError, UnicodeDecodeError) as error:
                print(name, "handled:", type(error).__name__, error)

    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE aq (station TEXT, pm25 REAL)")
    connection.executemany(
        "INSERT INTO aq VALUES (?, ?)",
        [("Adyar", 48.0), ("Guindy", 95.0), ("Velachery", 65.0)]
    )
    payload = "Adyar' OR '1'='1"
    unsafe = "SELECT COUNT(*) FROM aq WHERE station = '" + payload + "'"
    print("\nUNSAFE string-built query count:", connection.execute(unsafe).fetchone()[0])
    safe = connection.execute(
        "SELECT COUNT(*) FROM aq WHERE station = ?", (payload,)
    ).fetchone()[0]
    print("SAFE parameterised query count:", safe)
    connection.close()

    samples = [
        "good air",
        "not good air",
        "not bad service",
        "great, another dusty day",
        "not never clean"
    ]
    print("\nSENTIMENT EDGE CASES")
    for item in samples:
        print(simple_score(item), "|", item)

    rows = [("Adyar", "2026-10-01", float(i % 150)) for i in range(5000)]
    print("\nINSERT TIMING FOR 5,000 ROWS")
    print("execute loop:", round(insert_with_execute(rows), 6), "seconds")
    print("executemany :", round(insert_with_many(rows), 6), "seconds")
