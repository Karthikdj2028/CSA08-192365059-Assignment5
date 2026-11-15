# A4 – Debugging and profiling plan

## Debugging tools

- print(): temporarily display the raw value, its type and the cleaned value for one known row.
- assert: verify facts that must always be true, for example that no cleaned PM2.5 value is negative.
- logging: use DEBUG for detailed row information, INFO for successful stages and WARNING for rejected records. Logging levels can be changed without deleting statements.
- pdb or IDE debugger: set a breakpoint inside the cleaning function, inspect the current row, step over conversion and examine the call stack. Remove or disable the breakpoint after the fault is found.

The included debug_profile.py demonstrates assertions and logging. It profiles a small repeatable workload.

## Profiling tools

- time.perf_counter(): measures elapsed wall-clock time around one pipeline stage.
- timeit: repeats a small operation to reduce timing noise.
- cProfile: records the number of calls and time spent in each function. Sort by cumulative time to find the slowest function.

## Alternative: print every row

Printing every row can slow the program because console output is expensive, especially for thousands of records. Logging has levels; set the level to WARNING or ERROR in production to disable DEBUG and INFO output. A debugger is used only during investigation and can be detached without changing the data-processing code. Timing and memory should be measured with representative input, not one tiny row.
