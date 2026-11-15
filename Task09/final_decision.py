"""Evaluate simple complaint AI and measure a station/day SQL index."""
import re
import sqlite3
import time
from collections import Counter

POSITIVE = {"good", "clean", "fast", "helpful", "improved"}
NEGATIVE = {"bad", "dirty", "slow", "rude", "smoke", "broken"}
NEGATORS = {"not", "never", "no"}
STOP = {"the", "is", "and", "are", "from", "was", "a", "an", "in", "at", "to"}

# Each expected label was assigned by manually reading the sentence.
COMPLAINTS = [
    ("Air is clean near the park.", "positive"),
    ("Bus service is fast today.", "positive"),
    ("The officer was helpful.", "positive"),
    ("Air quality improved this week.", "positive"),
    ("Good work by the cleaning team.", "positive"),
    ("Water and air are clean.", "positive"),
    ("The road cleaning was helpful.", "positive"),
    ("Service is good and fast.", "positive"),
    ("Pollution reduced and air improved.", "positive"),
    ("Not bad, the area is clean.", "positive"),
    ("The street is never dirty.", "positive"),
    ("The bus is not slow.", "positive"),
    ("The staff were not rude.", "positive"),
    ("There is no smoke today.", "positive"),
    ("Clean and helpful service.", "positive"),
    ("Air is bad near the factory.", "negative"),
    ("Smoke is coming from the factory.", "negative"),
    ("The road is dirty.", "negative"),
    ("The bus is slow every morning.", "negative"),
    ("The staff were rude.", "negative"),
    ("The system is broken.", "negative"),
    ("Smoke and dirty roads are bad.", "negative"),
    ("The air is not clean.", "negative"),
    ("The staff were never helpful.", "negative"),
    ("There is no good air near the road.", "negative"),
    ("The service is bad and slow.", "negative"),
    ("Factory smoke makes the area dirty.", "negative"),
    ("The reply was not helpful.", "negative"),
    ("The pollution has not improved.", "negative"),
    ("The bus is not fast.", "negative"),
    ("Air is dirty near the bus stand.", "negative"),
    ("The water is bad.", "negative"),
    ("Smoke makes breathing difficult.", "negative"),
    ("The service is rude.", "negative"),
    ("The road is broken and dirty.", "negative"),
    ("The traffic is slow.", "negative"),
    ("The air smells of smoke.", "negative"),
    ("This is not good.", "negative"),
    ("The area is dirty and polluted.", "negative"),
    ("The complaint was not resolved.", "neutral"),
    ("The station is near the market.", "neutral"),
    ("A report was sent yesterday.", "neutral"),
    ("The reading was recorded at noon.", "neutral"),
    ("Please visit the public office.", "neutral"),
    ("The road is near the school.", "neutral"),
    ("The meeting starts at ten.", "neutral"),
    ("The station has a new sensor.", "neutral"),
    ("A citizen sent a message.", "neutral"),
    ("The data was stored today.", "neutral"),
    ("The weather changed this morning.", "neutral"),
]


def sentiment_score(text):
    words = re.findall(r"[a-z]+", text.lower())
    total = 0
    previous_negator = False
    for word in words:
        value = 1 if word in POSITIVE else -1 if word in NEGATIVE else 0
        if previous_negator:
            value = -value
        total += value
        previous_negator = word in NEGATORS
    return total


def sentiment_label(text):
    value = sentiment_score(text)
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "neutral"


def ranked_summary(text, count=3):
    sentences = [item.strip() for item in re.split(r"[.!?]+", text) if item.strip()]
    words = [w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOP]
    frequency = Counter(words)
    ranked = []
    for index, sentence in enumerate(sentences):
        sentence_words = [w for w in re.findall(r"[a-z]+", sentence.lower()) if w not in STOP]
        ranked.append((sum(frequency[w] for w in sentence_words), index, sentence))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    chosen = sorted(ranked[:count], key=lambda item: item[1])
    return [item[2] for item in chosen]


def first_sentences(text, count=3):
    return [item.strip() for item in re.split(r"[.!?]+", text) if item.strip()][:count]


def index_experiment():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE readings (station TEXT, day TEXT, pm25 REAL)")
    rows = []
    for station_number in range(100):
        station = f"S{station_number:03d}"
        for index in range(1000):
            month = (index // 28) % 12 + 1
            day = index % 28 + 1
            date_text = f"2026-{month:02d}-{day:02d}"
            value = float(10 + (station_number + index) % 150)
            rows.append((station, date_text, value))
    connection.executemany("INSERT INTO readings VALUES (?, ?, ?)", rows)
    connection.commit()

    station, day = "S050", "2026-06-01"
    query = "SELECT AVG(pm25) FROM readings WHERE station = ? AND day = ?"
    start = time.perf_counter()
    for _ in range(300):
        before = connection.execute(query, (station, day)).fetchone()[0]
    no_index_time = time.perf_counter() - start

    connection.execute("CREATE INDEX idx_station_day ON readings(station, day)")
    connection.commit()
    start = time.perf_counter()
    for _ in range(300):
        after = connection.execute(query, (station, day)).fetchone()[0]
    index_time = time.perf_counter() - start

    print("\nSQL INDEX EXPERIMENT")
    print("Rows:", len(rows), "Repeated queries:", 300)
    print("Without index:", round(no_index_time, 6), "seconds")
    print("With index   :", round(index_time, 6), "seconds")
    print("Same result:", before == after)
    connection.close()


if __name__ == "__main__":
    agreed = 0
    print("SENTIMENT AGREEMENT")
    for text, expected in COMPLAINTS:
        actual = sentiment_label(text)
        if actual == expected:
            agreed += 1
        else:
            print("Review:", actual, "expected:", expected, "|", text)
    print("Agreement:", agreed, "/", len(COMPLAINTS))

    combined = " ".join(text for text, expected in COMPLAINTS)
    print("\nFREQUENCY-BASED SUMMARY")
    for sentence in ranked_summary(combined):
        print("-", sentence)
    print("\nFIRST THREE SENTENCES")
    for sentence in first_sentences(combined):
        print("-", sentence)

    index_experiment()
