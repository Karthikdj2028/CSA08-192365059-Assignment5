# B4 – Final engineering decision

## B4.1 Sentiment and summary

final_decision.py contains 50 manually labelled complaint examples. It compares the lexicon sentiment label with the expected label assigned by reading each sentence and prints the agreement count. Review any disagreement: the word-list scorer is a baseline and may not understand context, sarcasm, mixed opinion or a negation that applies to more than one word.

The frequency-based extractive summary selects sentences containing the most frequent important words. The alternative first-k method is fast and predictable but may miss the main repeated issue if it appears later in the complaint collection. Compare the two outputs on the 50 examples and record which contains the repeated themes more clearly.

## B4.2 Database index

The program creates 100,000 sample readings, repeats a station/day average query 300 times before and after creating an index on (station, day), and verifies that the answers match. Record the timings from your own computer. The index uses additional disk/memory space but can reduce the number of rows SQLite must scan for a selective query.

## B4.3 Production decision

With 12 existing stations plus 100 new stations, there would be 112 stations. At one reading every 15 minutes, each station sends 96 readings per day. That is 10,752 readings per day and about 3.92 million readings per year. Store cleaned readings in SQLite for a small single-writer deployment, with a composite primary key and indexes on station/day. For multiple concurrent writers, central dashboards and higher availability, plan a managed server database such as PostgreSQL.

Keep raw CSV files as immutable source evidence. Validate and normalise before batch insertion. Use SQL for daily/monthly aggregation and pandas for offline analysis. Keep charts and profiling outputs as reproducible artifacts.

For 50,000 complaints per month, the simple lexicon is useful for a transparent first-pass label but not sufficient for final public-safety decisions. It should route uncertain or mixed complaints for human review. A trained classifier should be evaluated on a local labelled test set; a language model offers better context but requires more compute, memory and privacy controls. The final decision must use the agreement and index measurements printed by the program.
