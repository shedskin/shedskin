# dict/set backend benchmark (REVIEW.md item 2)

Measures Shed Skin's dict/set runtime for the optional open-addressing backend
added in item 2 of REVIEW.md. The default `__GC_DICT` / `__GC_SET` backend in
`shedskin/lib/builtin.hpp` remains the chaining STL hashtables
(`std::unordered_map` / `std::unordered_set`); the `--dense-table` option opts
into an open-addressing table (`ankerl::unordered_dense` 4.5.0, vendored at
`shedskin/ext/include/ankerl/`).

Workload: `dict_set_bench.py` in this directory. Both builds run identical code
over a runtime-populated working set of `N = 100000` keys; the multipliers keep
key generation inside a signed 32-bit int so the two builds -- and CPython --
see the exact same keys. The count-valued CHECKSUM lines (`BUILD`, `STR`,
`SET_*`) therefore match CPython exactly; the additive-sum lines wrap identically
in both Shed Skin builds (32-bit `__ss_int`), so all eight CHECKSUMs are
bit-identical between the old and new table -- correctness holds.

## How it was measured

```bash
cd tests/benchmarks

# default STL table
shedskin translate dict_set_bench.py && make && ./dict_set_bench

# open-addressing table (via the --dense-table command-line option)
shedskin translate --dense-table dict_set_bench.py && make && ./dict_set_bench
```

Apple M-series, `-O2 -std=c++20`, Boehm GC, best of several runs (seconds).

## Results

| Section          | What it stresses                         | OLD (STL) | NEW (dense) | Speedup |
|------------------|------------------------------------------|-----------|-------------|---------|
| DICT_INT_BUILD   | int->int insert + table growth           | 0.248     | 0.160       | 1.6x    |
| DICT_INT_LOOKUP  | int point lookup, ~half misses           | 0.050     | 0.091       | **0.55x** |
| DICT_INT_ITER    | iterate all items                        | 0.253     | 0.011       | **23x** |
| DICT_INT_CHURN   | insert then pop every key                | 0.378     | 0.246       | 1.5x    |
| DICT_STR         | str-keyed build + lookup (object hash/eq)| 1.035     | 0.825       | 1.3x    |
| SET_BUILD        | int set insert + dedup                   | 0.292     | 0.149       | 2.0x    |
| SET_MEMBER       | int membership, ~half misses             | 0.082     | 0.105       | **0.78x** |
| SET_OPS          | intersection + union                     | 2.605     | 0.620       | **4.2x** |
| **TOTAL**        |                                          | **4.97**  | **2.22**    | **2.2x**|

## Reading the result

The open-addressing table is a large, structural win where the review predicted
it -- anything that traverses or bulk-processes the container:

- **Iteration is ~23x faster.** `unordered_dense` stores entries densely in a
  contiguous vector, so a full scan is a linear cache-friendly walk that the
  compiler can vectorize; the chaining table pointer-chases one heap node per
  element. This is the single biggest structural difference and it dominates any
  iteration-heavy program.
- **Set algebra is ~4x, bulk build/dedup ~1.6-2x.** Same cause: contiguous
  storage and one amortized allocation growth instead of per-element node
  allocation.

The cost shows up in **pure point lookups on integer keys**, which are ~1.3-1.8x
*slower*. `unordered_dense` applies an extra hash-mixing step (wyhash finalizer)
on top of `ss_hash`, because it must not assume the incoming hash is well
distributed -- `ss_hash<int>` is `std::hash<int>`, i.e. the identity on
libstdc++/libc++, which would cluster badly in an open-addressing table without
mixing. For a lookup where the base hash is nearly free, that mix is pure
overhead. We deliberately keep the mix (do **not** mark `ss_hash` avalanching):
it is what makes the table robust for the sequential-integer-key case that real
programs hit, and the absolute cost is tiny (~0.09s for 24M lookups).

Net on this deliberately mixed workload: **~2.2x**. The real-world figure is
workload-dependent -- iteration/construction/set-op-heavy code wins big,
lookup-bound integer-keyed code is roughly flat-to-slightly-slower. This matches
the review's own caveat that the impact rating was analytical and needed
measurement; the swap is a clear win in aggregate and an unambiguous one for the
iteration and set-algebra patterns, with the honest caveat noted above.
