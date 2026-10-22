# another_world

The Another World (Out of This World) engine of
[tpy-another-world](https://github.com/trozen/tpy-another-world), at its
commit 5893aa2: the bytecode VM, the resource loader with its ByteKiller
unpacker, the polygon rasterizer, the sound and music mixer, drawn in the
terminal with block glyphs and 24-bit color. GPL-2.0, see `LICENSE`; Another
World is by Eric Chahi.

No game data is included. It reads the DOS release, the Amiga release (the
two `.adf` floppy images) and the 20th Anniversary Edition from GOG (which
also includes the Amiga version).

```bash
shedskin build aw.py
build/aw DIR                       # DIR holds the game data; no DIR shows the keys and options
build/aw DIR --frames 300 --digests | head   # headless, one digest per frame
```

Or `shedskin translate aw.py && make`, giving `./aw`. Sound goes through
`pw-play`, `paplay`, `aplay` or SoX's `play`, the first of them that works.

## Changes for Shedskin

The upstream engine is written for TurboPython. `prep.py` copies it here
(`python3 prep.py TPY_ANOTHER_WORLD_CHECKOUT`), with these changes:

- TurboPython's fixed-width ints (`int32(x)` and so on) are plain `int`, and
  its `tpy` imports are gone.
- Variable annotations are dropped; declarations without a value are kept as
  comments. Function signatures are kept (Shedskin ignores them), in plain
  Python types.
- The argparse parser in `main.py` is replaced by `another_world/cmdline.py`,
  generated from that parser: a class with a typed field per option, parsed
  with `getopt.gnu_getopt`, with argparse's help, usage and error messages.
- `subprocess.py` (written by hand) has the part of `subprocess.Popen` the
  game uses, over `os.fork` and `os.execvpe`; as Shedskin cannot mix `None`
  and `int`, `poll()` returns `NO_STATUS` while the process runs, and the
  game's two `is None` tests of it are rewritten.

`CHANGES.md` goes through these, with what needs each of them. The rest is
as upstream, including `try..finally`, `match`, relative imports,
`signal.signal`, `termios`, `tty` and `gzip`.

Built with Shedskin, it renders the same frames and writes the same WAV
output as under CPython. 3000 frames of the Amiga intro with `--wav` take
0.57 s, against 44.5 s under CPython 3.13.
