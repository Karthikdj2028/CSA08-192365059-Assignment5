"""Build daily summary values for a small air-quality example."""
from collections import defaultdict
from statistics import mean

rows = [
    ("Adyar", "2026-10-01", 48.0),
    ("Adyar", "2026-10-01", 52.0),
    ("Adyar", "2026-10-02", 60.0),
    ("Guindy", "2026-10-01", 95.0),
    ("Guindy", "2026-10-02", 80.0),
    ("Guindy", "2026-10-02", 90.0),
]

groups = defaultdict(list)
for station, day, pm25 in rows:
    groups[(station, day)].append(pm25)

print("STATION | DATE | MIN | MAX | MEAN | VALID COUNT")
for (station, day), values in sorted(groups.items()):
    print(station, day, min(values), max(values),
          round(mean(values), 2), len(values))
