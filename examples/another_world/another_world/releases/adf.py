# Files on an Amiga floppy image (.adf): the root directory of an AmigaDOS
# disk, OFS or FFS, which is where the Amiga release keeps its banks.
from __future__ import annotations

BLOCK = 512
ROOT_BLOCK = 880
HASH_SIZE = 72
OFS_DATA = BLOCK - 24  # an OFS data block after its header
ST_FILE = 0xFFFFFFFD  # -3 as an unsigned long


def _be32(data: bytes, pos: int) -> int:
    """An unsigned big-endian long."""
    return (int(data[pos]) << 24) | (int(data[pos + 1]) << 16) \
        | (int(data[pos + 2]) << 8) | int(data[pos + 3])


def is_amigados(path: str) -> bool:
    """Whether the file starts like an AmigaDOS disk image."""
    with open(path, "rb") as f:
        head = f.read(4)
    return len(head) == 4 and head[0:3] == b"DOS"


class Disk:
    # path: str
    # image: bytes
    # blocks: int
    # Fast File System: data blocks carry no header.
    # ffs: bool

    def __init__(self, path: str) -> None:
        with open(path, "rb") as f:
            image = f.read()
        self.path = path
        self.image = image
        self.blocks = len(self.image) // BLOCK
        if self.blocks <= ROOT_BLOCK or self.image[0:3] != b"DOS":
            raise ValueError(f"{path}: not an AmigaDOS disk image")
        self.ffs = (int(self.image[3]) & 1) != 0

    def names(self) -> list[str]:
        """The names of the files in the root directory."""
        found = []
        for at in self._files():
            found.append(self._name(at))
        return found

    def read(self, name: str) -> bytes:
        """The contents of a root directory file, found case-insensitively
        as AmigaDOS does."""
        want = name.lower()
        for at in self._files():
            if self._name(at).lower() == want:
                return self._contents(at)
        raise FileNotFoundError(f"{self.path}: {name} is not on the disk")

    def _corrupt(self) -> ValueError:
        return ValueError(f"{self.path}: the disk image is damaged")

    def _block(self, pos: int) -> int:
        """A block number stored as a long: the byte offset of that block,
        or 0 for none."""
        n = _be32(self.image, pos)
        if n >= self.blocks:
            raise self._corrupt()
        return int(n) * BLOCK

    def _files(self) -> list[int]:
        """The header blocks of the root directory's files, walking each
        hash chain; a chain longer than the disk means a loop."""
        found = []
        root = ROOT_BLOCK * BLOCK
        for slot in range(HASH_SIZE):
            at = self._block(root + 24 + slot * 4)
            steps = 0
            while at != 0:
                steps += 1
                if steps > self.blocks:
                    raise self._corrupt()
                if _be32(self.image, at + BLOCK - 4) == ST_FILE:
                    found.append(at)
                at = self._block(at + BLOCK - 16)
        return found

    def _name(self, at: int) -> str:
        n = min(int(self.image[at + BLOCK - 80]), 30)
        chars = []
        for i in range(n):
            chars.append(chr(int(self.image[at + BLOCK - 79 + i])))
        return "".join(chars)

    def _contents(self, at: int) -> bytes:
        size = _be32(self.image, at + BLOCK - 188)
        if size > len(self.image):
            raise self._corrupt()
        out = bytearray()
        # The header block and its extension blocks list the data blocks,
        # last slot first.
        header = at
        steps = 0
        while True:
            steps += 1
            count = _be32(self.image, header + 8)
            if count > HASH_SIZE or steps > self.blocks:
                raise self._corrupt()
            for k in range(int(count)):
                data = self._block(header + 24 + (HASH_SIZE - 1 - k) * 4)
                if self.ffs:
                    n = min(BLOCK, int(size) - len(out))
                    for i in range(n):
                        out.append(self.image[data + i])
                else:
                    length = _be32(self.image, data + 12)
                    if length > OFS_DATA:
                        raise self._corrupt()
                    for i in range(int(length)):
                        out.append(self.image[data + 24 + i])
            header = self._block(header + BLOCK - 8)
            if header == 0:
                break
        if len(out) != size:
            raise self._corrupt()
        return bytes(out)
