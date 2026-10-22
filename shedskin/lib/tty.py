# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

import termios

IFLAG = 0
OFLAG = 1
CFLAG = 2
LFLAG = 3
ISPEED = 4
OSPEED = 5
CC = 6

def cfmakeraw(mode):
    pass

def cfmakecbreak(mode):
    pass

def setraw(fd, when=-2):  # -2: termios.TCSAFLUSH, see tty.cpp
    return termios.tcgetattr(fd)

def setcbreak(fd, when=-2):
    return termios.tcgetattr(fd)
