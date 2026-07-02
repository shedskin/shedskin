# Reducer/genexpr fusion benchmark

`reducer_bench.py` is a synthetic benchmark for the code-generation optimization
that fuses `sum`/`any`/`all` over a **generator expression** into a direct
accumulator loop (REVIEW.md finding 3A.1). It exists because no program in
`examples/` or `tests/` drives that pattern in a hot loop, so the optimization's
effect is invisible on the regular suite.

This directory is intentionally **not** named `test_*`, so it is not picked up by
the auto-discovered correctness suite (`make test`); it is a standalone
benchmark you build and run manually.

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
line is the measurement. Results are recorded in `../../reducer-benchmark.md`.
