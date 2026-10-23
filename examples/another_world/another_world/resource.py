# Game resources: which release the data directory holds, the resource
# list the DOS and Amiga releases share, and the four segments the current
# game part runs from. What each release does its own way lives in
# releases/.
from __future__ import annotations

from .codes import read_code_strings, read_codes, read_letter_labels, relabel
from .releases import amiga, anniversary, dos
from .releases.bytekiller import unpack
from .releases.files import find_file
from .releases.memlist import (RT_BITMAP, STATE_LOAD_ME, STATE_LOADED, STATE_NOT_NEEDED,
                               MemEntry)
from .sound import Sample, no_sample, raw_sample, wav_sample
from .text import string_table

RELEASE_DOS = 0
RELEASE_AMIGA = 1
RELEASE_20TH = 2

GAME_PART_FIRST = 16000
GAME_PART_LAST = 16009
PART_INTRO = 16001

# Per game part: the palette, bytecode, cinematic polygons and shared shapes
# (0 = none) it loads, as MEMLIST indices.
PARTS = [
    (0x14, 0x15, 0x16, 0x00),  # 16000 copy protection
    (0x17, 0x18, 0x19, 0x00),  # 16001 intro
    (0x1A, 0x1B, 0x1C, 0x11),  # 16002 water
    (0x1D, 0x1E, 0x1F, 0x11),  # 16003 jail
    (0x20, 0x21, 0x22, 0x11),  # 16004 city
    (0x23, 0x24, 0x25, 0x00),  # 16005 arena
    (0x26, 0x27, 0x28, 0x11),  # 16006 baths
    (0x29, 0x2A, 0x2B, 0x11),  # 16007 final
    (0x7D, 0x7E, 0x7F, 0x00),  # 16008 password screen
    (0x7D, 0x7E, 0x7F, 0x00),  # 16009 password screen
]


def decode_planar(src: bytes) -> bytes:
    """A DOS or Amiga background: 4 bit planes of 8000 bytes, the leftmost
    pixel in the high bit, into one palette index per pixel."""
    out = bytearray()
    for k in range(8000):
        b0 = int(src[k])
        b1 = int(src[8000 + k])
        b2 = int(src[16000 + k])
        b3 = int(src[24000 + k])
        for bit in range(8):
            shift = 7 - bit
            out.append(int(((b0 >> shift) & 1) | (((b1 >> shift) & 1) << 1)
                             | (((b2 >> shift) & 1) << 2) | (((b3 >> shift) & 1) << 3)))
    return bytes(out)


