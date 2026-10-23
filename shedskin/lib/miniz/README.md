# miniz

Vendored copy of [miniz](https://github.com/richgel999/miniz) 3.1.2 (MIT
license, see LICENSE): the amalgamated `miniz.c` and `miniz.h` from the
release archive `miniz-3.1.2.zip`
(sha256 `f0446d863f9c19926ad9483c523fdc42e42b8d4a6a431d27e09d49c79a140d9a`),
unmodified.

It provides deflate/inflate for the `gzip` module. `gzip.cpp` compiles it
directly (`#include "miniz/miniz.c"`), so no separate build step or library
is needed, with:

- `MINIZ_NO_STDIO`, `MINIZ_NO_TIME`, `MINIZ_NO_ARCHIVE_APIS`: only the
  zlib-style stream API (`mz_deflate`, `mz_inflate`, `mz_crc32`) is used;
- `MINIZ_NO_ZLIB_COMPATIBLE_NAMES`: no plain `deflate`, `crc32` etc. names,
  which could clash with a real zlib (e.g. in an extension module).

To update, replace `miniz.c`, `miniz.h` and `LICENSE` with those of a newer
release archive.
