# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

# like CPython, tty re-exports everything from termios (see tty.hpp)
from termios import *

__void = 0

# indices for termios list
IFLAG = 0
OFLAG = 1
CFLAG = 2
LFLAG = 3
ISPEED = 4
OSPEED = 5
CC = 6

def cfmakeraw(mode):
    mode[0] = 1
    mode.__getcc__(6)[0] = 1

def cfmakecbreak(mode):
    mode[0] = 1
    mode.__getcc__(6)[0] = 1

# when defaults to TCSAFLUSH
def setraw(fd, when=__void):
    fd.fileno()
    return tcgetattr(fd)

def setcbreak(fd, when=__void):
    fd.fileno()
    return tcgetattr(fd)
