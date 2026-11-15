# B2 – Engineer adversarial data

The test program constructs four difficult input files:
- Missing column: header omits pm25; rejected by the header check.
- Wrong delimiter: semicolons are used; DictReader cannot find the required field names.
- Different encoding: UTF-16 bytes are read as UTF-8; UnicodeDecodeError is caught.
- Empty file: no header exists; the header validation rejects it.

The SQL injection example uses the station string Adyar' OR '1'='1. String concatenation changes the SQL condition and can return all rows. A ? placeholder treats the entire value as data and finds zero matching station names.

The sentiment edge cases include a negated positive phrase, a negated negative phrase, sarcasm and double negation. A small word list cannot reliably understand sarcasm or the full scope of multiple negators.

executemany() sends many rows through one batch call. Calling execute() in a Python loop repeatedly crosses the Python/SQLite boundary. Both insert n rows in O(n) time, but executemany generally has lower call overhead. The measured result depends on Python, SQLite, disk and row size.
