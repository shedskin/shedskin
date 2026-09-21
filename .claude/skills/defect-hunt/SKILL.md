---
name: defect-hunt
description: Hunt for latent defects in shedskin by differential-testing translated C++ against CPython, and file the findings as a GitHub issue. Use for the weekly defect report, or when asked to go looking for bugs in a particular area (a library module, a language feature, the type inferencer).
---

# Defect hunt

Find *real, reproducible* shedskin defects and report them so they can be fixed
without further investigation. A short report of confirmed bugs beats a long
report of suspicions.

## Setup

```bash
./.claude/setup.sh      # installs libgc/pcre, pip install -e .
```

Always work from the latest `main` unless told otherwise:

```bash
git fetch origin main && git checkout -B <branch> origin/main
```

## The core loop: differential testing

This is where almost every confirmed defect comes from. A test program is a
self-contained `.py` file that prints its results; shedskin's own test suite
uses `assert`, but **printing is better for hunting** — an assert only tells you
something broke, printed output tells you exactly how the two runtimes diverge.

```bash
cd "$SCRATCH/probe"
python3 probe.py > cpython.txt 2>&1          # reference behaviour
shedskin translate probe.py && make          # translate + compile
./probe > shedskin.txt 2>&1
diff cpython.txt shedskin.txt                # a difference is a candidate defect
```

Four distinct failure modes, all worth reporting:

1. **Wrong output** — compiles and runs, disagrees with CPython.
2. **Compile error** — shedskin emits C++ that g++ rejects.
3. **Translate error/crash** — shedskin itself raises, or reports a bogus error
   on valid Python.
4. **Runtime crash** — the binary segfaults or aborts.

Keep each probe small and single-purpose. When a big probe diverges, bisect it
down to the smallest program that still reproduces before reporting.

## Rules of engagement

- **Never run the whole test suite.** It takes about an hour. Use
  `shedskin translate` on individual probes, or at most a few related test sets
  via `shedskin runtests --include <regex>`.
- **Ignore empty-list/empty-container inference issues.** Known weak spot,
  deliberately out of scope.
- The `tests/skip_*` directories are known-unsupported; don't report those.
- Check `tests/errs/` — those are expected-error cases, not defects.
- Before reporting, search existing issues for a duplicate.

## Where to look

Rotate the focus each week rather than re-treading the same ground; say in the
report which area was covered so the next run can pick a different one.

- **Library modules** — `shedskin/lib/*.py` and their `.cpp`/`.hpp`
  implementations. The `.py` file is a type-inference stub; the `.cpp` is the
  real behaviour, and the two drifting apart is a rich source of bugs. Compare
  each against CPython's documented semantics: negative and out-of-range
  indices, empty and single-element inputs, default arguments, keyword
  arguments, unicode vs bytes, exception type and message, float formatting and
  rounding, integer overflow at 32/64-bit boundaries.
- **Builtins** — `shedskin/lib/builtin/*.hpp`. String methods, `sorted`/`sort`
  stability and `key=`, `format`/f-string specifiers, `dict`/`set` ordering
  guarantees, slicing with negative steps, `int`/`float` conversion edges.
- **Language features** — comprehensions and generators, nested and recursive
  functions, closures, default mutable arguments, `*args`/`**kwargs`,
  inheritance and `super()`, operator overloading and reflected operators,
  context managers, exception chaining and `finally` interactions.
- **Type inference** — `shedskin/infer.py`, `graph.py`, `typestr.py`. Union
  types flowing through containers, polymorphic call sites, recursive data
  structures.
- **Code generation** — `shedskin/cpp.py`. Operator precedence in emitted
  expressions, name mangling and shadowing, temporaries and evaluation order.
- **Recent commits** — `git log --since="8 weeks ago"` points at code that is
  newly changed and least exercised.

## Cross-checking flags

Behaviour that differs only under a flag is a defect too. When a probe passes
cleanly, it is cheap to re-run it under `--int32`, `--int64`, `--nogc`, or
`-b` (bounds checking) and diff again.

## Reading the source for defects

Differential testing finds what you thought to probe. Reading finds the rest.
Worthwhile patterns in the generated-code and library layers: missing bounds or
null checks, `int` vs `__ss_int` confusion, signed/unsigned comparisons,
off-by-one in slice arithmetic, reference cycles the GC cannot collect,
exception paths that leak or skip cleanup, and `.py` stubs whose signature no
longer matches the `.cpp`.

A code-reading finding is only worth reporting once a probe confirms it. If you
cannot make it reproduce, leave it out — or state plainly that it is unconfirmed
and say what you tried.

## Going wide

A thorough hunt is many independent probes, and probes do not depend on each
other. Fan out with subagents — one per focus area — each building and running
its own probes in its own scratch directory, then collect and confirm their
findings yourself before writing the report. Re-run every candidate defect
yourself before it goes in the issue.

## The report

File one GitHub issue per run against `shedskin/shedskin`, titled
`Weekly defect report — <date>`. Structure it as:

- **Summary** — how many confirmed defects, which areas were covered, and how
  long the run took.
- **Confirmed defects** — one section each, ordered by severity. Every one needs
  a minimal reproducing `.py`, the CPython output, the shedskin output (or the
  translate/compile/runtime error), and a one-line note on the suspected cause
  with a `file:line` pointer where you have one.
- **Unconfirmed suspicions** — only if genuinely worth a look; say what you tried
  and why it did not reproduce.
- **Areas checked, nothing found** — so the next run can skip them.

If a run finds nothing, file the issue anyway and say so. A clean week is a
useful signal, and the "areas checked" list still compounds.

Do not open pull requests with fixes unless asked — the report is the
deliverable.
