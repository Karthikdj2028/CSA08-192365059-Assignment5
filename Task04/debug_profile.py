"""Small example of assertions, logging, timing and profiling."""
import cProfile
import logging
import pstats
import time
import timeit

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def clean_values(values):
    result = []
    for value in values:
        if value is None:
            continue
        if 0 <= value <= 999:
            result.append(value)
    return result


def workload():
    values = [i % 1100 for i in range(10000)]
    cleaned = clean_values(values)
    assert all(0 <= item <= 999 for item in cleaned)
    return sum(cleaned)


if __name__ == "__main__":
    sample = [10, 20, None, -1, 1001, 30]
    print("Debug sample:", clean_values(sample))
    assert clean_values(sample) == [10, 20, 30]
    logging.info("Cleaning assertion passed")

    start = time.perf_counter()
    answer = workload()
    elapsed = time.perf_counter() - start
    print("Workload result:", answer)
    print("perf_counter seconds:", round(elapsed, 6))

    small_time = timeit.timeit("sum(range(1000))", number=1000)
    print("timeit 1,000 repetitions:", round(small_time, 6), "seconds")

    profiler = cProfile.Profile()
    profiler.enable()
    workload()
    profiler.disable()
    print("\nTop functions from cProfile:")
    pstats.Stats(profiler).sort_stats("cumulative").print_stats(5)
