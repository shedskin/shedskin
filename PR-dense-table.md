# Add opt-in open-addressing dict/set backend (`--dense-table`)

**Suggested title:** Add opt-in open-addressing dict/set backend (ankerl::unordered_dense) **Suggested branch:** `dense-table`

## Summary

Adds an alternative, opt-in hash-table backend for `dict`/`set`. The default remains the long-standing chaining `std::unordered_map`/`std::unordered_set`; passing `--dense-table` (or the `ENABLE_DENSE_TABLE` CMake option) switches the `__GC_DICT`/`__GC_SET` typedefs to an open-addressing table (`ankerl::unordered_dense`), which stores entries densely in a contiguous vector for cache-friendly iteration and bulk operations.

This addresses item 2 of the code-generation review (`REVIEW.md`, finding 3B.2): the chaining tables allocate one node per element and pointer-chase on every probe and traversal, which bounds dict/set-heavy programs regardless of what the generator emits.

## Design

- **Opt-in, not default.** The STL backend is untouched and remains the default, so existing builds are byte-for-byte unaffected. The open-addressing table is a deliberate, measured choice the user turns on.

- **Single switch, three entry points.** One `dense_table` build-config flag drives all build paths:

  - CLI: `shedskin --dense-table translate|build|run ...`

  - Makefile backend: emits `-D__SS_DENSE_TABLE`

  - CMake backend: sets the `ENABLE_DENSE_TABLE` option, which maps to the same `-D__SS_DENSE_TABLE` compile definition

  - The macro `__SS_DENSE_TABLE` can also be defined directly.

- **Guarded include.** `#include <ankerl/unordered_dense.h>` is wrapped in `#ifdef __SS_DENSE_TABLE`, so default builds never even parse the vendored header and have zero dependency on it.

- **API-compatible.** Every use of the underlying container in the runtime (`find`, `begin/end`, `erase(it)`, `operator[]`, `insert`, `reserve`, `size`, `clear`, range-for) is a strict subset of the standard associative API, so the swap is a pair of typedefs plus the vendored header — no changes to `dict.hpp`/`set.hpp` logic. The Boehm `gc_allocator` flows through to both the value-vector and bucket-vector, keeping everything GC-scanned and alive.

## Changes

**Runtime**
- `shedskin/lib/builtin.hpp` — `__GC_DICT`/`__GC_SET` select `ankerl::unordered_dense::{map,set}` under `__SS_DENSE_TABLE`, else the existing `std::unordered_{map,set}` (all four GC/NOGC branches); vendored `#include` guarded by the macro.

- `shedskin/ext/include/ankerl/unordered_dense.h` — vendored single-header `ankerl::unordered_dense` v4.5.0 (MIT). New third-party dir `shedskin/ext/include/`.

**Compiler / CLI**
- `shedskin/state/build_config.py` — new `dense_table: bool = False` field.

- `shedskin/config.py` — `dense_table` property.

- `shedskin/__init__.py` — `--dense-table` CLI flag → `gx.dense_table`.

- `shedskin/makefile.py` — adds `shedskin/ext/include` to the include path in both the direct builder and the Makefile generator; emits `-D__SS_DENSE_TABLE` when the flag is set.

- `shedskin/cmake.py` — `add_shedskin_product` gains an `enable_dense_table` keyword (emits `ENABLE_DENSE_TABLE`); `generate_cmakefile` forwards `gx.dense_table` to all three product call sites.

**CMake resources**
- `shedskin/resources/cmake/fn_add_shedskin_product.cmake`

  - `ENABLE_DENSE_TABLE` added to the function's `options`.

  - Both the executable and extension targets get `$<$<OR:$<BOOL:${SHEDSKIN_ENABLE_DENSE_TABLE}>,$<BOOL:${ENABLE_DENSE_TABLE}>>:__SS_DENSE_TABLE>`, so it responds to both the function keyword and a direct `-DENABLE_DENSE_TABLE=ON` at configure time.

  - Self-derives `SHEDSKIN_EXT_INCLUDE` from `SHEDSKIN_LIB` (its parent + `/ext/include`) so every caller — `examples/`, `tests/`, and `shedskin build`-generated projects — gets the vendored include path without each `CMakeLists.txt` having to define it.

**Benchmark**
- `tests/benchmarks/dict_set_bench.py` — synthetic benchmark over eight dict/set access patterns (build, lookup, iterate, churn, str-keyed, set build, membership, set algebra).

