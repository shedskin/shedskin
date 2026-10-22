# The Amiga release: the DOS banks and packing, on its two floppy images or
# copied off them, with the resource list its executable carries instead of
# a MEMLIST.BIN, and the start values its game expects.
from __future__ import annotations

import os

from .adf import Disk, is_amigados
from .amiga_memlist import BANK01_SIZE_EN, BANK01_SIZE_FR, MEMLIST_EN, MEMLIST_FR
from .files import find_file
from .memlist import STATE_NOT_NEEDED, MemEntry

# rawgl leaves 0xE5 alone for the Amiga data, whose game takes up from the
# jump variable; the port follows it.
WRITES_UP_DOWN = False
HAS_PROTECTION = True
# The Amiga intro never reads a key; the port gives it the DOS way out.
INTRO_SKIP = True
# Its password screen reads the joystick only, not typed letters.
TYPED_CODES = False
# The release ships without bank05, which holds only the copy protection
# screen's pictures.
ABSENT_BANK = 5


def has_data(data_dir: str) -> bool:
    if find_file(data_dir, "bank01") != "":
        return True
    for entry in os.listdir(data_dir):
        if entry.lower().endswith(".adf"):
            return True
    return False


def bank_number(name: str) -> int:
    """The number in a bankNN file name, NN in hex, or -1 for other names."""
    low = name.lower()
    if len(low) != 6 or not low.startswith("bank"):
        return -1
    n = 0
    for i in range(4, 6):
        d = "0123456789abcdef".find(low[i])
        if d < 0:
            return -1
        n = n * 16 + d
    return n


def read_disks(data_dir: str, banks: dict[int, bytes], disks: list[str]) -> None:
    """Loads the banks on the AmigaDOS .adf images in the data directory,
    naming each image used in `disks`; other .adf files are skipped."""
    for entry in sorted(os.listdir(data_dir)):
        if not entry.lower().endswith(".adf"):
            continue
        path = os.path.join(data_dir, entry)
        if not is_amigados(path):
            continue
        disk = Disk(path)
        disks.append(entry)
        for name in disk.names():
            bank = bank_number(name)
            if bank >= 0:
                banks[bank] = disk.read(name)


def bank_source(disks: list[str]) -> str:
    """Where the banks are looked for, for an error message."""
    if len(disks) > 0:
        return "on the disk images " + ", ".join(disks)
    return "in the directory"


def read_entries(data_dir: str, bank01: bytes, entries: list[MemEntry]) -> None:
    """The resource list of the release bank01 belongs to."""
    size = len(bank01)
    if size == BANK01_SIZE_EN:
        table = MEMLIST_EN
    elif size == BANK01_SIZE_FR:
        table = MEMLIST_FR
    else:
        raise ValueError(f"{data_dir}: bank01 has {size} bytes, not a known Amiga release")
    for kind, bank, offset, packed_size, unpacked_size in table:
        entries.append(MemEntry(STATE_NOT_NEEDED, kind, 0, bank, offset,
                                packed_size, unpacked_size))


def start_vars(v: list[int]) -> None:
    # Values the copy-protection screen would have left behind; the Amiga
    # game checks 0xF2 for 6000 where DOS has 4000.
    v[0xBC] = 0x10
    v[0xC6] = 0x80
    v[0xF2] = 6000
    v[0xDC] = 33


def part_vars(v: list[int]) -> None:
    v[0xE4] = 0x14
