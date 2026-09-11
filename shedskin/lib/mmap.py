# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)


PAGESIZE = 0x1000
ALLOCATIONGRANULARITY = 0x10000

MAP_SHARED, MAP_PRIVATE, MAP_ANON, MAP_ANONYMOUS = (1, 2, 32, 32)
PROT_READ, PROT_WRITE, PROT_EXEC = (1, 2, 4)
ACCESS_DEFAULT, ACCESS_READ, ACCESS_WRITE, ACCESS_COPY = (0, 1, 2, 3)

# Linux-only flags for mmap()'s `flags` argument; -1 on platforms that
# don't support them (e.g. Windows, macOS).
MAP_DENYWRITE = 2048
MAP_EXECUTABLE = 4096
MAP_POPULATE = 32768
MAP_STACK = 131072

# madvise() advice constants. Only MADV_NORMAL/RANDOM/SEQUENTIAL/WILLNEED/
# DONTNEED are portable; the others are Linux-, BSD- or macOS-only. Unlike
# CPython (which simply omits the missing ones), they are always defined
# here and are -1 on platforms that lack them, so that passing one raises
# OSError instead of failing to compile.
MADV_NORMAL = 0
MADV_RANDOM = 1
MADV_SEQUENTIAL = 2
MADV_WILLNEED = 3
MADV_DONTNEED = 4
MADV_FREE = 8
MADV_REMOVE = 9
MADV_DONTFORK = 10
MADV_DOFORK = 11
MADV_MERGEABLE = 12
MADV_UNMERGEABLE = 13
MADV_HUGEPAGE = 14
MADV_NOHUGEPAGE = 15
MADV_DONTDUMP = 16
MADV_DODUMP = 17
MADV_HWPOISON = 100
MADV_SOFT_OFFLINE = 101

# BSD-only
MADV_NOSYNC = -1
MADV_AUTOSYNC = -1
MADV_NOCORE = -1
MADV_CORE = -1
MADV_PROTECT = -1

# macOS-only
MADV_FREE_REUSABLE = -1
MADV_FREE_REUSE = -1

class mmap(pyiter):
    def __init__(self, fileno, length, flags=MAP_SHARED, prot=PROT_READ | PROT_WRITE, access=0, offset=0):
        self.closed = False

    def __win32__init__(self, fileno, length, tagname='', access=0, offset=0):
        pass

    def close(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def flush(self, offset=0, size=-1):
        return 0

    def madvise(self, option, start=0, length=-1):
        pass

    def find(self, string, start=-1, end=-1):
        return -1

    def move(self, destination, source, count):
        pass

    def read(self, size):
        return b''

    def read_byte(self):
        return 1

    def readline(self):
        return b''

    def resize(self, newsize):
        pass

    def rfind(self, string, start=-1, end=-1):
        return -1

    def seek(self, offset, whence=0):
        pass

    def seekable(self):
        return True

    def set_name(self, name):
        pass

    def size(self):
        return 0

    def tell(self):
        return 0

    def write(self, string):
        pass

    def write_byte(self, string):
        pass

    def __contains__(self, string):
        return False

    def __iter__(self):
        return __iter(b'')

    def __len__(self):
        return 0

    def __getitem__(self, index):
        return 1

    def __setitem__(self, index, value):
        pass

    def __slice__(self, kind, lower, upper, step=1):
        return b''

    def __setslice__(self, kind, lower, upper, step, sequence):
        pass
