# B3 – Loops vs libraries vs SQL

The program generates 8,760 hourly readings per station (365 days × 24 hours). It tests 1, 12 and 120 stations. Each method calculates daily mean PM2.5 per station.

- Python loop: reads the CSV once and accumulates sum/count in a dictionary keyed by station and day.
- pandas: reads the CSV into a DataFrame and uses groupby(["station", "day"]).mean().
- SQL: loads the CSV into SQLite with executemany(), then uses GROUP BY. The reported SQL time includes CSV loading and the query, so it is an end-to-end measurement.

The program checks that the three dictionaries of results have the same keys and means before a timing row is accepted. It profiles the Python loop with cProfile for the one-station file and prints the functions with the highest cumulative time.

The running-sum alternative still takes O(n) time for n readings, but it stores only sum and count for each station/day group, O(g) space. Storing all readings before calculating means takes O(n) space. If only the final averages are required, running sums are preferable. If later analysis needs each individual reading, the original rows must also be retained.
