# CSA08-192365059-Assignment5

**Assignment:** Data Acquisition, Cleaning, Analysis and AI Applications (CO5)  
**Student:** Karthikeyan S  
**Register Number:** 192365059  
**Platform:** Windows 10  
**Python:** 3.11.6 (`python`)  

Repository: https://github.com/Karthikdj2028/CSA08-192365059-Assignment5

## Python libraries

Standard library: `csv`, `sqlite3`, `statistics`, `time`, `timeit`, `cProfile`, `logging`, `random`, `collections`, `pathlib`.

Third-party libraries used for the required charts and DataFrame comparison:
- pandas
- matplotlib

Install them from the repository root:

```powershell
python -m pip install -r requirements.txt
```

## Task map and run commands

This repository uses Task01–Task09 for the five Part A design tasks and four Part B implementation tasks.

| Folder | Assignment section | Run command | Main result |
|---|---|---|---|
| Task01 | A1 – Data Acquisition Design | Read `analysis.md` and `schema.sql` | CSV source model, SQLite tables, SQL examples and CSV-vs-SQL analysis. |
| Task02 | A2 – Cleaning and Normalisation Design | `python Task02/cleaning_demo.py` | Cleaning rules, Fahrenheit conversion, min-max and z-score examples. |
| Task03 | A3 – Analysis and Visualisation Design | `python Task03/summary_demo.py` | Summary statistics and SQL GROUP BY example; chart choices in analysis. |
| Task04 | A4 – Debugging and Profiling Plan | `python Task04/debug_profile.py` | Assertions, logging, perf_counter, timeit and cProfile demonstration. |
| Task05 | A5 – Citizen Complaint AI Design | `python Task05/citizen_ai.py` | Lexicon sentiment with negation, extractive summary and rule-based chatbot. |
| Task06 | B1 – Cleaning Pipeline | `python Task06/clean_pipeline.py` | Cleaned CSV, SQLite database, SQL summaries and four matplotlib charts. |
| Task07 | B2 – Adversarial Data | `python Task07/adversarial_tests.py` | Missing-column, delimiter, encoding and empty-file tests; parameterised SQL. |
| Task08 | B3 – Loops vs Libraries vs SQL | `python Task08/compare_methods.py` | Correctness check, timing at 1/12/120 stations and cProfile-ready script. |
| Task09 | B4 – Final Engineering Decision | `python Task09/final_decision.py` | 50-complaint sentiment check, summary, SQLite index timing and production recommendation. |

## Important notes

- Run commands from the repository root.
- Task06 creates a small raw CSV sample in `Task06/data/`, cleans it, creates `Task06/air_quality.db`, writes `Task06/output/cleaned_readings.csv`, and saves charts under `Task06/charts/`.
- Task08 generates synthetic hourly readings (8,760 per station) for 1, 12 and 120 stations. The 120-station case contains about 1.05 million rows and may take longer on a lower-memory computer.
- Task09 uses 50 labelled sample complaints. Its agreement count is a manual comparison against the labels recorded in the script; review those labels and record your own judgement.
- Timings depend on your computer. Use the output produced by your own Windows run in the report. Never copy sample timing values as if they were measured on your device.
- Capture genuine terminal screenshots in each task's `evidence/` folder after execution.

## GitHub workflow

Commit Task01 through Task09 separately after execution and evidence capture. Example:

```powershell
git add Task01
git commit -m "docs(task01): design air-quality data acquisition"
git push origin main
```

Repeat for each task folder.
