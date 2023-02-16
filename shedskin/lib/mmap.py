# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)


PAGESIZE = 0x1000
ALLOCATIONGRANULARITY = 0x10000

MAP_SHARED, MAP_PRIVATE, MAP_ANON, MAP_ANONYMOUS = (1, 2, 32, 32)
PROT_READ, PROT_WRITE, PROT_EXEC = (1, 2, 4)
ACCESS_READ, ACCESS_WRITE, ACCESS_COPY = (1, 2, 3)

class mmap:
    def __init__(self, fileno, length, flags=MAP_SHARED, prot=PROT_READ | PROT_WRITE, access=0, offset=0):
        pass

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

    def size(self):
        return 0

    def tell(self):
        return 0

    def write(self, string):
        pass

    def write_byte(self, string):
        pass

    def __contains(self, string):
        return False

    def __iter__(self):
        return __mmapiter()

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

class __mmapiter:
    def __next__(self):
        return b''
