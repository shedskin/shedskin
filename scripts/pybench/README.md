# pybench

Times programs from the Shed Skin examples under several Python
implementations, each built from git: CPython (with and without its JIT),
PyPy, Shed Skin and TurboPython. The default program set is the eight
examples that TurboPython has ported (`tpy-examples/shedskin`), so every
implementation runs every program.

```sh
./pybench.py build                       # clone and build everything (hours: PGO+LTO, PyPy translation)
./pybench.py --pypy pypy3 build          # same, but use the installed PyPy instead of building it
./pybench.py run                         # time all programs on all implementations
./pybench.py --pypy pypy3 run -i "PyPy 7.3.15" -p sieve
./pybench.py report                      # times, and speedups over the baseline
```

Implementations are named as in `config.toml`; `list` shows them, what each
is built from, whether it is built yet, and how many programs it has results
for. `run` builds what it needs, so `build` is optional. Some examples:

```sh
./pybench.py list

# one CPython, with and without its JIT (both rows use the same build)
./pybench.py run -i "CPython 3.15" -i "CPython 3.15 JIT"

# Shed Skin releases against each other, on two programs
./pybench.py run -i "Shed Skin 0.9.14" -i "Shed Skin main" -p sieve -p voronoi

# CPython 3.14 against Shed Skin main and TurboPython, then compare
./pybench.py build "CPython 3.14" "Shed Skin main" "TurboPython 0.6.2"
./pybench.py run -i "CPython 3.14" -i "Shed Skin main" -i "TurboPython 0.6.2"
./pybench.py report -b "CPython 3.14"
```

To add a version, copy an `[[impl]]` entry in `config.toml` and give it a new
`name` and a `ref`: a tag, a branch, or a commit. For example, an older
CPython release, and a Shed Skin branch:

```toml
[[impl]]
name = "CPython 3.13.0"
kind = "cpython"
ref = "v3.13.0"

[[impl]]
name = "Shed Skin my-branch"
kind = "shedskin"
ref = "my-branch"
flags = ["-b"]
```

A branch is fetched once, when it is first built. To pick up newer commits,
delete its directory under `<work>/impl/` and re-run with `-f`.

Implementations, refs, program list and run counts live in `config.toml`.
Builds, program copies and `results.json` go to the work directory
(`~/.cache/pybench`, or `-w DIR`). Results are saved after every program, so
`run` can be interrupted and restarted; `-f` re-runs programs that already have
a time.

How each kind is built:

- **cpython**: `./configure --enable-optimizations --with-lto` with gcc, plus
  `--enable-experimental-jit` where `jit` names an LLVM version (3.13+). One
  build serves both the JIT and non-JIT rows, through `PYTHON_JIT=1/0`.
  `configure` and `make` add arguments to those steps. LLVM release
  tarballs are at https://github.com/llvm/llvm-project/releases; the LLVM 18
  one needs `libtinfo.so.5`, which newer Ubuntus lack: copy it from Ubuntu
  22.04's `libtinfo5` package into the tarball's `lib/` (a symlink to
  `libtinfo.so.6` doesn't work).
  Python 2.7 runs each program with `from __future__ import print_function,
  division` added.
- **pypy**: translated with `rpython --opt=jit`, hosted by the `host`
  implementation (a Python 2.7), and run from the source tree. With `--pypy
  EXE`, the installed PyPy replaces these, named by its version.
- **shedskin**: installed in a venv; each program is built with `shedskin
  translate <flags>` and the generated Makefile. `[shedskin_flags]` adds
  flags for single programs, such as `--int64` for collatz.
- **tpy**: installed in a venv; each port is built with `tpyc --build`.

Compiling is not timed. Each program runs its workload ten times and prints
`TIME` for the last five, so that PyPy and the CPython JIT have warmed up;
that is the time recorded (best of `runs.interpreter` or `runs.compiled`
runs). Wall-clock times of the whole process are kept as well, under `wall`
in `results.json`. Programs that use `random` can print different results
under Shed Skin or Python 2.7, whose random number generators differ from
CPython 3's, but they do the same amount of work.
