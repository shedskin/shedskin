# The 20th Anniversary Edition: every resource a file of its own under the
# game directory (DAT/FILEnnn.DAT), its 320x200 backgrounds gzipped BMP
# images (BGZ/), its strings the lines of TXT/<lang>.txt, and the start
# values its game expects.
from __future__ import annotations

import gzip

from .anniversary_strings import FALLBACK_STRINGS, STRING_IDS
from .files import find_file

WRITES_UP_DOWN = True
HAS_PROTECTION = False
INTRO_SKIP = False
TYPED_CODES = True

# The 320x200 backgrounds; the other ids the game asks for are its HD
# pictures (3000 and up) and sound preloads (2000 and up), which the
# original resolution has no use for.
BITMAPS = [67, 68, 69, 70, 71, 72, 73, 83, 144, 145]


def find_root(data_dir: str) -> str:
    """The directory holding DAT/, BGZ/ and TXT/: the one given, or its
    game/, or its game/game/ when given the GOG install root."""
    roots = []
    roots.append(data_dir)
    roots.append(find_file(data_dir, "game"))
    roots.append(find_file(find_file(data_dir, "game"), "game"))
    for root in roots:
        if find_file(find_file(root, "DAT"), "FILE017.DAT") != "":
            return root
    return ""


def game_file(root: str, sub: str, name: str) -> str:
    """`sub/name` in the game directory, found case-insensitively, so a copy
    from a Windows install works too."""
    path = find_file(find_file(root, sub), name)
    if path == "":
        raise FileNotFoundError(f"{root}: {sub}/{name} is missing")
    return path


def read_dat(root: str, index: int) -> bytes:
    path = game_file(root, "DAT", f"FILE{index:03d}.DAT")
    with open(path, "rb") as f:
        return f.read()


def read_bitmap(root: str, index: int) -> list[bytes]:
    """The background `index` as one palette index per pixel, if it is one;
    a picture the install lacks is skipped, as rawgl does."""
    found = []
    if index in BITMAPS:
        name = f"file{index:03d}.bgz"
        path = find_file(find_file(root, "BGZ"), name)
        if path != "":
            with gzip.open(path) as f:
                found.append(decode_bmp(f.read(), name))
    return found


# The sounds that repeat until stopped; the original's samples carry their
# loop, the edition's WAV files do not.
LOOPING_SOUNDS = [1, 3, 8, 16, 89, 97, 102, 104, 106, 132, 139]
# The music the original's modules played, as recordings.
MUSIC_TRACKS = {7: "intro.ogg", 138: "ending.ogg"}

# What a music request does with a recording.
MUSIC_NONE = 0
MUSIC_PLAY = 1
MUSIC_LOOP = 2
MUSIC_STOP = 3
# The remastered sound's ambient tracks, which loop, and the request that
# stops any recording.
AMBIENT_STOP = 5000
AMBIENT_FIRST_LOOP = 5001
AMBIENT_LAST_LOOP = 5010
# The ambience the last remastered ambient track set, which picks the
# variant of some sounds: none yet, exterior, interior, or 5006's.
AMBIENCE_NONE = 0
AMBIENCE_EXTERIOR = 1
AMBIENCE_INTERIOR = 2
AMBIENCE_5006 = 3


def sound_loops(index: int) -> bool:
    return index in LOOPING_SOUNDS


def read_wgz(path: str) -> bytes:
    """A gzipped WAV file, b"" for no path."""
    if path == "":
        return b""
    with gzip.open(path) as f:
        return f.read()


def _numbered(sounds: str, index: int) -> str:
    # Some are stored under a B suffix.
    path = find_file(sounds, f"file{index:03d}.wgz")
    if path == "":
        path = find_file(sounds, f"file{index:03d}B.wgz")
    return path


def sound_path(root: str, index: int, remastered: bool, ambience: int,
               pick: int) -> str:
    """The file of sound `index`, "" if there is none. A few remastered
    sounds come in variants: by the ambience playing, and `pick` (any
    number) choosing among takes, as the edition does at random."""
    sounds = find_file(root, "WGZ")
    if not remastered:
        return _numbered(find_file(sounds, "original"), index)
    place = "GR"
    if ambience == AMBIENCE_EXTERIOR:
        place = "EX"
    elif ambience == AMBIENCE_INTERIOR:
        place = "IN"
    if index == 81:
        return find_file(sounds, f"file081-EX-{1 + pick % 3}.wgz")
    if index == 85:
        inside = "EX" if ambience == AMBIENCE_EXTERIOR else "IN"
        return find_file(sounds, f"file085-{inside}-{1 + pick % 2}.wgz")
    if index == 96:
        return find_file(sounds, f"file096-{place}-{1 + pick % 3}.wgz")
    if index == 163:
        return find_file(sounds, f"file163-{place}-1.wgz")
    return _numbered(sounds, index)


def music_request(root: str, index: int, remastered: bool) -> tuple[int, str]:
    """What music request `index` does: (MUSIC_*, the recording's path)."""
    music = find_file(root, "OGG")
    # With the original sound too, as in rawgl.
    if index == AMBIENT_STOP:
        return (MUSIC_STOP, "")
    if not remastered:
        if index not in MUSIC_TRACKS:
            return (MUSIC_NONE, "")
        return (MUSIC_PLAY, find_file(find_file(music, "original"), MUSIC_TRACKS[index]))
    if index > AMBIENT_STOP:
        path = find_file(music, f"amb{index}.ogg")
        if AMBIENT_FIRST_LOOP <= index <= AMBIENT_LAST_LOOP:
            return (MUSIC_LOOP, path)
        return (MUSIC_PLAY, path)
    if index == 7:
        return (MUSIC_PLAY, find_file(music, "Intro_20th.ogg"))
    # The remastered ending is not played from here, as in rawgl.
    return (MUSIC_NONE, "")


