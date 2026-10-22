# The 320x200 16-color video: four pages of palette indices, the polygon
# rasterizer the bytecode draws with, and page fill/copy/flip.
from __future__ import annotations

from .binary import be16
from .screen import Screen
from .text import FONT

W = 320
H = 200
PAGE_SIZE = W * H

# Polygon "colors" above 15 are not palette entries: 0x10 sets the high bit of
# what is already there (the game's translucency), anything higher copies the
# pixel from page 0 (the background).
COLOR_BLEND = 0x10
COLOR_BACKGROUND = 0x11


def s16(v: int) -> int:
    """Wraps to int16, the width the original keeps coordinates in."""
    v &= 0xFFFF
    if v >= 0x8000:
        return v - 0x10000
    return v


class Video:
    # The four pages back to back. Page indices: `work` is drawn into, `front`
    # is on screen, `back` is the other half of the double buffer.
    # mem: bytearray
    # work: int
    # front: int
    # back: int
    # palette: list[int]
    # palette_requested: int
    # interp: list[int]
    # The polygon being filled, in object space.
    # bbw: int
    # bbh: int
    # npoints: int
    # px: list[int]
    # py: list[int]
    # strings: dict[int, str]

    def __init__(self) -> None:
        self.mem = bytearray(4 * PAGE_SIZE)
        self.back = 1
        self.front = 2
        self.work = self.front
        self.palette = [0] * 16
        self.palette_requested = 0xFF
        # 1/dy in 2.14 fixed point, for stepping polygon edges.
        self.interp = [0x4000] * 0x400
        for i in range(1, 0x400):
            self.interp[i] = 0x4000 // i
        self.bbw = 0
        self.bbh = 0
        self.npoints = 0
        self.px = [0] * 50
        self.py = [0] * 50
        self.strings = {}

    def page_index(self, page: int) -> int:
        if page <= 3:
            return page
        if page == 0xFF:
            return self.back
        if page == 0xFE:
            return self.front
        return 0

    def select_page(self, page: int) -> None:
        self.work = self.page_index(page)

    def fill_page(self, page: int, color: int) -> None:
        # The original fills with one packed byte, so a color above 15 puts
        # different nibbles on even and odd pixels.
        packed = ((color << 4) | color) & 0xFF
        even = int(packed >> 4)
        odd = int(packed & 0xF)
        base = self.page_index(page) * PAGE_SIZE
        self.mem[base:base + PAGE_SIZE:2] = bytes([even]) * (PAGE_SIZE // 2)
        self.mem[base + 1:base + PAGE_SIZE:2] = bytes([odd]) * (PAGE_SIZE // 2)

    def copy_page(self, src: int, dst: int, vscroll: int) -> None:
        if src == dst:
            return
        if src >= 0xFE or (src & 0xBF & 0x80) == 0:
            s = self.page_index(src & 0xBF if src < 0xFE else src)
            d = self.page_index(dst)
            if s != d:
                self._copy(s * PAGE_SIZE, d * PAGE_SIZE, PAGE_SIZE)
            return
        s = self.page_index(src & 3)
        d = self.page_index(dst)
        if vscroll < -199 or vscroll > 199:
            return
        rows = 200
        src_off = 0
        dst_off = 0
        if vscroll < 0:
            rows += vscroll
            src_off = -vscroll * W
        else:
            rows -= vscroll
            dst_off = vscroll * W
        self._copy(s * PAGE_SIZE + src_off, d * PAGE_SIZE + dst_off, rows * W)

    def _copy(self, src: int, dst: int, n: int) -> None:
        # A forward byte copy into its own source (a vertical scroll of a
        # page onto itself) repeats the source's first rows, where a slice
        # copy would move them; past the end a slice would grow the buffer.
        # Both cases keep the byte loop.
        if (dst <= src or dst >= src + n) and max(src, dst) + n <= len(self.mem):
            self.mem[dst:dst + n] = self.mem[src:src + n]
            return
        for i in range(n):
            self.mem[dst + i] = self.mem[src + i]

    def copy_bitmap(self, pixels: bytes) -> None:
        """Loads a background, one palette index per pixel, into page 0."""
        if len(pixels) < PAGE_SIZE:
            # A slice copy would shrink the pages instead.
            raise IndexError("a background shorter than a page")
        self.mem[:PAGE_SIZE] = pixels[:PAGE_SIZE]

    def set_palette(self, palettes: bytes, n: int) -> None:
        if n >= 32:
            return
        base = n * 32
        for i in range(16):
            c1 = int(palettes[base + i * 2])
            c2 = int(palettes[base + i * 2 + 1])
            r = _expand4(c1 & 0xF)
            g = _expand4(c2 >> 4)
            b = _expand4(c2 & 0xF)
            self.palette[i] = (r << 16) | (g << 8) | b

    def flip(self, page: int, palettes: bytes) -> None:
        """Chooses the page to show and applies a pending palette change."""
        if page != 0xFE:
            if page == 0xFF:
                t = self.front
                self.front = self.back
                self.back = t
            else:
                self.front = self.page_index(page)
        if self.palette_requested != 0xFF:
            self.set_palette(palettes, self.palette_requested)
            self.palette_requested = 0xFF

    def show(self, screen: Screen, now: int) -> None:
        screen.present(self.mem, self.front * PAGE_SIZE, self.palette, now)

    # -- text ----------------------------------------------------------------

    def use_strings(self, table: dict[int, str]) -> None:
        self.strings = table

    def string(self, string_id: int) -> str:
        """String `string_id` of the table, "" if it has none."""
        if string_id in self.strings:
            return self.strings[string_id]
        return ""

    def draw_string(self, string_id: int, x: int, y: int, color: int) -> None:
        """Draws a string of the table; `x` counts 8-pixel columns."""
        if string_id not in self.strings:
            return
        x0 = x
        text = self.strings[string_id]
        for ch in text:
            if ch == "\n":
                y += 8
                x = x0
                continue
            self._draw_char(ord(ch), x, y, color)
            x += 1

    def _draw_char(self, c: int, x: int, y: int, color: int) -> None:
        if x > 39 or y > 192:
            return
        glyph = (c - 32) * 8
        base = self.work * PAGE_SIZE + y * W + x * 8
        for j in range(8):
            row = int(FONT[glyph + j])
            at = base + j * W
            for _ in range(4):
                # Two pixels share a byte in the original, so a color above
                # 15 spills into the left pixel, as in fill_page.
                b = (int(self.mem[at]) << 4) | int(self.mem[at + 1])
                keep = 0xFF
                put = 0
                if row & 0x80:
                    put |= (color << 4) & 0xFF
                    keep &= 0x0F
                if row & 0x40:
                    put |= color & 0xFF
                    keep &= 0xF0
                row <<= 2
                b = (b & keep) | put
                self.mem[at] = int(b >> 4)
                self.mem[at + 1] = int(b & 0xF)
                at += 2

    # -- polygons ------------------------------------------------------------

    def draw_shape(self, data: bytes, pos: int, color: int, zoom: int,
                   x: int, y: int) -> None:
        """Draws the shape at `pos`: one polygon, or a group of child shapes."""
        i = int(data[pos])
        pos += 1
        if i >= 0xC0:
            if color & 0x80:
                color = i & 0x3F
            self._read_vertices(data, pos, zoom)
            self._fill_polygon(color, x, y)
        elif (i & 0x3F) == 2:
            self._draw_group(data, pos, zoom, x, y)

    def _draw_group(self, data: bytes, pos: int, zoom: int,
                    x: int, y: int) -> None:
        x = s16(x - int(data[pos]) * zoom // 64)
        y = s16(y - int(data[pos + 1]) * zoom // 64)
        children = int(data[pos + 2])
        pos += 3
        for _ in range(children + 1):
            off = be16(data, pos)
            cx = s16(x + int(data[pos + 2]) * zoom // 64)
            cy = s16(y + int(data[pos + 3]) * zoom // 64)
            pos += 4
            color = 0xFF
            if off & 0x8000:
                color = int(data[pos]) & 0x7F
                pos += 2
            self.draw_shape(data, (off & 0x7FFF) * 2, color, zoom, cx, cy)

    def _read_vertices(self, data: bytes, pos: int, zoom: int) -> None:
        self.bbw = (int(data[pos]) * zoom // 64) & 0xFFFF
        self.bbh = (int(data[pos + 1]) * zoom // 64) & 0xFFFF
        self.npoints = int(data[pos + 2])
        pos += 3
        for i in range(self.npoints):
            self.px[i] = s16(int(data[pos]) * zoom // 64)
            self.py[i] = s16(int(data[pos + 1]) * zoom // 64)
            pos += 2

    def _fill_polygon(self, color: int, x: int, y: int) -> None:
        """Scan-converts the polygon: its vertices run down the right edge
        from the first point and down the left edge from the last, so the two
        edges are stepped in 16.16 fixed point, one scanline at a time."""
        if self.bbw == 0 and self.bbh == 1 and self.npoints == 4:
            self._draw_point(color, x, y)
            return
        x1 = s16(x - self.bbw // 2)
        x2 = s16(x + self.bbw // 2)
        y1 = s16(y - self.bbh // 2)
        y2 = s16(y + self.bbh // 2)
        if x1 > 319 or x2 < 0 or y1 > 199 or y2 < 0:
            return
        line_y = y1
        i = 0
        j = self.npoints - 1
        x2 = s16(self.px[i] + x1)
        x1 = s16(self.px[j] + x1)
        i += 1
        j -= 1
        cpt1 = (int(x1) << 16) & 0xFFFFFFFF
        cpt2 = (int(x2) << 16) & 0xFFFFFFFF
        remaining = self.npoints
        while True:
            remaining -= 2
            if remaining == 0:
                break
            h = (self.py[j] - self.py[j + 1]) & 0xFFFF
            step1 = int((self.px[j] - self.px[j + 1]) * self.interp[h] * 4)
            h = (self.py[i] - self.py[i - 1]) & 0xFFFF
            step2 = int((self.px[i] - self.px[i - 1]) * self.interp[h] * 4)
            i += 1
            j -= 1
            cpt1 = (cpt1 & 0xFFFF0000) | 0x7FFF
            cpt2 = (cpt2 & 0xFFFF0000) | 0x8000
            if h == 0:
                cpt1 = (cpt1 + step1) & 0xFFFFFFFF
                cpt2 = (cpt2 + step2) & 0xFFFFFFFF
                continue
            while h != 0:
                if line_y >= 0:
                    xa = s16(int(cpt1 >> 16))
                    xb = s16(int(cpt2 >> 16))
                    if xa <= 319 and xb >= 0:
                        if xa < 0:
                            xa = 0
                        if xb > 319:
                            xb = 319
                        self._draw_span(line_y, xa, xb, color)
                cpt1 = (cpt1 + step1) & 0xFFFFFFFF
                cpt2 = (cpt2 + step2) & 0xFFFFFFFF
                line_y += 1
                if line_y > 199:
                    return
                h -= 1

    def _draw_span(self, y: int, xa: int, xb: int, color: int) -> None:
        lo = min(xa, xb)
        hi = max(xa, xb)
        row = y * W
        base = self.work * PAGE_SIZE + row
        # The caller clips the span to 0 <= lo <= hi <= 319.
        if color < COLOR_BLEND:
            self.mem[base + lo:base + hi + 1] = bytes([int(color)]) * (hi - lo + 1)
        elif color == COLOR_BLEND:
            for x in range(base + lo, base + hi + 1):
                self.mem[x] = self.mem[x] | 8
        else:
            self.mem[base + lo:base + hi + 1] = self.mem[row + lo:row + hi + 1]

    def _draw_point(self, color: int, x: int, y: int) -> None:
        if x < 0 or x > 319 or y < 0 or y > 199:
            return
        off = y * W + x
        at = self.work * PAGE_SIZE + off
        if color == COLOR_BLEND:
            self.mem[at] = self.mem[at] | 8
        elif color == COLOR_BACKGROUND:
            self.mem[at] = self.mem[off]
        else:
            # The packed-byte write again: see fill_page.
            packed = ((color << 4) | color) & 0xFF
            self.mem[at] = int(packed & 0xF if x & 1 else packed >> 4)


def _expand4(v: int) -> int:
    """Widens a 4-bit channel to 8 bits the way the reference does."""
    return ((v << 2) | (v >> 2)) << 2
