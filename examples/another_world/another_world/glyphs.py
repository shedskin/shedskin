# For each cell layout, the glyph for every on/off pattern of the cell's
# pixels: bit (row * width + col) set means drawn in the foreground color.
from __future__ import annotations


def _utf8(cp: int) -> str:
    # Not chr(): it truncates code points above 127 (BUGS.md#chr-above-127-truncates).
    if cp < 0x80:
        return bytes([cp]).decode()
    if cp < 0x800:
        return bytes([0xC0 | (cp >> 6), 0x80 | (cp & 0x3F)]).decode()
    if cp < 0x10000:
        return bytes([0xE0 | (cp >> 12), 0x80 | ((cp >> 6) & 0x3F),
                      0x80 | (cp & 0x3F)]).decode()
    return bytes([0xF0 | (cp >> 18), 0x80 | ((cp >> 12) & 0x3F),
                  0x80 | ((cp >> 6) & 0x3F), 0x80 | (cp & 0x3F)]).decode()


def _in_order(n: int, first: int, older: dict[int, str]) -> list[str]:
    """Unicode encodes a block-mosaic set in pattern order, leaving out the
    patterns an older character already draws."""
    out = []
    cp = first
    for mask in range(n):
        if mask in older:
            out.append(older[mask])
        else:
            out.append(_utf8(cp))
            cp += 1
    return out


def _sextant() -> list[str]:
    older = {
        0: " ", 21: "\u258c", 42: "\u2590", 63: "\u2588",
    }
    return _in_order(64, 0x1FB00, older)


def _octant() -> list[str]:
    # The octants skip every pattern a quadrant, half, quarter or
    # three-quarter block, or one of the six quarter-cell blocks encoded
    # before them, draws.
    older = {
        0: " ", 1: "\U0001cea8", 2: "\U0001ceab", 3: "\U0001fb82",
        5: "\u2598", 10: "\u259d", 15: "\u2580", 20: "\U0001fbe6",
        40: "\U0001fbe7", 63: "\U0001fb85", 64: "\U0001cea3", 80: "\u2596",
        85: "\u258c", 90: "\u259e", 95: "\u259b", 128: "\U0001cea0",
        160: "\u2597", 165: "\u259a", 170: "\u2590", 175: "\u259c",
        192: "\u2582", 240: "\u2584", 245: "\u2599", 250: "\u259f",
        252: "\u2586", 255: "\u2588",
    }
    return _in_order(256, 0x1CD00, older)


def _braille() -> list[str]:
    # Braille dots 1-3 and 7 run down the left column, 4-6 and 8 the right.
    dot_of_pixel = [0, 3, 1, 4, 2, 5, 6, 7]
    out = []
    for mask in range(256):
        dots = 0
        for i in range(8):
            if mask & (1 << i):
                dots |= 1 << dot_of_pixel[i]
        out.append(_utf8(0x2800 + dots))
    return out


HALF = [" ", "\u2580", "\u2584", "\u2588"]

QUAD = [
    " ", "\u2598", "\u259d", "\u2580", "\u2596", "\u258c", "\u259e", "\u259b",
    "\u2597", "\u259a", "\u2590", "\u259c", "\u2584", "\u2599", "\u259f", "\u2588",
]

SEXTANT = _sextant()
OCTANT = _octant()
BRAILLE = _braille()
