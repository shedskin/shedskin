# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)

# copied from pypy:
# https://codespeak.net/viewvc/pypy/dist/lib-python/2.4.1/stat.py?revision=16842&view=markup

"""Constants/functions for interpreting results of os.stat() and os.lstat().

Suggested usage: from stat import *
"""

# XXX Strictly spoken, this module may have to be adapted for each POSIX
# implementation; in practice, however, the numeric constants used by
# stat() are almost universal (even for stat() emulations on non-UNIX
# systems like MS-DOS).

# Indices for stat struct members in tuple returned by os.stat()

ST_MODE  = 0
ST_INO   = 1
ST_DEV   = 2
ST_NLINK = 3
ST_UID   = 4
ST_GID   = 5
ST_SIZE  = 6
ST_ATIME = 7
ST_MTIME = 8
ST_CTIME = 9

# Extract bits from the mode

def S_IMODE(mode):
    return mode & 0O7777

def S_IFMT(mode):
    return mode & 0O170000

# Constants used as S_IFMT() for various file types
# (not all are implemented on all systems)

S_IFDIR  = 0O040000
S_IFCHR  = 0O020000
S_IFBLK  = 0O060000
S_IFREG  = 0O100000
S_IFIFO  = 0O010000
S_IFLNK  = 0O120000
S_IFSOCK = 0O140000

# Functions to test for each file type

def S_ISDIR(mode):
    return S_IFMT(mode) == S_IFDIR

def S_ISCHR(mode):
    return S_IFMT(mode) == S_IFCHR

def S_ISBLK(mode):
    return S_IFMT(mode) == S_IFBLK

def S_ISREG(mode):
    return S_IFMT(mode) == S_IFREG

def S_ISFIFO(mode):
    return S_IFMT(mode) == S_IFIFO

def S_ISLNK(mode):
    return S_IFMT(mode) == S_IFLNK

def S_ISSOCK(mode):
    return S_IFMT(mode) == S_IFSOCK

# Names for permission bits

S_ISUID = 0O4000
S_ISGID = 0O2000
S_ENFMT = S_ISGID
S_ISVTX = 0O1000
S_IREAD = 0O0400
S_IWRITE = 0O0200
S_IEXEC = 0O0100
S_IRWXU = 0O0700
S_IRUSR = 0O0400
S_IWUSR = 0O0200
S_IXUSR = 0O0100
S_IRWXG = 0O0070
S_IRGRP = 0O0040
S_IWGRP = 0O0020
S_IXGRP = 0O0010
S_IRWXO = 0O0007
S_IROTH = 0O0004
S_IWOTH = 0O0002
S_IXOTH = 0O0001

