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
        s = 0
        for x in DATA:
            s += x ^ k
        total += s
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
    total = 0.0
    total += timed("SUM", bench_sum)
    print("TIME %.3f" % total)
