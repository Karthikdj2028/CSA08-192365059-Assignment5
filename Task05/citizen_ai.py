"""Lexicon sentiment, extractive summary and a simple air-quality chatbot."""
import re
import sqlite3
from collections import Counter

POSITIVE = {"good", "clean", "fast", "helpful", "improved"}
NEGATIVE = {"bad", "dirty", "slow", "rude", "smoke", "broken"}
NEGATORS = {"not", "never", "no"}
STOP_WORDS = {"the", "is", "and", "are", "from", "was", "a", "an", "in", "at", "to"}


def score(text):
    words = re.findall(r"[a-z]+", text.lower())
    total = 0
    previous_was_negator = False
    for word in words:
        value = 1 if word in POSITIVE else -1 if word in NEGATIVE else 0
        if previous_was_negator:
            value = -value
        total += value
        previous_was_negator = word in NEGATORS
    return total


def label(text):
    value = score(text)
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "neutral"


def summarise(text, limit=2):
    sentences = [part.strip() for part in re.split(r"[.!?]+", text) if part.strip()]
    words = re.findall(r"[a-z]+", text.lower())
    important = [word for word in words if word not in STOP_WORDS]
    frequency = Counter(important)

    ranked = []
    for index, sentence in enumerate(sentences):
        sentence_words = re.findall(r"[a-z]+", sentence.lower())
        value = sum(frequency[word] for word in sentence_words if word not in STOP_WORDS)
        ranked.append((value, index, sentence))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    chosen = sorted(ranked[:limit], key=lambda item: item[1])
    return [item[2] for item in chosen]


def answer_question(connection, question):
    """Match a station name in the question and ask SQLite for latest mean PM2.5."""
    station_names = [row[0] for row in connection.execute(
        "SELECT DISTINCT station FROM readings"
    )]
    for station in station_names:
        if station.lower() in question.lower():
            day = connection.execute(
                "SELECT MAX(day) FROM readings WHERE station = ?", (station,)
            ).fetchone()[0]
            average = connection.execute(
                "SELECT AVG(pm25) FROM readings WHERE station = ? AND day = ?",
                (station, day)
            ).fetchone()[0]
            return f"PM2.5 at {station} on {day} is {average:.1f}"
    return "Please mention a station name in the question."


if __name__ == "__main__":
    complaints = [
        "Roads are clean and the bus was fast.",
        "Smoke from the factory, air is bad.",
        "The staff were not helpful.",
        "Not bad, service improved.",
        "The road is dirty near the school.",
    ]
    print("SENTIMENT")
    for complaint in complaints:
        print(label(complaint), "|", complaint)

    text = (
        "The road near the school is dirty. Smoke is present every evening. "
        "Children have coughs and the air is bad. Please clean the road."
    )
    print("\nEXTRACTIVE SUMMARY")
    for sentence in summarise(text):
        print("-", sentence)

    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE readings (station TEXT, day TEXT, pm25 REAL)")
    con.executemany(
        "INSERT INTO readings VALUES (?, ?, ?)",
        [("Adyar", "2026-10-01", 48.0),
         ("Adyar", "2026-10-01", 52.0),
         ("Guindy", "2026-10-01", 95.0)]
    )
    print("\nCHATBOT")
    print(answer_question(con, "What is PM2.5 in Adyar today?"))
    con.close()
