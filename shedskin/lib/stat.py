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
S_IFDOOR = 0
S_IFPORT = 0
S_IFWHT  = 0

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

# doors (solaris), event ports (solaris) and whiteouts (bsd/macos) don't
# exist on every platform; cpython defines the predicates everywhere and
# has them return False where the file type is unknown, so these are
# always available even though they can only ever be True on the
# platforms that model the type
def S_ISDOOR(mode):
    return False

def S_ISPORT(mode):
    return False

def S_ISWHT(mode):
    return False

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

# Names for file flags (os.chflags() / stat_result.st_flags)
UF_SETTABLE   = 0x0000ffff  # mask of owner changeable flags
UF_NODUMP     = 0x00000001  # do not dump file
UF_IMMUTABLE  = 0x00000002  # file may not be changed
UF_APPEND     = 0x00000004  # file may only be appended to
UF_OPAQUE     = 0x00000008  # directory is opaque when viewed through a union stack
UF_NOUNLINK   = 0x00000010  # file may not be renamed or deleted
UF_COMPRESSED = 0x00000020  # macOS: file is hfs-compressed
UF_TRACKED    = 0x00000040  # macOS: used for handling document IDs
UF_DATAVAULT  = 0x00000080  # macOS: entitlement needed for I/O
UF_HIDDEN     = 0x00008000  # macOS: file should not be displayed
SF_SETTABLE   = 0xffff0000  # mask of super user changeable flags
SF_ARCHIVED   = 0x00010000  # file may be archived
SF_IMMUTABLE  = 0x00020000  # file may not be changed
SF_APPEND     = 0x00040000  # file may only be appended to
SF_RESTRICTED = 0x00080000  # macOS: entitlement needed for writing
SF_NOUNLINK   = 0x00100000  # file may not be renamed or deleted
SF_SNAPSHOT   = 0x00200000  # file is a snapshot file
SF_FIRMLINK   = 0x00800000  # macOS: file is a firmlink
SF_DATALESS   = 0x40000000  # macOS: file is a dataless object

# Windows file attributes (stat_result.st_file_attributes)
FILE_ATTRIBUTE_ARCHIVE = 32
FILE_ATTRIBUTE_COMPRESSED = 2048
FILE_ATTRIBUTE_DEVICE = 64
FILE_ATTRIBUTE_DIRECTORY = 16
FILE_ATTRIBUTE_ENCRYPTED = 16384
FILE_ATTRIBUTE_HIDDEN = 2
FILE_ATTRIBUTE_INTEGRITY_STREAM = 32768
FILE_ATTRIBUTE_NORMAL = 128
FILE_ATTRIBUTE_NOT_CONTENT_INDEXED = 8192
FILE_ATTRIBUTE_NO_SCRUB_DATA = 131072
FILE_ATTRIBUTE_OFFLINE = 4096
FILE_ATTRIBUTE_READONLY = 1
FILE_ATTRIBUTE_REPARSE_POINT = 1024
FILE_ATTRIBUTE_SPARSE_FILE = 512
FILE_ATTRIBUTE_SYSTEM = 4
FILE_ATTRIBUTE_TEMPORARY = 256
FILE_ATTRIBUTE_VIRTUAL = 65536

# Linux extended attributes (os.statx()'s stx_attributes)
STATX_ATTR_COMPRESSED = 0x00000004
STATX_ATTR_IMMUTABLE = 0x00000010
STATX_ATTR_APPEND = 0x00000020
STATX_ATTR_NODUMP = 0x00000040
STATX_ATTR_ENCRYPTED = 0x00000800
STATX_ATTR_AUTOMOUNT = 0x00001000
STATX_ATTR_MOUNT_ROOT = 0x00002000
STATX_ATTR_VERITY = 0x00100000
STATX_ATTR_DAX = 0x00200000
STATX_ATTR_WRITE_ATOMIC = 0x00400000

def filemode(mode):
    return ''
