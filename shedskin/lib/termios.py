# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

# tcgetattr() returns a list holding six ints and, at index 6 (tty.CC), a list
# of control characters. as shedskin lists are homogeneous, these are modeled
# by two list-like classes: tcattrs, and cclist (holding 1-byte bytes objects).
# indexing a tcattrs with literal 6, CC or tty.CC is redirected to __getcc__
# (see infer.py), so the cclist type does not mix with the int elements.

class error(Exception):
    pass

class cclist(pyseq):
    def __init__(self):
        self.unit = b''
    def __getitem__(self, i):
        return self.unit
    def __setitem__(self, i, v):  # int or bytes
        pass
    def __len__(self):
        return 1
    def __iter__(self):
        return __iter(self.unit)
    def __eq__(self, other):
        return True
    def __ne__(self, other):
        return True
    def __repr__(self):
        return ''
    def __copy__(self):
        return self
    def __deepcopy__(self):
        return self

class tcattrs:
    def __init__(self):
        self.cc = cclist()
    def __getitem__(self, i):
        return 1
    def __getcc__(self, i):
        return self.cc
    def __setitem__(self, i, v):  # int or cclist
        pass
    def __len__(self):
        return 7
    def __eq__(self, other):
        return True
    def __ne__(self, other):
        return True
    def __repr__(self):
        return ''
    def __copy__(self):
        return self
    def __deepcopy__(self):
        return self

def tcgetattr(fd):
    return tcattrs()

def tcsetattr(fd, when, attributes):
    pass

TCSANOW = 0
TCSADRAIN = 1
TCSAFLUSH = 2
NCCS = 32
VMIN = 6
VTIME = 5
ECHO = 8
ICANON = 2
