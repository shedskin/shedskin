# pyvm

A tiny CPython 3.14 bytecode interpreter in Shedskin-compatible Python.

It reads real `.pyc` files (marshal format, magic 3627) with its own
unmarshaller, decodes each code object into a list of `Instr` objects
(inline `CACHE` entries stripped, jump targets resolved), and runs them.

Two dispatch strategies run over the same decoded instruction list, so
they can be benchmarked against each other:

* `--virtual`: one `Instr` subclass per opcode, `execute()` is a virtual
  call (like the pygasus example)
* `--ifelse`: a single if/elif chain on the opcode number (like the c64
  example)

Supported so far: module-level code, functions (positional args, recursion),
fast locals and the 3.14 `LOAD_FAST_LOAD_FAST` superinstruction family,
globals, int/str constants, `BINARY_OP`, `COMPARE_OP`, conditional and
unconditional jumps, and `print()`.

    python -m py_compile prog.py        # with CPython 3.14
    ./pyvm [--virtual|--ifelse] [--dis] prog.pyc
    ./pyvm                              # self-test on testdata/

The `.pyc` files in `testdata/` were compiled with `py_compile` using
`PycInvalidationMode.UNCHECKED_HASH`, so they are byte-for-byte reproducible.
