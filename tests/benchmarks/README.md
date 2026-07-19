# Shed Skin micro-benchmarks

Synthetic benchmarks for specific code-generation and runtime optimizations from
`REVIEW.md`. Each exists because no program in `examples/` or `tests/` drives the
relevant pattern in a hot loop, so the optimization's effect is invisible on the
regular suite.

This directory is intentionally **not** named `test_*`, so it is not picked up by
the auto-discovered correctness suite (`make test`); these are standalone
benchmarks you build and run manually.

| Benchmark            | REVIEW.md item | Measures                                   |
|----------------------|----------------|--------------------------------------------|
| `reducer_bench.py`   | 3A.1 (item 1)  | reducer/genexpr fusion into an accumulator |
| `dict_set_bench.py`  | 3B.2 (item 2)  | open-addressing dict/set backend           |

---

# Reducer/genexpr fusion benchmark

`reducer_bench.py` is a synthetic benchmark for the code-generation optimization
that fuses `sum`/`any`/`all` over a **generator expression** into a direct
accumulator loop (REVIEW.md finding 3A.1).

## Build and run (current compiler)

```bash
cd tests/benchmarks
shedskin translate reducer_bench.py   # emits reducer_bench.cpp + a Makefile
make
./reducer_bench
# SUM 0.002 CHECKSUM 1782538496
# ANY 0.013 CHECKSUM 0
# ALL 0.013 CHECKSUM 2000
# TIME 0.028
```

Each section prints its own wall-clock time and a `CHECKSUM`; the checksums must
be identical between the fused and unfused builds.

## Compare fused vs unfused

The workload is fixed; the two data points come from compiling it with and
without the fusion. From a clean checkout with the fusion applied:

```bash
# fused (current working tree)
shedskin translate reducer_bench.py && make && ./reducer_bench   # note TIME

# unfused (temporarily drop the change), then rebuild
git stash push ../../shedskin/cpp.py
shedskin translate reducer_bench.py && make && ./reducer_bench   # note TIME
git stash pop
```

The `CHECKSUM` line must be identical for both builds (correctness); the `TIME`
line is the measurement.

---

# dict/set backend benchmark

`dict_set_bench.py` measures the dict/set runtime for the alternative
open-addressing backend added in item 2 of REVIEW.md. The default `__GC_DICT` /
`__GC_SET` backend in `shedskin/lib/builtin.hpp` remains the chaining STL
hashtables; the `--dense-table` option opts into an open-addressing table
(`ankerl::unordered_dense`, vendored under `shedskin/ext/include/ankerl/`). The
benchmark drives eight dict/set access patterns -- build, lookup, iterate, churn,
membership, and set algebra -- over a runtime-populated working set.

## Build and run (current compiler)

```bash
cd tests/benchmarks
shedskin translate dict_set_bench.py   # emits dict_set_bench.cpp + a Makefile
make
./dict_set_bench
```

## Compare old (STL) vs new (open-addressing) table

Unlike the reducer benchmark, the two data points here come from a build-time
switch, not a source edit. The default chaining `std::unordered_map`/`set`
backend is used unless the `--dense-table` command-line option is given, which
opts into the open-addressing table (mapping to `-D__SS_DENSE_TABLE` for the
Makefile build and to the `ENABLE_DENSE_TABLE` CMake option for `shedskin
build`/`run`):

```bash
# default STL table
shedskin translate dict_set_bench.py && make && ./dict_set_bench       # note TIME

# open-addressing table
shedskin translate --dense-table dict_set_bench.py && make && ./dict_set_bench

# (equivalently, without re-translating: make CPPFLAGS=-D__SS_DENSE_TABLE)
```

All eight `CHECKSUM` lines must be identical between the two builds
(correctness); the `TIME` lines are the measurement. Results and analysis are
recorded in `dict-set-benchmark.md`.
