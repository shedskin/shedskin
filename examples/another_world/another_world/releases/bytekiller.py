# ByteKiller, the packer the DOS and Amiga banks store most resources with.
from __future__ import annotations

from ..binary import be32


class _BitReader:
    """ByteKiller's input: 32-bit words read from the end of the packed data
    towards its start, each shifted out low bit first. A word's highest set
    bit is a sentinel marking where its payload ends."""

    # data: bytes
    # pos: int
    # chk: int
    # crc: int

    def __init__(self, data: bytes, pos: int) -> None:
        self.data = data
        self.pos = pos
        self.chk = 0
        self.crc = 0

    def word(self) -> int:
        v = be32(self.data, self.pos)
        self.pos -= 4
        return v

    def bit(self) -> int:
        b = int(self.chk & 1)
        self.chk >>= 1
        if self.chk == 0:
            # A fresh word: its top bit is shifted in as 1 so the word runs
            # dry exactly when its payload does.
            self.chk = self.word()
            self.crc ^= self.chk
            b = int(self.chk & 1)
            self.chk = (self.chk >> 1) | 0x80000000
        return b

    def bits(self, n: int) -> int:
        v = 0
        for _ in range(n):
            v = (v << 1) | self.bit()
        return v


def unpack(packed: bytes) -> bytes:
    """Decompress one ByteKiller stream. The output is written back to front;
    a back-reference copies from bytes already written above the cursor."""
    r = _BitReader(packed, len(packed) - 4)
    size = int(r.word())
    out = bytearray(size)
    r.crc = r.word()
    r.chk = r.word()
    r.crc ^= r.chk
    dst = size - 1
    remaining = size
    while remaining > 0:
        literal_count = 0
        copy_count = 0
        copy_bits = 0
        if r.bit() == 0:
            if r.bit() == 0:
                literal_count = r.bits(3) + 1
            else:
                copy_count = 2
                copy_bits = 8
        else:
            c = r.bits(2)
            if c == 3:
                literal_count = r.bits(8) + 9
            elif c < 2:
                copy_count = c + 3
                copy_bits = c + 9
            else:
                copy_count = r.bits(8) + 1
                copy_bits = 12
        if literal_count > 0:
            remaining -= literal_count
            for _ in range(literal_count):
                out[dst] = int(r.bits(8))
                dst -= 1
        else:
            distance = r.bits(copy_bits)
            remaining -= copy_count
            for _ in range(copy_count):
                out[dst] = out[dst + distance]
                dst -= 1
    if r.crc != 0:
        raise ValueError("ByteKiller checksum mismatch")
    return bytes(out)
