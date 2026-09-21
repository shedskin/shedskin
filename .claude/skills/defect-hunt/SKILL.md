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

The checkout is shallow. shedskin lands well over two hundred commits in eight
weeks, so the default depth does not reach back far enough for the "recent
commits" area below — deepen it with a bounded fetch before relying on history:

```bash
git fetch --depth=1000 origin main
```

Probes go in a scratch directory **outside the repo**, so nothing you generate
is mistaken for a change to shedskin itself. Use this session's scratchpad
directory if it has one, otherwise:

```bash
SCRATCH=$(mktemp -d)
```

## The core loop: differential testing

This is where almost every confirmed defect comes from. A test program is a
self-contained `.py` file that prints its results; shedskin's own test suite
uses `assert`, but **printing is better for hunting** — an assert only tells you
something broke, printed output tells you exactly how the two runtimes diverge.

```bash
mkdir -p "$SCRATCH/probe" && cd "$SCRATCH/probe"   # one dir per probe
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
- Make sure to understand the Shedskin limitations as described in the
  documentation.
- Not mentioned in the documentation perhaps: evaluation order in C++ may be
  different from that in CPython.
- Before reporting, search existing open issues for a duplicate/very similar
  issue. Only report new or substantially different issues.
- One exception to "open": if a probe reproduces something an issue was
  **closed as fixed** for, that is a regression, not a duplicate. Report it,
  cite the issue, and name the commit that closed it if you can find one.

## Budget

There is no token or spend cap available to a session, so the budget is whatever
this file says it is. These numbers are the dial — raise or lower them here.

- **Target about 3 hours of wall clock.** Note the time when you start.
- **At most 3 focus areas per run**, and **at most 6 subagents in flight** at
  once. Fan-out is the dominant cost: every subagent carries its own context, so
  doubling the areas roughly doubles the run.
- **At most ~12 probes per area.** Probes are cheap individually; it is the
  unbounded ones that run away. When an area keeps yielding, note it in the
  report as worth revisiting rather than chasing it to exhaustion.
- **Stop probing once your own context passes roughly 60%** and spend the rest
  on confirming candidates and writing the report. A thorough hunt with no
  report written is a wasted run.

Stopping early because the budget is spent is a correct outcome, not a failure —
say so in the report and name what was left unexplored.

## Where to look

Rotate the focus each week rather than re-treading the same ground; say in the
report which area was covered so the next run can pick a different one.

- **Library modules** — `shedskin/lib/*.py` and their `.cpp`/`.hpp`
  implementations. The `.py` file is a type-inference stub; the `.cpp` is the
  real behaviour, and the two drifting apart is a rich source of bugs. Compare
  each against CPython's documented semantics: negative and out-of-range
  indices, empty and single-element inputs, default arguments, keyword
  arguments, unicode vs bytes, exception type and message, float formatting and
  rounding, integer overflow at 32/64-bit boundaries, etc.
- **Builtins** — `shedskin/lib/builtin/*.hpp`. String methods, `sorted`/`sort`
  stability and `key=`, `format`/f-string specifiers, `dict`/`set` ordering
  guarantees, slicing with negative steps, `int`/`float` conversion edges, etc.
- **Language features** — comprehensions and generators, nested and recursive
  functions, closures, default mutable arguments, `*args`/`**kwargs`,
  inheritance and `super()`, operator overloading and reflected operators,
  context managers, exception chaining and `finally` interactions, etc.
- **Type inference** — `shedskin/infer.py`, `graph.py`, `typestr.py`. Union
  types flowing through containers, polymorphic call sites, recursive data
  structures, etc.
- **Code generation** — `shedskin/cpp.py`. Operator precedence in emitted
  expressions, name mangling and shadowing, temporaries and evaluation order, etc.
- **Memory safety** - check that GC is working as intended, that there are
  no memory leaks/premature deallocations, that extmod refcounting works as
  intended, that it works well with linked-in shared libs and so on, etc.
- **Recent commits** — `git log --since="8 weeks ago"` points at code that is
  newly changed and least exercised. Often there are similar fixes possible
  by generalizing the issue/recent commits, etc.

## The other half: extension modules

The loop above covers `shedskin translate` to an executable. shedskin also
translates to a CPython extension module (`-e`), CI tests both, and nothing in
this file probes it — so that surface is where undisturbed bugs are most likely
to be sitting.

```bash
shedskin translate -e mymod.py && make      # produces mymod.so
python3 -c "import mymod; print(mymod.f(10))"
```

**The gotcha that will cost you an hour if you do not know it:** shedskin only
generates a binding for a function whose argument types it could infer, so a
module with no calls in it exports nothing and `import` gives you an
`AttributeError`. Seed the types with a main block:

```python
def addup(n):
    return sum(range(n))

if __name__ == '__main__':
    print(addup(10))       # seeds inference; without this, no binding
```

Extension modules make a *better* differential harness than executables: import
the module and compare its functions against a pure-Python reference in the same
process, over many inputs, instead of diffing stdout once. Disagreement between
the same function called as an extension module and as an executable is itself a
defect worth reporting.

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

## Probing memory safety

Stdout diffing cannot see a leak or a premature free, so the memory-safety area
needs its own tooling — and the obvious approach is a trap worth knowing about
before you spend a subagent on it.

**Do not run valgrind against a normal build.** Boehm GC scans memory
conservatively by design, so valgrind reports hundreds of uninitialised-read
errors on a test that passes perfectly — 343 errors from 8 contexts on a small
passing test, none of them bugs. A subagent that does not know this will report
the noise.

Build with `--nogc` instead, which takes the collector out of the picture and
leaves valgrind's error summary meaningful:

```bash
shedskin translate --nogc probe.py && make
valgrind ./probe                    # same probe, GC build: 343 errors
                                    #              --nogc build: 0 errors
```

Read that run for **invalid accesses** — use-after-free, out-of-bounds, bad
reads — not for leak counts: with `--nogc` nothing is ever freed, so the leak
numbers mean nothing. `-fsanitize=address` on the generated `.cpp` is the other
option where valgrind is too slow.

This leaves one real blind spot, and it is worth saying out loud rather than
pretending otherwise: bugs *in* GC behaviour — a premature collection, an object
the collector never reclaims — only manifest in the GC build, where valgrind is
useless. Those need a probe that allocates hard in a loop and watches RSS, or a
reproducible wrong answer caused by an object collected too early. If you cannot
get either, say so rather than reporting valgrind noise as a finding.

## Going wide

A thorough hunt is many independent probes, and probes do not depend on each
other. Fan out with subagents — one per focus area — each building and running
its own probes in its own scratch directory, then collect and confirm their
findings yourself before writing the report. Re-run every candidate defect
yourself before it goes in the issue.

## The report

Write the report once, then deliver it three ways. Do all three — they fail
independently, and between them one always gets through.

**1. A file in the repo.** Write the report to
`reports/defect-hunt/<YYYY-MM-DD>.md` and commit it to your working branch.
This is what makes the reports an archive rather than a stream of emails: they
accumulate, they diff against each other, and next week's run can read last
week's instead of relying on the issue tracker. Commit it even if you cannot
push — the file still shows in the session's diff, where it can be read and
downloaded, and it is ready to push the moment access allows.

**2. A GitHub issue** against `shedskin/shedskin`, titled
`Weekly defect report — <date>`. If filing fails with a 403, the Claude GitHub
App is not installed on the shedskin org. Do not retry it or look for a way
around it. Note it in one line at the top of the report and carry on — reading
the tracker still works, so duplicate-checking is unaffected.

**3. Your final message**, which is what reaches the maintainer by email. This
one is not optional and it must be genuinely last: the turn ending is what
sends the mail, so anything you do afterwards means the mail arrived before the
work stopped. Write the file and file the issue *first*, then end the turn with
the full report.

Structure it the same way in all three:

- **Run cost** — wall clock, tokens and dollars, and the fan-out used (see
  below).
- **Summary** — how many confirmed defects and which areas were covered.
- **Confirmed defects** — one section each, ordered by severity. Every one needs
  a minimal reproducing `.py`, the CPython output, the shedskin output (or the
  translate/compile/runtime error), and a one-line note on the suspected cause
  with a `file:line` pointer where you have one.
- **Unconfirmed suspicions** — only if genuinely worth a look; say what you tried
  and why it did not reproduce.
- **Areas checked, nothing found** — so the next run can skip them.

If a run finds nothing, write and file it anyway and say so. A clean week is a
useful signal, and the "areas checked" list still compounds.

## Reporting the run's cost

Open the report with what the run itself cost, so the budget above can be tuned
against real numbers rather than guesses:

- **Wall clock** — always available; you noted the start time.
- **Tokens and dollars** — call the `get_session` tool (Claude Code Remote MCP)
  with `session_id` omitted and read `external_metadata.usage` (input, output and
  cache token counts, and `cost_usd`) plus `external_metadata.context_usage`.
  If that tool is not available in the run, say "usage unavailable" rather than
  estimating — a made-up number is worse than none.
- **Fan-out actually used** — how many areas and subagents, so the cost lines up
  with something you can adjust.

Do not open pull requests with fixes unless asked — the report is the
deliverable.