def ambience_of(index: int) -> int:
    """The ambience ambient track `index` sets."""
    if index == 5005:
        return AMBIENCE_EXTERIOR
    if index == 5006:
        return AMBIENCE_5006
    return AMBIENCE_INTERIOR


def sound_period(period: int) -> int:
    """The edition's period table lacks the original's 170 and starts one
    entry later, so the bytecode's index needs shifting to the same pitch."""
    if period != 0:
        period -= 1
    if period >= 32:
        period += 1
    return period


def _le32(data: bytes, pos: int) -> int:
    """An unsigned little-endian long."""
    return int(data[pos]) | (int(data[pos + 1]) << 8) \
        | (int(data[pos + 2]) << 16) | (int(data[pos + 3]) << 24)


def decode_bmp(data: bytes, name: str) -> bytes:
    """A 20th Anniversary background: an 8-bit 320x200 BMP whose pixel
    values are the palette indices; the palette it carries is not used."""
    if len(data) < 54 or data[0:2] != b"BM" or _le32(data, 0x12) != 320 \
            or _le32(data, 0x16) != 200 or int(data[0x1C]) != 8 or _le32(data, 0x1E) != 0:
        raise ValueError(f"{name}: not an uncompressed 320x200 8-bit BMP")
    if _le32(data, 0x0A) + 320 * 200 > len(data):
        raise ValueError(f"{name}: the BMP is cut short")
    start = int(_le32(data, 0x0A))
    out = bytearray()
    # BMP rows run bottom-up.
    for y in range(199, -1, -1):
        row = start + y * 320
        for x in range(320):
            # The pictures use indices 0-15 only; the mask keeps a stray
            # value from reaching past the 16-color palette.
            out.append(int(int(data[row + x]) & 0xF))
    return bytes(out)


def _decode_text_line(line: bytes) -> str:
    """One line of a 20th Anniversary TXT file in the DOS string form:
    `\\n` breaks the line and `\\2x` / `\\3x` name a glyph by number.
    Characters the 8x8 font lacks (tabs, accented letters) become spaces,
    which keep their column as the original's drawing does."""
    out = []
    i = 0
    n = len(line)
    while i < n:
        c = int(line[i])
        if c == 0x5C and i + 1 < n:  # backslash
            e = int(line[i + 1])
            if e == 0x6E:  # n
                out.append("\n")
                i += 2
                continue
            if (e == 0x32 or e == 0x33) and i + 2 < n:
                code = (e - 0x30) * 10 + (int(line[i + 2]) - 0x30)
                if 0x20 <= code < 0x7F:
                    out.append(chr(code))
                else:
                    out.append(" ")
                i += 3
                continue
            i += 2
            continue
        if c == 0x0D:
            out.append("\n")
        elif 0x20 <= c < 0x7F:
            out.append(chr(c))
        else:
            out.append(" ")
        i += 1
    return "".join(out)


def read_strings(root: str, lang: str) -> dict[int, str]:
    """The strings in `lang` (EN, FR, DE, ES or IT), by the id the bytecode
    draws them with."""
    # The Windows install has TXT/<lang>.txt, the Linux one TXT/Linux/.
    txt = find_file(root, "TXT")
    path = find_file(txt, f"{lang}.txt")
    if path == "":
        path = find_file(find_file(txt, "Linux"), f"{lang}.txt")
    lines = []
    if path != "":
        with open(path, "rb") as f:
            lines = f.read().split(b"\n")
    table = {}
    for i in range(len(STRING_IDS)):
        sid = STRING_IDS[i]
        # 0x193 is listed twice; rawgl's lookup stops at the first.
        if sid in table:
            continue
        if i < len(lines):
            line = lines[i]
            # A Windows copy of the file ends its lines with CR LF.
            if len(line) > 0 and int(line[len(line) - 1]) == 0x0D:
                line = line[:len(line) - 1]
            table[sid] = _decode_text_line(line)
        else:
            table[sid] = FALLBACK_STRINGS[i]
    return table


# The continue screen's prompt and its "ACCESS CODE:" label.
CONTINUE_SCREEN = [0x13D, 0x13C]


def fill_continue_screen(table: dict[int, str]) -> None:
    """Gives the continue screen's lines, which the edition leaves blank,
    the built-in text."""
    for i in range(len(STRING_IDS)):
        sid = STRING_IDS[i]
        if sid in CONTINUE_SCREEN and table[sid].strip() == "":
            table[sid] = FALLBACK_STRINGS[i]


def start_vars(v: list[int]) -> None:
    """The edition's game has its protection check stubbed out, so it needs
    none of the protection values."""


def part_vars(v: list[int], remastered: bool) -> None:
    # Set at every part start, as rawgl does: normal difficulty, and which
    # of the edition's sounds the bytecode asks for.
    v[0xBF] = 1
    v[0xDE] = 1 if remastered else 0
