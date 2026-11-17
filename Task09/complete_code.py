"""Completed TODO 1 from Assignment 5, B4."""
POSITIVE = {"good", "clean", "fast", "helpful", "improved"}
NEGATIVE = {"bad", "dirty", "slow", "rude", "smoke", "broken"}
NEGATORS = {"not", "never", "no"}


def score(text):
    """+1 per positive word, -1 per negative word; a preceding negator flips it."""
    words = text.lower().replace(".", " ").replace(",", " ").split()
    total = 0
    previous_was_negator = False
    for word in words:
        if word in POSITIVE:
            value = 1
        elif word in NEGATIVE:
            value = -1
        else:
            value = 0

        if previous_was_negator:
            value = -value

        total += value
        previous_was_negator = word in NEGATORS

    return total


def label(text):
    value = score(text)
    return "positive" if value > 0 else "negative" if value < 0 else "neutral"


for complaint in [
    "Roads are clean and the bus was fast.",
    "Smoke from the factory, air is bad.",
    "The staff were not helpful.",
    "Not bad, service improved."
]:
    print(f"{label(complaint):8} | {complaint}")