- `tests/benchmarks/dict-set-benchmark.md` — results and analysis.

- `tests/benchmarks/README.md` — documents the second benchmark and the old-vs-new comparison via `--dense-table`.

## Usage

```bash
# Makefile backend
shedskin translate --dense-table prog.py && make && ./prog

# CMake backend
shedskin build --dense-table prog.py        # generates add_shedskin_product(ENABLE_DENSE_TABLE ...)

# Direct CMake option (test suite / hand-written CMake projects)
cmake -DENABLE_DENSE_TABLE=ON -S . -B build
shedskin runtests --run test_type_dict -c ENABLE_DENSE_TABLE=ON
```

## Benchmark results

`tests/benchmarks/dict_set_bench.py`, N=100000, `-O2 -std=c++20`, Boehm GC, best-of-several runs (seconds). Default STL vs `--dense-table`:

| Section          | What it stresses            | STL (default) | dense (`--dense-table`) | Speedup |
|------------------|-----------------------------|---------------|-------------------------|---------|
| DICT_INT_BUILD   | int->int insert + growth    | 0.248         | 0.160                   | 1.6x    |
| DICT_INT_LOOKUP  | int point lookup, ~half miss| 0.050         | 0.091                   | 0.55x   |
| DICT_INT_ITER    | iterate all items           | 0.253         | 0.011                   | 23x     |
| DICT_INT_CHURN   | insert then pop every key   | 0.378         | 0.246                   | 1.5x    |
| DICT_STR         | str-keyed build + lookup    | 1.035         | 0.825                   | 1.3x    |
| SET_BUILD        | int set insert + dedup      | 0.292         | 0.149                   | 2.0x    |
| SET_MEMBER       | int membership, ~half miss  | 0.082         | 0.105                   | 0.78x   |
| SET_OPS          | intersection + union        | 2.605         | 0.620                   | 4.2x    |
| **TOTAL**        |                             | **4.97**      | **2.22**                | **2.2x**|

Open-addressing wins big on iteration (~23x, dense contiguous scan vs pointer chase) and set algebra (~4x), and 1.3-2x on construction/churn. It is ~1.3-1.8x *slower* on pure integer point-lookups, because `unordered_dense` applies a wyhash finalizer on top of `ss_hash` (which is `std::hash<int>`, i.e. the identity on libstdc++/libc++, and would cluster badly without mixing). We deliberately keep the mix — the absolute lookup cost is tiny and the robustness matters for sequential-integer-key programs. Net on this mixed workload: ~2.2x.

## Testing

- `make test` (unit suite): 246 passed.

- `mypy` clean on all modified Python modules.

- dict/set correctness programs pass in both executable and extension-module modes, default and `--dense-table`: `test_type_dict`, `test_type_set`, `test_mod_collections`, `test_mod_copy`, `test_mod_os`, plus dict/set-heavy programs (`dijkstra`, `soduko`, `horn`).

- All eight benchmark checksums are bit-identical between the STL and dense backends; the count-valued ones also match CPython.

- All four backend branches exercised: GC/NOGC x STL/dense.

## Backward compatibility

Default behavior is unchanged: no flag means the STL backend, the vendored header is not included, and the `-I shedskin/ext/include` entry (added unconditionally to the include path) is harmless when unused. No generated-code or API changes.

## Notes / caveats

- **Vendored dependency:** `ankerl::unordered_dense` v4.5.0, single MIT-licensed header. The v4.5.0 tag is a genuine standalone amalgamation; `main` (4.8.x) was split into a non-self-contained `stl.h` and is unsuitable for vendoring as-is.

- **Warnings:** under `-Wall -Wextra -Wconversion` the vendored header emits benign `-Wsign-conversion` notes (a `long -> uint64_t` in its hash mixing of the `ss_hash` result). It is third-party code and is left unpatched; if desired it can be silenced by including `ext/include` via `-isystem` instead of `-I`.

- **Impact is workload-dependent:** iteration/construction/set-algebra-heavy code wins substantially; lookup-bound integer-keyed code is flat-to-slightly-slower. This converts the review's analytical "High" rating into measured evidence.

## Not in this PR

- `examples/amaze/amaze.py` (a type-inference convergence fix using a `(-1, -1)` point sentinel) is unrelated to the backend and should land separately.

---

Generated with Claude Code (https://claude.com/claude-code)
