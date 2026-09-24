---
name: defect-hunt
description: Hunt for latent defects in shedskin by differential-testing translated C++ against CPython, and file the findings as a GitHub issue. Use for the weekly defect report, or when asked to go looking for bugs in a particular area (a library module, a language feature, the type inferencer).
---

# Defect hunt

Find *real, reproducible* shedskin defects and report them so they can be fixed
without further investigation. A short report of confirmed bugs beats a long
report of suspicions.

## Setup

The container may not have the repo in it. Check before assuming a working
directory — in a fresh remote container `/home/user/shedskin` has not existed:

```bash
[ -d /home/user/shedskin ] || git clone https://github.com/shedskin/shedskin.git /home/user/shedskin
cd /home/user/shedskin
./.claude/setup.sh      # installs libgc/pcre, pip install -e .
```

**Do not trust setup.sh's exit code or its "ready" line.** Its install guard is
`python3 -c 'import shedskin' || pip install -e "$repo_root"`, and because the
script runs from the repo root, `import shedskin` resolves to the source tree via
cwd and always succeeds — so `pip install -e` never runs. On a machine where
shedskin was not already installed this leaves it uninstalled while the script
still prints `setup.sh: ready (shedskin )` and exits 0. Verify for yourself and
install by hand if needed:

```bash
python3 -c 'import importlib.metadata as m; print(m.version("shedskin"))' || pip install -e .
which shedskin
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

`shedskin` and `make` generate files next to the `.py`, so **every probe needs
its own directory** — and you have to create it, `mktemp -d` only made
`$SCRATCH`:

```bash
mkdir -p "$SCRATCH/probe" && cd "$SCRATCH/probe"   # one dir per probe
python3 probe.py > cpython.txt 2>&1          # reference behaviour
timeout 120 shedskin translate probe.py && make   # translate + compile
./probe > shedskin.txt 2>&1
diff cpython.txt shedskin.txt                # a difference is a candidate defect
```

Two harness facts that will bite you otherwise: the shell's working directory
**does not persist between tool calls**, so begin every command with an absolute
`cd`; and wrapping `shedskin translate` in `timeout` turns a non-terminating type
analysis into exit 124 instead of a blocked run (a hang is itself a defect —
report it).

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
- **Read `docs/documentation.md` "Python Subset Restrictions" before you probe**,
  and put it in every subagent's brief. shedskin supports a subset on purpose,
  and a divergence from a documented non-feature is not a defect. That list
  currently rules out `eval`/`getattr`/`isinstance`, arbitrary-precision
  integers, `*args`/`**kwargs`, **ordered dicts**, multiple inheritance, nested
  functions and classes, closures, full unicode, and inheritance from builtins.
  Ordered dicts is the expensive one: dict insertion order and `popitem()` LIFO
  look like serious CPython divergences, and agents who have not read that list
  reliably report them as top-severity findings that then have to be thrown away.
- **Ignore empty-list/empty-container inference issues.** Known weak spot,
  deliberately out of scope.
- The `tests/skip_*` directories are known-unsupported; don't report those.
- Check `tests/errs/` — those are expected-error cases, not defects.
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

## Start from the previous reports

Each run starts in a fresh container, so earlier reports only reach you through
the tracker. The maintainer attaches each week's report as a `.md` file to issue
[#1286](https://github.com/shedskin/shedskin/issues/1286) ("weekly defect
report"), in the issue body or in a comment, and notes there which findings
have since been fixed and which are expected. Read these **before picking focus
areas**:

1. Read #1286 and all its comments with the GitHub MCP `issue_read` tool
   (`get`, then `get_comments`). If #1286 has been closed or replaced, search
   the issues for "weekly defect report" (any case, open or closed) and use the
   most recent one.
2. Fetch the most recent attached report, and the one before it if there is
   one. The links look like `https://github.com/user-attachments/files/...`.
   `curl` on them gets a 403 from the proxy, so use `WebFetch` instead. It
   answers with a 302 to a signed `objects.githubusercontent.com` URL that is
   valid for 5 minutes, so call `WebFetch` again on that URL right away. WebFetch
   passes the page through a small model, so ask it to return the sections
   **verbatim** rather than to summarise them.
