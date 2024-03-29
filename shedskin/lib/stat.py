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
    return mode & 0o7777

def S_IFMT(mode):
    return mode & 0o170000

# Constants used as S_IFMT() for various file types
# (not all are implemented on all systems)

S_IFDIR  = 0o040000
S_IFCHR  = 0o020000
S_IFBLK  = 0o060000
S_IFREG  = 0o100000
S_IFIFO  = 0o010000
S_IFLNK  = 0o120000
S_IFSOCK = 0o140000

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

S_ISUID = 0o4000
S_ISGID = 0o2000
S_ENFMT = S_ISGID
S_ISVTX = 0o1000
S_IREAD = 0o0400
S_IWRITE = 0o0200
S_IEXEC = 0o0100
S_IRWXU = 0o0700
S_IRUSR = 0o0400
S_IWUSR = 0o0200
S_IXUSR = 0o0100
S_IRWXG = 0o0070
S_IRGRP = 0o0040
S_IWGRP = 0o0020
S_IXGRP = 0o0010
S_IRWXO = 0o0007
S_IROTH = 0o0004
S_IWOTH = 0o0002
S_IXOTH = 0o0001

