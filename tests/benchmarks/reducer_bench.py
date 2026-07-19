"""Synthetic benchmark for reducer/genexpr fusion (REVIEW.md finding 3A.1).

Each timed section drives one of the fusible builtins -- sum / any / all / min /
max -- over a generator expression inside a hot loop. This is the pattern that
Shed Skin lowers to a `static inline` accumulator when the fusion optimization is
enabled, and to a heap-allocated iterator class with a virtual `__get_next()` per
element otherwise.

Each reducer iterates over a runtime-populated list (`DATA`) and mixes in the
outer loop variable `k`, so the reducer is neither loop-invariant nor a
closed-form series: the C++ optimizer cannot hoist, constant-fold, or eliminate
it. This measures real per-element iteration + dispatch cost, keeping the
fused-vs-unfused comparison fair and representative.

Run standalone (prints a checksum for correctness and a wall-clock TIME):

    shedskin translate reducer_bench.py && make && ./reducer_bench

To compare fused vs unfused, build once with the current compiler and once with
the fusion removed, then diff the TIME lines (see tests/benchmarks/README.md).
"""

import time

SUM_REPS = 2000
ANY_REPS = 2000
ALL_REPS = 2000
MIN_REPS = 2000
MAX_REPS = 2000
N = 20000

# runtime-populated data: the optimizer cannot see through the GC-allocated list,
# so every reduction below must actually iterate it (no closed-form collapse).
DATA = [(i * 2654435761) % 1000 for i in range(N)]


def bench_sum():
    """sum(<genexpr>) in a hot loop -- accumulator fold over runtime data."""
    total = 0
    for k in range(SUM_REPS):
        total += sum(x ^ k for x in DATA)
    return total


def bench_any():
    """any(<genexpr>) in a hot loop -- condition never true, so full scan."""
    hits = 0
    for k in range(ANY_REPS):
        # DATA values are all < 1000, so this is always False -> full scan
        if any(x > 1000000 + k for x in DATA):
            hits += 1
    return hits


def bench_all():
    """all(<genexpr>) in a hot loop -- condition always true, so full scan."""
    hits = 0
    for k in range(ALL_REPS):
        if all(x < 1000000 + k for x in DATA):
            hits += 1
    return hits


def bench_min():
    """min(<genexpr>) in a hot loop -- full scan, first-element fold."""
    total = 0
    for k in range(MIN_REPS):
        total += min(x ^ k for x in DATA)
    return total


def bench_max():
    """max(<genexpr>) in a hot loop -- full scan, first-element fold."""
    total = 0
    for k in range(MAX_REPS):
        total += max(x ^ k for x in DATA)
    return total


def timed(label, fn):
    t0 = time.time()
    r = fn()
    dt = time.time() - t0
    print("%s %.3f CHECKSUM %d" % (label, dt, r))
    return dt


if __name__ == "__main__":
    # warmup (fill caches, let the branch predictor settle)
    bench_sum()
    bench_any()
    bench_all()
    bench_min()
    bench_max()
    total = 0.0
    total += timed("SUM", bench_sum)
    total += timed("ANY", bench_any)
    total += timed("ALL", bench_all)
    total += timed("MIN", bench_min)
    total += timed("MAX", bench_max)
    print("TIME %.3f" % total)