3. Apply what you read:
   - The **skip list** and **"Deliberately not reported"** sections are
     standing exclusions. Add them to every subagent's brief.
   - **"Areas checked, nothing found"**: pick different areas this week, unless
     recent commits have touched one of them.
   - **"Recommendations" / "next hunt should focus on"**: use these as
     candidates for your focus areas.
   - If the maintainer marked a finding as **expected** (or "not a bug"), drop
     it for good and add it to the standing exclusions.

4. **Re-check every other previous finding yourself** on current `main`. Do
   not rely on the maintainer's notes to decide what is fixed: a "fixed" note
   may be wrong, and a finding with no note may have been fixed without anyone
   saying so. Do this before the new hunt, in the main session, not in
   subagents — it is a handful of `shedskin build` runs.
   - Take the findings from the latest report's "Confirmed defects" and "Still
     open from previous reports" sections. The latest report carries the older
     open findings forward, so you do not need to go further back.
   - Ask `WebFetch` for each repro **verbatim**, save it as a `.py`, run it under
     CPython and under shedskin as in the core loop, and compare.
   - Put each one in exactly one bucket: **fixed** (outputs now match; name the
     fixing commit if `git log` makes it obvious), **still failing** (same
     divergence as before), **changed** (still wrong, but differently: describe
     how), or **could not re-check** (repro missing, garbled or no longer valid
     Python; say which).
   - A finding the maintainer marked fixed that is still failing is a
     **regression** or an incomplete fix. Put it at the top of the report.
   - Do not report still-failing findings again as new, and do not spend new
     probes on them.

If the attachments cannot be fetched, say so in one line at the top of the
report, work from the issue text, and carry on. Say in the report which
previous reports you read.

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
- **Unicode support** - does unicode work across the board? so anywhere a str
  can be used (in filenames or otherwise). are common encodings supported? do
  we get proper errors/fallbacks for unsupported encodings? surrogates etc.

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
cleanly, it is cheap to re-run it under `--int32`, `--int64`, `--nogc`, `-b`,
`--predict`, `--boost`, `-w` or `-z` and diff again.

Mind what the disabling flags actually mean — they are all *off* switches, and
reading them the other way produces confident false positives. `-b` is
`--nobounds`: it turns bounds checking **off**, so out-of-range indexing
returning garbage or a NUL byte under `-b` is by design. Likewise `-w`
(`--nowrap`) drops wrap-around checking on negative indices, `-z` (`--nozero`)
makes division by zero undefined, and `--noassert` removes `assert`s. Narrowing
flags lose information on purpose too: `--int32` overflowing at 2**31 and
`--float32` printing `0.33333334` are not defects.

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
other. Fan out with subagents, each building and running its own probes in its
own scratch directory, then collect and confirm their findings yourself before
writing the report. Re-run every candidate defect yourself before it goes in the
issue.

The budget's "at most 3 focus areas" and "at most 6 subagents" reconcile by
*splitting* a broad area across two agents — "library modules" into
string/data and numeric/time, say — not by taking on more areas. Give each
agent its own scratch directory and tell it explicitly which findings other
agents have already reported, or two of them will hand you the same bug.

## The report

**One run produces exactly one report.** Everything the run found goes in it —
including anything turned up by follow-up work after you have already drafted
it. If you find more after drafting, fold it into the same report and deliver
the whole thing again; never leave findings spread across two reports, two
messages or two files. A maintainer who is not watching the session sees only
what is delivered, and a second partial report does not add to the first, it
competes with it.

Write the report once, then deliver it three ways. Do all three — they fail
independently, and between them one always gets through.

