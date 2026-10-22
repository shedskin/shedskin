# Big-endian integers, the byte order of every release's bytecode, shapes
# and palettes.
from __future__ import annotations


def be16(data: bytes, pos: int) -> int:
    hi = int(data[pos])
    lo = int(data[pos + 1])
    return (hi << 8) | lo


def be32(data: bytes, pos: int) -> int:
    hi = int(be16(data, pos))
    lo = int(be16(data, pos + 2))
    return (hi << 16) | lo
