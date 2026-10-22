# Changes from upstream

Every change `prep.py` makes to the game of
[tpy-another-world](https://github.com/trozen/tpy-another-world) (commit
5893aa2), with what needs it and what could make it unnecessary. Everything
else is upstream's code, unchanged.

## Needed

1. **TurboPython's fixed-width ints.** `from tpy import int32, ...` is
   dropped, and `int32(x)`, `uint8(x)` and the other widths become
   `int(x)`.
   - Why: `tpy` is TurboPython's own module. Its conversions are called with
     ints, bools and floats, so as Python functions their parameter would
     mix types, which Shedskin's C++ cannot do (items 4 and 5 of
     shedskin#1420).
   - Possible fix: unify bool with int in a parameter, as bool is an int
     subclass; or a `tpy` module in Shedskin with these as builtin-like
     conversions.

2. **argparse.** The parser in `main.py` is replaced by the generated
   `another_world/cmdline.py`: the same options, a class with a typed field
   per option, parsed with `getopt.gnu_getopt`, with argparse's help, usage
   and error messages.
   - Why: Shedskin has no argparse. Its `Namespace` gets a field per
     `add_argument` call, of the type set by `type=`, `action=` and
     `default=`, which Shedskin's type analysis cannot follow.
   - Possible fix: what TurboPython does, a translation-time step that reads
     the literal `add_argument` calls and generates a typed class and a
     parser (prep.py's `gen_cmdline` is such a step, run under CPython).
   - Differences: the help is wrapped for 80 columns, where argparse wraps
     for the terminal's width; getopt's message for an ambiguous option
     abbreviation differs from argparse's.

3. **subprocess.** `subprocess.py` (written by hand) has the part of
   `Popen` the game uses (stdin `PIPE`/`DEVNULL`, stdout and stderr
   `DEVNULL`, `.stdin.write`/`.flush`, `poll`, `kill`, `wait`), over
   `os.fork`, `os.pipe`, `os.dup2` and `os.execvpe`. A failed exec is
   reported to the parent through a close-on-exec pipe and raised there as
   `OSError`, as in CPython.
   - Why: Shedskin has no subprocess module.
   - Possible fix: a subprocess module in Shedskin's lib; this shim could be
     its start.

4. **`poll()` returning None.** `audio.py` tests `poll()` results with
   `!= NO_STATUS` and `== NO_STATUS` instead of `is not None` and
   `is None` (two places). The shim's `poll()` returns `NO_STATUS` while
   the process runs, and its `stdin=`/`stdout=`/`stderr=` default to
   `INHERIT` (0) instead of None.
   - Why: Shedskin cannot mix None and int in a value (shedskin#424,
     shedskin#1490).
   - Possible fix: optional ints (a boxed int, or std::optional).

## Not needed (by choice)

5. **Annotations.** Variable annotations are dropped, and declarations
   without a value (`player: Popen | None` in a class body) become comments.
   Function signatures stay, with TurboPython's types as plain Python ones:
   `int32` as `int`, `Own[T]` as `T`, `types.FrameType` as `object`
   (`prep.py --no-signatures` drops them too). Shedskin skips annotations
   of every kind (module and class level, `Final`, quoted), so they could
   all stay as upstream has them.

6. **`from typing import Final` and `from types import FrameType`.**
   Dropped with the annotations that use them. Shedskin skips typing
   imports. It has no `types` module, so `from types import FrameType`
   would fail (item 14 of shedskin#1420); a `types` module with
   `FrameType` and friends, or skipping imports only annotations use, would
   allow it.

## Needed before, now supported by Shedskin

Shedskin's benchmark build of the engine core (upstream's
`bench/shedskin/build.py`) rewrote these too. They now work as written:

- `try..finally` (shedskin#1470), with return, break and continue inside,
  and nested; the game's cleanup in `main()` and `WavWriter.close` relies on
  it.
- `from ..binary import be32` in a plain module (relative imports two
  levels up), and `from __future__ import annotations`.
- `match` statements on literal patterns, and f-string format specs
  (`f"bank{n:02x}"`).
- `signal.signal`: the game's SIGTERM and SIGHUP handler calls `sys.exit`,
  and leaves through `main()`'s finally blocks, which restore the terminal.
  The handler runs at the next check: in `time.sleep` (which the signal
  interrupts), and right after `os.kill` and `signal.raise_signal`.
- `termios` and `tty` (`tcgetattr`, `tcsetattr`, `TCSAFLUSH`,
  `termios.error`, `tty.setraw`). `tcgetattr` returns a `TermAttributes`
  object rather than a list: indexable like the list for the six
  flag/speed fields, with the control characters as a list of ints in
  `.cc`. The game only saves and restores it.
- `gzip.open(path)` and `GzipFile.read()`, with an inflate of Shedskin's
  own (no zlib dependency). Upstream's benchmark build stubbed gzip out, so
  it could not read the 20th Anniversary Edition. Differences from CPython:
  the file is decompressed when it is opened, so errors come at `open()`
  rather than at the first `read()`, and bad deflate data raises
  `BadGzipFile` rather than `zlib.error`.

## Warnings left

- `main.py: expression has no type`, at `e.strerror` after
  `except OSError as e`. The handlers of a function share one variable `e`,
  and an earlier `except (OSError, ValueError) as e` leaves it typed
  ValueError. The C++ is right, as each `catch` declares its own `e`.
  Giving each handler its own variable would fix the warning (simply
  merging the classes is not right: it moves attributes such as `e.code`
  out of the classes that define them).
- `system 'KeyboardInterrupt' is not caught`. In the terminal the game
  reads Ctrl-C as a key (raw mode), so it quits normally. A SIGINT from
  outside kills it without restoring the terminal, where CPython raises
  KeyboardInterrupt and cleans up. Possible fix: a default SIGINT handler
  that raises KeyboardInterrupt, now that signal.signal handlers run at
  safe points.
- `Function (Class Popen, 'terminate') not called!`: the shim's unused
  method.
