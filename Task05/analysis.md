# A5 – AI application for citizen complaints

## Sentiment scorer

Use a small positive word set (good, clean, fast, helpful, improved), a negative word set (bad, dirty, slow, rude, smoke, broken), and negators (not, never, no). Tokenise text into lowercase words. A positive word adds 1, a negative word subtracts 1, and a preceding negator reverses the next word's score. A positive total is positive, a negative total is negative, and zero is neutral.

This is a rule-based baseline. It can fail on sarcasm ("great, another smog day"), double negatives, local language, spelling mistakes and context.

## Extractive summariser

Split a complaint into sentences, remove common stop words, count important words, score each sentence by the frequency of its important words, and choose the highest-scoring sentences. Keep the chosen sentences in original order. This selects existing text; it does not generate new facts.

## Basic chatbot

The chatbot detects a station name from a small list of known stations. It queries the latest day and average PM2.5 using parameterised SQL. A real version should also ask for a date when "today" is ambiguous and return a helpful response if no data is available.

Limitations: keyword matching cannot understand spelling variations or complex questions; it only knows stations stored in the database; lexicon sentiment may misunderstand sarcasm and negation scope.

## Alternative: trained model

A Naive Bayes classifier needs labelled complaints and feature counts; prediction is usually fast and its memory is related to the vocabulary/features. A pre-trained language model can understand more context but needs much more memory and compute, and may be slower per complaint. A trained model may improve accuracy if its training data represents local language and common complaint styles. Accuracy must be measured on a labelled test set rather than assumed.
