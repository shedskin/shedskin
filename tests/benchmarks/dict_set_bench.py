"""Synthetic benchmark for the dict/set hash-table backend (REVIEW.md finding 3B.2).

Each timed section drives one dict or set access pattern -- build, lookup,
iterate, insert/delete churn, membership, and set algebra -- over a
runtime-populated working set. This is the code that Shed Skin lowers onto the
`__GC_DICT` / `__GC_SET` typedefs in `shedskin/lib/builtin.hpp`, which item 2 of
REVIEW.md swaps from chaining hashtables (`std::unordered_map` /
`std::unordered_set`) to an open-addressing table (`ankerl::unordered_dense`).

The keys come from a runtime-populated list (`KEYS` / `STR_KEYS`), so the C++
optimizer cannot see through the GC-allocated storage: every insert, probe, and
iteration below must actually touch the table. Both int keys (the unboxed,
scalar-hash fast path) and str keys (the object `__hash__`/`__eq__` path) are
exercised, since the two stress the table differently.

The iteration and build sections are where an open-addressing table is expected
to win most: `unordered_dense` stores entries densely in a contiguous vector
(cache-friendly linear scan, one allocation growth) where a chaining table
allocates one node per element and pointer-chases on every probe and traversal.

Run standalone (prints a checksum for correctness and a wall-clock TIME):

    shedskin translate dict_set_bench.py && make && ./dict_set_bench

To compare the new table against the old one, build once with the current tree
and once with the `builtin.hpp` typedef swap reverted; the CHECKSUM lines must be
identical and the TIME lines are the measurement (see README.md).
"""

import time

# working-set size and per-section repetition counts, tuned so each section does
# real, measurable work without exhausting memory under the GC.
N = 100000
BUILD_REPS = 120
LOOKUP_REPS = 120
ITER_REPS = 1000
CHURN_REPS = 120
SET_BUILD_REPS = 120
SET_MEMBER_REPS = 120
SET_OPS_REPS = 200

# runtime-populated key data: multiplicative hashing spreads the keys over a
# range ~4x the set size, giving a realistic load factor and a mix of
# lookup hits and misses. The optimizer cannot fold these away. The multipliers
# are chosen so `i * mult` stays inside a signed 32-bit int for i < N (Shed
# Skin's default __ss_int width), keeping the key set identical to CPython's and
# the tables at their full intended size of N distinct keys.
KEYS = [(i * 20011) % (N * 4) for i in range(N)]
STR_KEYS = [str((i * 19997) % (N * 4)) for i in range(N)]


def bench_dict_int_build():
    """Build a fresh int->int dict every rep: insert + growth/rehash cost."""
    total = 0
    for _ in range(BUILD_REPS):
        d = {}
        for k in KEYS:
            d[k] = k ^ 0x5a5a
        total += len(d)
    return total


def bench_dict_int_lookup():
    """Probe a fixed int->int dict: ~half hits (k), ~half misses (k+1)."""
    d = {}
    for k in KEYS:
        d[k] = k ^ 0x5a5a
    total = 0
    for _ in range(LOOKUP_REPS):
        for k in KEYS:
            total += d.get(k, 0)
            total += d.get(k + 1, 0)
    return total


def bench_dict_int_iter():
    """Iterate items of a fixed int->int dict: dense-scan vs pointer-chase."""
    d = {}
    for k in KEYS:
        d[k] = k ^ 0x5a5a
    total = 0
    for _ in range(ITER_REPS):
        for k, v in d.items():
            total += k ^ v
    return total


def bench_dict_int_churn():
    """Insert then pop every key: exercises erase / backward-shift deletion."""
    total = 0
    for _ in range(CHURN_REPS):
        d = {}
        for k in KEYS:
            d[k] = k
        for k in KEYS:
            total += d.pop(k, 0)
    return total


def bench_dict_str():
    """Build + probe a str-keyed dict: the object __hash__/__eq__ path."""
    total = 0
    for _ in range(BUILD_REPS):
        d = {}
        for s in STR_KEYS:
            d[s] = len(s)
        for s in STR_KEYS:
            total += d.get(s, 0)
    return total


def bench_set_build():
    """Build a fresh int set every rep: insert + dedup + growth cost."""
    total = 0
    for _ in range(SET_BUILD_REPS):
        s = set()
        for k in KEYS:
            s.add(k)
        total += len(s)
    return total


def bench_set_membership():
    """Membership on a fixed int set: ~half hits (k), ~half misses (k+1)."""
    s = set()
    for k in KEYS:
        s.add(k)
    total = 0
    for _ in range(SET_MEMBER_REPS):
        for k in KEYS:
            if k in s:
                total += 1
            if (k + 1) in s:
                total += 1
    return total


def bench_set_ops():
    """Intersection and union of two fixed int sets: bulk build + scan."""
    a = set()
    b = set()
    for k in KEYS:
        a.add(k)
        b.add(k ^ 0x0f0f)
    total = 0
    for _ in range(SET_OPS_REPS):
        total += len(a & b)
        total += len(a | b)
    return total


def timed(label, fn):
    t0 = time.time()
    r = fn()
    dt = time.time() - t0
    print("%s %.3f CHECKSUM %d" % (label, dt, r))
    return dt


if __name__ == "__main__":
    # warmup (fill caches, let the allocator/branch predictor settle)
    bench_dict_int_build()
    bench_set_build()
    total = 0.0
    total += timed("DICT_INT_BUILD ", bench_dict_int_build)
    total += timed("DICT_INT_LOOKUP", bench_dict_int_lookup)
    total += timed("DICT_INT_ITER  ", bench_dict_int_iter)
    total += timed("DICT_INT_CHURN ", bench_dict_int_churn)
    total += timed("DICT_STR       ", bench_dict_str)
    total += timed("SET_BUILD      ", bench_set_build)
    total += timed("SET_MEMBER     ", bench_set_membership)
    total += timed("SET_OPS        ", bench_set_ops)
    print("TIME %.3f" % total)