class Resources:
    """The game data of one release: for DOS and Amiga the loaded state of
    every entry of its resource list, for the 20th Anniversary Edition its
    files; and the four segments the current game part runs from."""

    # data_dir: str
    # release: int
    # The 20th Anniversary Edition's game directory.
    # nth_root: str
    # The Amiga floppy images the banks were read from, for error messages.
    # disks: list[str]
    # entries: list[MemEntry]
    # banks: dict[int, bytes]
    # loaded: dict[int, bytes]
    # current_part: int
    # requested_part: int
    # palettes: bytes
    # bytecode: bytes
    # cinematic: bytes
    # shapes: bytes
    # What the release's game expects of the engine.
    # writes_up_down: bool
    # has_protection: bool
    # intro_skip: bool
    # typed_codes: bool
    # The letters the password screen shows for those it takes, where they
    # differ, and the other way round, as lowercase keys.
    # letter_labels: dict[int, int]
    # label_keys: dict[int, int]
    # The 20th Anniversary Edition's sound files, read once each, by path.
    # wavs: dict[str, bytes]
    # Its remastered sound instead of the original's; the ambience the
    # last ambient track set, and the state choosing among takes.
    # remastered_audio: bool
    # ambience: int
    # pick: int
    # Resources read from the data files so far, so a benchmark can check
    # that none is read while it is timing the engine.
    # loads: int

    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        self.release = RELEASE_DOS
        self.entries = []
        self.banks = {}
        self.disks = []
        self.loaded = {}
        self.current_part = 0
        self.requested_part = 0
        self.palettes = b""
        self.bytecode = b""
        self.cinematic = b""
        self.shapes = b""
        self.writes_up_down = True
        self.has_protection = True
        self.intro_skip = False
        self.typed_codes = True
        self.letter_labels = {}
        self.label_keys = {}
        self.wavs = {}
        self.remastered_audio = False
        self.ambience = anniversary.AMBIENCE_NONE
        self.pick = 1
        self.loads = 0
        self.nth_root = anniversary.find_root(data_dir)
        memlist = dos.memlist_path(data_dir)
        if self.nth_root != "":
            self.release = RELEASE_20TH
            self.writes_up_down = anniversary.WRITES_UP_DOWN
            self.has_protection = anniversary.HAS_PROTECTION
            self.intro_skip = anniversary.INTRO_SKIP
            self.typed_codes = anniversary.TYPED_CODES
            text = anniversary.read_strings(self.nth_root, "EN")
            self.letter_labels = read_letter_labels(self._part_bytecode(GAME_PART_LAST), text)
            for taken in self.letter_labels:
                self.label_keys[self.letter_labels[taken] | 0x20] = taken | 0x20
        elif memlist != "":
            dos.read_memlist(memlist, self.entries)
            self.writes_up_down = dos.WRITES_UP_DOWN
            self.has_protection = dos.HAS_PROTECTION
            self.intro_skip = dos.INTRO_SKIP
            self.typed_codes = dos.TYPED_CODES
        elif amiga.has_data(data_dir):
            self.release = RELEASE_AMIGA
            amiga.read_disks(data_dir, self.banks, self.disks)
            if 1 not in self.banks:
                self.banks[1] = self._read_bank_file(1)
            amiga.read_entries(data_dir, self.banks[1], self.entries)
            self.writes_up_down = amiga.WRITES_UP_DOWN
            self.has_protection = amiga.HAS_PROTECTION
            self.intro_skip = amiga.INTRO_SKIP
            self.typed_codes = amiga.TYPED_CODES
        else:
            raise FileNotFoundError(
                f"{data_dir}: no 20th Anniversary game directory, MEMLIST.BIN, "
                ".adf disk images or bank01")

    def start_vars(self, v: list[int]) -> None:
        """Sets the variables the release's game expects at its start."""
        if self.release == RELEASE_20TH:
            anniversary.start_vars(v)
        elif self.release == RELEASE_AMIGA:
            amiga.start_vars(v)
        else:
            dos.start_vars(v)

    def part_vars(self, v: list[int]) -> None:
        """Sets the variables the release's game expects at a part start."""
        if self.release == RELEASE_20TH:
            anniversary.part_vars(v, self.remastered_audio)
        elif self.release == RELEASE_AMIGA:
            amiga.part_vars(v)
        else:
            dos.part_vars(v)

    def strings(self) -> dict[int, str]:
        """The text the bytecode draws, by string id."""
        if self.release == RELEASE_20TH:
            table = anniversary.read_strings(self.nth_root, "EN")
            anniversary.fill_continue_screen(table)
        else:
            table = string_table()
        # The continue screen shows the code of the checkpoint the game
        # restarts at, as the password screen takes it: the built-in table
        # has the DOS codes, and the 20th Anniversary Edition's are blank.
        codes = self.checkpoint_codes()
        parts = []
        for name in codes:
            part = codes[name][0]
            if part not in parts:
                parts.append(part)
        for part in parts:
            drawn = read_code_strings(self._part_bytecode(part), part, codes)
            for string_id, name in drawn.items():
                table[string_id] = name
        return table

    def _read_bank_file(self, bank: int) -> bytes:
        path = find_file(self.data_dir, f"bank{bank:02x}")
        if path == "":
            raise FileNotFoundError(
                f"{self.data_dir}: no bank{bank:02X} {amiga.bank_source(self.disks)}")
        with open(path, "rb") as f:
            return f.read()

    def _has_bank(self, bank: int) -> bool:
        return bank in self.banks or find_file(self.data_dir, f"bank{bank:02x}") != ""

    def read(self, index: int) -> bytes:
        self.loads += 1
        e = self.entries[index]
        if e.bank not in self.banks:
            self.banks[e.bank] = self._read_bank_file(e.bank)
        packed = self.banks[e.bank][e.offset:e.offset + e.packed_size]
        if e.packed_size == e.size:
            return packed
        return unpack(packed)

    def load_marked(self) -> list[bytes]:
        """Loads every entry marked LOAD_ME, highest rank first. Bitmaps are
        not kept: they are returned, for the caller to put into page 0."""
        bitmaps = []
        while True:
            best = -1
            best_rank = 0
            for i in range(len(self.entries)):
                candidate = self.entries[i]
                if candidate.state == STATE_LOAD_ME and best_rank <= candidate.rank:
                    best_rank = candidate.rank
                    best = i
            if best < 0:
                return bitmaps
            e = self.entries[best]
            # Only the bank the Amiga release lacks by design is skipped;
            # any other missing bank is an error when it is read.
            if e.bank == 0 or (self.release == RELEASE_AMIGA and e.bank == amiga.ABSENT_BANK
                               and not self._has_bank(e.bank)):
                e.state = STATE_NOT_NEEDED
                continue
            data = self.read(best)
            if e.kind == RT_BITMAP:
                bitmaps.append(decode_planar(data))
                e.state = STATE_NOT_NEEDED
            else:
                self.loaded[best] = data
                e.state = STATE_LOADED

    def sound(self, index: int) -> Sample:
        """Sound effect `index`, empty when it is not there to play."""
        if self.release == RELEASE_20TH:
            # The takes some remastered sounds have are picked by an LCG,
            # so a run stays repeatable.
            self.pick = int((int(self.pick) * 1103515245 + 12345) & 0x7FFFFFFF)
            path = anniversary.sound_path(self.nth_root, index, self.remastered_audio,
                                          self.ambience, self.pick >> 16)
            if path not in self.wavs:
                self.loads += 1
                self.wavs[path] = anniversary.read_wgz(path)
            return wav_sample(self.wavs[path], anniversary.sound_loops(index))
        if self.is_loaded(index):
            return raw_sample(self.entry(index))
        return no_sample()

    def sound_period(self, period: int) -> int:
        if self.release == RELEASE_20TH:
            return anniversary.sound_period(period)
        return period

    def music_request(self, index: int) -> tuple[int, str]:
        """What music request `index` does with a recording: (MUSIC_*, its
        path); MUSIC_NONE for one a module plays."""
        if self.release != RELEASE_20TH:
            return (anniversary.MUSIC_NONE, "")
        request = anniversary.music_request(self.nth_root, index, self.remastered_audio)
        if self.remastered_audio and index > anniversary.AMBIENT_STOP:
            self.ambience = anniversary.ambience_of(index)
        return request

    def is_loaded(self, index: int) -> bool:
        return index < len(self.entries) and self.entries[index].state == STATE_LOADED

    def request(self, index: int) -> list[bytes]:
        """Loads one entry, or, for a game part number, asks for that part
        to start at the next frame. Ids that name nothing are ignored."""
        if index >= GAME_PART_FIRST:
            self.requested_part = index
            return []
        if self.release == RELEASE_20TH:
            self.loads += 1
            return anniversary.read_bitmap(self.nth_root, index)
        if index >= len(self.entries):
            return []
        e = self.entries[index]
        if e.state == STATE_NOT_NEEDED:
            e.state = STATE_LOAD_ME
            return self.load_marked()
        return []

    def invalidate_media(self) -> None:
        """Drops sounds, music and bitmaps, keeping the part's segments."""
        for e in self.entries:
            if e.kind <= RT_BITMAP or e.kind > 6:
                e.state = STATE_NOT_NEEDED

    def segment(self, which: int) -> bytes:
        """The current part's bytecode, palettes, cinematic polygons or
        shared shapes (0-3)."""
        if which == 0:
            return self.bytecode
        if which == 1:
            return self.palettes
        if which == 2:
            return self.cinematic
        return self.shapes

    def entry(self, index: int) -> bytes:
        return self.loaded[index]

    def setup_part(self, part: int) -> None:
        if part == self.current_part:
            return
        if part < GAME_PART_FIRST or part > GAME_PART_LAST:
            raise ValueError(f"invalid game part {part}")
        pal, code, cine, shapes = PARTS[part - GAME_PART_FIRST]
        if self.release != RELEASE_20TH:
            for e in self.entries:
                e.state = STATE_NOT_NEEDED
            self.entries[pal].state = STATE_LOAD_ME
            self.entries[code].state = STATE_LOAD_ME
            self.entries[cine].state = STATE_LOAD_ME
            if shapes != 0:
                self.entries[shapes].state = STATE_LOAD_ME
            self.load_marked()
        self.palettes = self._load(pal)
        self.bytecode = self._load(code)
        self.cinematic = self._load(cine)
        if shapes != 0:
            self.shapes = self._load(shapes)
        self.current_part = part

    def checkpoint_codes(self) -> dict[str, tuple[int, int]]:
        """The password screen's codes, spelled as it shows them, each mapped
        to (part, checkpoint)."""
        codes = read_codes(self._part_bytecode(GAME_PART_LAST))
        if len(self.letter_labels) == 0:
            return codes
        shown = {}
        for name in codes:
            start = codes[name]
            shown[relabel(name, self.letter_labels)] = (start[0], start[1])
        return shown

    def taken_key(self, key: int) -> int:
        """The key the password screen takes for a lowercase letter typed,
        so that a letter types what the screen shows for it."""
        if key in self.label_keys:
            return self.label_keys[key]
        return key

    def _part_bytecode(self, part: int) -> bytes:
        return self._load(PARTS[part - GAME_PART_FIRST][1])

    def _load(self, index: int) -> bytes:
        """One part segment: its own file in the 20th Anniversary Edition,
        a resource list entry elsewhere."""
        if self.release == RELEASE_20TH:
            self.loads += 1
            return anniversary.read_dat(self.nth_root, index)
        return self.read(index)
