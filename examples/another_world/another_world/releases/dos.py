# The DOS release: MEMLIST.BIN, the resource list its BANKxx files are read
# through, and the start values its game expects.
from __future__ import annotations

from ..binary import be32
from .files import find_file
from .memlist import STATE_END_OF_LIST, MemEntry

WRITES_UP_DOWN = True
HAS_PROTECTION = True
# The DOS intro ends at the action key by itself.
INTRO_SKIP = False
TYPED_CODES = True


def memlist_path(data_dir: str) -> str:
    return find_file(data_dir, "memlist.bin")


def read_memlist(path: str, entries: list[MemEntry]) -> None:
    with open(path, "rb") as f:
        raw = f.read()
    pos = 0
    while int(raw[pos]) != STATE_END_OF_LIST:
        entries.append(MemEntry(
            int(raw[pos]), int(raw[pos + 1]), int(raw[pos + 6]),
            int(raw[pos + 7]), int(be32(raw, pos + 8)),
            int(be32(raw, pos + 12)), int(be32(raw, pos + 16))))
        pos += 20


def start_vars(v: list[int]) -> None:
    # Values the copy-protection screen would have left behind.
    v[0xBC] = 0x10
    v[0xC6] = 0x80
    v[0xF2] = 4000
    v[0xDC] = 33


def part_vars(v: list[int]) -> None:
    v[0xE4] = 0x14