**1. A file in the repo.** Write the report to
`reports/defect-hunt/<YYYY-MM-DD>.md` and commit it to your working branch.
This is what makes the reports an archive rather than a stream of emails: they
accumulate and they diff against each other. Until they land on `main`, next
week's run reads them from #1286 (see "Start from the previous reports"), so
keep the section headings stable: "Areas checked, nothing found", "Deliberately
not reported", a skip list, and recommendations for the next run. Commit it even if you cannot
push — the file still shows in the session's diff, where it can be read and
downloaded, and it is ready to push the moment access allows.

**2. A GitHub issue** against `shedskin/shedskin`, titled
`Weekly defect report — <date>`. If filing fails with a 403, note it in one line
at the top of the report and carry on — reading the tracker still works, so
duplicate-checking is unaffected. Do not retry it or look for a way around it.
Two different 403s are possible and neither is actionable from inside the run:
GitHub's own, meaning the Claude GitHub App is not installed on the shedskin
org; or the API proxy's, which reads `GitHub access to this repository is not
enabled for this session. Use add_repo to request access.` If you get the
second, do **not** go looking for `add_repo` — it is not among the available
tools in this environment. The same authorization gap also blocks `git push`
(`access denied by the git proxy: shedskin/shedskin is not in this session's
authorized repository set`), so delivery 1 may end at the commit; say so rather
than retrying.

**3. Your final message**, which is what reaches the maintainer by email. This
one is not optional and it must be genuinely last: the turn ending is what
sends the mail, so anything you do afterwards means the mail arrived before the
work stopped. Write the file and file the issue *first*, then end the turn with
the full report.

When the run is a scheduled routine rather than someone sitting at the terminal,
`PushNotification` is what puts it in front of them — banner and inbox — so send
it too, with the report inside `<routine_summary>` tags. Note that it and the
final message are two deliveries of one report, not two reports: if you notify
and then keep working, the next notification must carry the *whole* updated
report, not just the new part.

Structure it the same way everywhere:

- **Run cost** — wall clock, tokens and dollars, and the fan-out used (see
  below).
- **Summary** — how many confirmed defects and which areas were covered.
- **Confirmed defects** — one section each, ordered by severity. Every one needs
  a minimal reproducing `.py`, the CPython output, the shedskin output (or the
  translate/compile/runtime error), and a one-line note on the suspected cause
  with a `file:line` pointer where you have one.
- **Status of previous findings** — a table with one row per finding re-checked
  in step 4 of "Start from the previous reports": ID, one-line title, bucket
  (fixed / still failing / changed / could not re-check), and the fixing commit
  where known. Keep the original IDs, so the same finding has the same ID from
  week to week.
- **Still open from previous reports** — every finding that is still failing
  or changed, each with its minimal reproducing `.py` copied through unchanged.
  This carries open findings forward, so the next run only needs to read this
  report.
- **Unconfirmed suspicions** — only if genuinely worth a look; say what you tried
  and why it did not reproduce.
- **Areas checked, nothing found** — so the next run can skip them.

If a run finds nothing, write it, file it and send it anyway, and say so. A
clean week is a useful signal, and the "areas checked" list still compounds.

## Reporting the run's cost

Open the report with what the run itself cost, so the budget above can be tuned
against real numbers rather than guesses:

- **Wall clock** — always available; you noted the start time.
- **Tokens and dollars** — call the `get_session` tool (Claude Code Remote MCP)
  with `session_id` omitted and read `external_metadata.usage` (input, output and
  cache token counts, and `cost_usd`) plus `external_metadata.context_usage`.
  **This tool is usually absent in the remote container these runs happen in** —
  if it is not there, say "usage unavailable" in one line and move on. Do not
  estimate, and do not spend the run hunting for a substitute; a made-up number
  is worse than none.
- **Fan-out actually used** — how many areas and subagents, so the cost lines up
  with something you can adjust.

Do not open pull requests with fixes unless asked — the report is the
deliverable.
