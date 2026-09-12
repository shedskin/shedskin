/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "stat.hpp"

#include <sys/types.h>
#include <sys/stat.h>

#if defined( _MSC_VER )
    #if !defined(S_ISREG) && defined(S_IFMT) && defined(S_IFREG)
      #define S_ISREG(m) (((m) & S_IFMT) == S_IFREG)
    #endif
    #if !defined(S_ISDIR) && defined(S_IFMT) && defined(S_IFDIR)
      #define S_ISDIR(m) (((m) & S_IFMT) == S_IFDIR)
    #endif

    #include <stdlib.h>
    #include <io.h>
#else
    #include <unistd.h>
#endif


/* Platform fallbacks, mirroring cpython's Modules/_stat.c: where the
   system headers model a file type or file flag we take the system
   value, otherwise we fall back to the fixed value cpython's stat.py
   hardcodes. That way stat.S_IFWHT is the real whiteout bit on macos
   and 0 on linux/windows, exactly as in interpreted python, while the
   names are always defined. */

/* file types not modelled on every platform */
#ifndef S_IFDOOR
#  define S_IFDOOR 0
#endif
#ifndef S_IFPORT
#  define S_IFPORT 0
#endif
#ifndef S_IFWHT
#  define S_IFWHT 0
#endif

/* ..and the matching predicates; these can only ever be true on a
   platform that models the type at all */
#ifndef S_ISDOOR
#  define S_ISDOOR(mode) 0
#endif
#ifndef S_ISPORT
#  define S_ISPORT(mode) 0
#endif
#ifndef S_ISWHT
#  define S_ISWHT(mode) 0
#endif

/* BSD-style file flags (os.chflags, stat_result.st_flags) */
#ifndef UF_SETTABLE
#  define UF_SETTABLE 0x0000ffff
#endif
#ifndef UF_NODUMP
#  define UF_NODUMP 0x00000001
#endif
#ifndef UF_IMMUTABLE
#  define UF_IMMUTABLE 0x00000002
#endif
#ifndef UF_APPEND
#  define UF_APPEND 0x00000004
#endif
#ifndef UF_OPAQUE
#  define UF_OPAQUE 0x00000008
#endif
#ifndef UF_NOUNLINK
#  define UF_NOUNLINK 0x00000010
#endif
#ifndef UF_COMPRESSED
#  define UF_COMPRESSED 0x00000020
#endif
#ifndef UF_TRACKED
#  define UF_TRACKED 0x00000040
#endif
#ifndef UF_DATAVAULT
#  define UF_DATAVAULT 0x00000080
#endif
#ifndef UF_HIDDEN
#  define UF_HIDDEN 0x00008000
#endif
#ifndef SF_SETTABLE
#  define SF_SETTABLE 0xffff0000
#endif
#ifndef SF_ARCHIVED
#  define SF_ARCHIVED 0x00010000
#endif
#ifndef SF_IMMUTABLE
#  define SF_IMMUTABLE 0x00020000
#endif
#ifndef SF_APPEND
#  define SF_APPEND 0x00040000
#endif
#ifndef SF_RESTRICTED
#  define SF_RESTRICTED 0x00080000
#endif
#ifndef SF_NOUNLINK
#  define SF_NOUNLINK 0x00100000
#endif
#ifndef SF_SNAPSHOT
#  define SF_SNAPSHOT 0x00200000
#endif
#ifndef SF_FIRMLINK
#  define SF_FIRMLINK 0x00800000
#endif
#ifndef SF_DATALESS
#  define SF_DATALESS 0x40000000
#endif

/* older macos versions define SF_SUPPORTED differently; cpython
   normalizes SF_SETTABLE there, so do the same */
#if defined(__APPLE__) && !defined(SF_SUPPORTED)
#  undef SF_SETTABLE
#  define SF_SETTABLE 0x3fff0000
#endif

namespace __stat__ {

__ss_int __ss_ST_MODE, __ss_ST_INO, __ss_ST_DEV, __ss_ST_NLINK, __ss_ST_UID, __ss_ST_GID, __ss_ST_SIZE, __ss_ST_ATIME, __ss_ST_MTIME, __ss_ST_CTIME, __ss_S_IFDIR, __ss_S_IFCHR, __ss_S_IFBLK, __ss_S_IFREG, __ss_S_IFIFO, __ss_S_IFLNK, __ss_S_IFSOCK, __ss_S_ISUID, __ss_S_ISGID, __ss_S_ENFMT, __ss_S_ISVTX, __ss_S_IREAD, __ss_S_IWRITE, __ss_S_IEXEC, __ss_S_IRWXU, __ss_S_IRUSR, __ss_S_IWUSR, __ss_S_IXUSR, __ss_S_IRWXG, __ss_S_IRGRP, __ss_S_IWGRP, __ss_S_IXGRP, __ss_S_IRWXO, __ss_S_IROTH, __ss_S_IWOTH, __ss_S_IXOTH;
__ss_int __ss_S_IFDOOR;
__ss_int __ss_S_IFPORT;
__ss_int __ss_S_IFWHT;
__ss_int __ss_UF_SETTABLE;
__ss_int __ss_UF_NODUMP;
__ss_int __ss_UF_IMMUTABLE;
__ss_int __ss_UF_APPEND;
__ss_int __ss_UF_OPAQUE;
__ss_int __ss_UF_NOUNLINK;
__ss_int __ss_UF_COMPRESSED;
__ss_int __ss_UF_TRACKED;
__ss_int __ss_UF_DATAVAULT;
__ss_int __ss_UF_HIDDEN;
__ss_int __ss_SF_SETTABLE;
__ss_int __ss_SF_ARCHIVED;
__ss_int __ss_SF_IMMUTABLE;
__ss_int __ss_SF_APPEND;
__ss_int __ss_SF_RESTRICTED;
__ss_int __ss_SF_NOUNLINK;
__ss_int __ss_SF_SNAPSHOT;
__ss_int __ss_SF_FIRMLINK;
__ss_int __ss_SF_DATALESS;
__ss_int __ss_FILE_ATTRIBUTE_ARCHIVE;
__ss_int __ss_FILE_ATTRIBUTE_COMPRESSED;
__ss_int __ss_FILE_ATTRIBUTE_DEVICE;
__ss_int __ss_FILE_ATTRIBUTE_DIRECTORY;
__ss_int __ss_FILE_ATTRIBUTE_ENCRYPTED;
__ss_int __ss_FILE_ATTRIBUTE_HIDDEN;
__ss_int __ss_FILE_ATTRIBUTE_INTEGRITY_STREAM;
__ss_int __ss_FILE_ATTRIBUTE_NORMAL;
__ss_int __ss_FILE_ATTRIBUTE_NOT_CONTENT_INDEXED;
__ss_int __ss_FILE_ATTRIBUTE_NO_SCRUB_DATA;
__ss_int __ss_FILE_ATTRIBUTE_OFFLINE;
__ss_int __ss_FILE_ATTRIBUTE_READONLY;
__ss_int __ss_FILE_ATTRIBUTE_REPARSE_POINT;
__ss_int __ss_FILE_ATTRIBUTE_SPARSE_FILE;
__ss_int __ss_FILE_ATTRIBUTE_SYSTEM;
__ss_int __ss_FILE_ATTRIBUTE_TEMPORARY;
__ss_int __ss_FILE_ATTRIBUTE_VIRTUAL;
__ss_int __ss_STATX_ATTR_COMPRESSED;
__ss_int __ss_STATX_ATTR_IMMUTABLE;
__ss_int __ss_STATX_ATTR_APPEND;
__ss_int __ss_STATX_ATTR_NODUMP;
__ss_int __ss_STATX_ATTR_ENCRYPTED;
__ss_int __ss_STATX_ATTR_AUTOMOUNT;
__ss_int __ss_STATX_ATTR_MOUNT_ROOT;
__ss_int __ss_STATX_ATTR_VERITY;
__ss_int __ss_STATX_ATTR_DAX;
__ss_int __ss_STATX_ATTR_WRITE_ATOMIC;

void __init() {
   __ss_ST_MODE = 0; /* XXX */
   __ss_ST_INO = 1;
   __ss_ST_DEV = 2;
   __ss_ST_NLINK = 3;
   __ss_ST_UID = 4;
   __ss_ST_GID = 5;
   __ss_ST_SIZE = 6;
   __ss_ST_ATIME = 7;
   __ss_ST_MTIME = 8;
   __ss_ST_CTIME = 9;

   __ss_S_IFDIR = S_IFDIR;
   __ss_S_IFCHR = S_IFCHR;
   __ss_S_IFREG = S_IFREG;
   __ss_S_IREAD = S_IREAD;
   __ss_S_IWRITE = S_IWRITE;
   __ss_S_IEXEC = S_IEXEC;

   /* The constants below have no corresponding macro in MSVC's
      <sys/stat.h> (file-type bits it doesn't model: IFIFO/IFBLK/
      IFLNK/IFSOCK; permission bits it also omits: ISUID/ISGID/ISVTX
      and the group/other IRWX* families) and used to be left at 0 on
      Windows as a result. They're assigned the fixed POSIX values
      that stat.py itself hardcodes instead of system macros, so
      behavior matches interpreted Python on every platform. */
   __ss_S_IFIFO = 0010000;
   __ss_S_IFBLK = 0060000;
   __ss_S_IFLNK = 0120000;
   __ss_S_IFSOCK = 0140000;
   __ss_S_IRWXU = 0700;
   __ss_S_IRUSR = 0400;
   __ss_S_IWUSR = 0200;
   __ss_S_IXUSR = 0100;
   __ss_S_ISUID = 04000;
   __ss_S_ISGID = 02000;
   __ss_S_ENFMT = __ss_S_ISGID;
   __ss_S_ISVTX = 01000;
   __ss_S_IRWXG = 0070;
   __ss_S_IRGRP = 0040;
   __ss_S_IWGRP = 0020;
   __ss_S_IXGRP = 0010;
   __ss_S_IRWXO = 0007;
   __ss_S_IROTH = 0004;
   __ss_S_IWOTH = 0002;
   __ss_S_IXOTH = 0001;

   /* file types the platform may or may not model (0 where it doesn't) */
   __ss_S_IFDOOR = S_IFDOOR;
   __ss_S_IFPORT = S_IFPORT;
   __ss_S_IFWHT = S_IFWHT;

   /* file flags; system values where available, cpython's fixed
      values otherwise. cast through unsigned so SF_SETTABLE stays
      positive rather than sign-extending. */
   __ss_UF_SETTABLE = (__ss_int)(unsigned int)UF_SETTABLE;
   __ss_UF_NODUMP = (__ss_int)(unsigned int)UF_NODUMP;
   __ss_UF_IMMUTABLE = (__ss_int)(unsigned int)UF_IMMUTABLE;
   __ss_UF_APPEND = (__ss_int)(unsigned int)UF_APPEND;
   __ss_UF_OPAQUE = (__ss_int)(unsigned int)UF_OPAQUE;
   __ss_UF_NOUNLINK = (__ss_int)(unsigned int)UF_NOUNLINK;
   __ss_UF_COMPRESSED = (__ss_int)(unsigned int)UF_COMPRESSED;
   __ss_UF_TRACKED = (__ss_int)(unsigned int)UF_TRACKED;
   __ss_UF_DATAVAULT = (__ss_int)(unsigned int)UF_DATAVAULT;
   __ss_UF_HIDDEN = (__ss_int)(unsigned int)UF_HIDDEN;
   __ss_SF_SETTABLE = (__ss_int)(unsigned int)SF_SETTABLE;
   __ss_SF_ARCHIVED = (__ss_int)(unsigned int)SF_ARCHIVED;
   __ss_SF_IMMUTABLE = (__ss_int)(unsigned int)SF_IMMUTABLE;
   __ss_SF_APPEND = (__ss_int)(unsigned int)SF_APPEND;
   __ss_SF_RESTRICTED = (__ss_int)(unsigned int)SF_RESTRICTED;
   __ss_SF_NOUNLINK = (__ss_int)(unsigned int)SF_NOUNLINK;
   __ss_SF_SNAPSHOT = (__ss_int)(unsigned int)SF_SNAPSHOT;
   __ss_SF_FIRMLINK = (__ss_int)(unsigned int)SF_FIRMLINK;
   __ss_SF_DATALESS = (__ss_int)(unsigned int)SF_DATALESS;

   /* windows st_file_attributes bits; these have fixed win32 values,
      and cpython's stat.py hardcodes the same numbers on every
      platform, so no system macro is consulted */
   __ss_FILE_ATTRIBUTE_ARCHIVE = 32;
   __ss_FILE_ATTRIBUTE_COMPRESSED = 2048;
   __ss_FILE_ATTRIBUTE_DEVICE = 64;
   __ss_FILE_ATTRIBUTE_DIRECTORY = 16;
   __ss_FILE_ATTRIBUTE_ENCRYPTED = 16384;
   __ss_FILE_ATTRIBUTE_HIDDEN = 2;
   __ss_FILE_ATTRIBUTE_INTEGRITY_STREAM = 32768;
   __ss_FILE_ATTRIBUTE_NORMAL = 128;
   __ss_FILE_ATTRIBUTE_NOT_CONTENT_INDEXED = 8192;
   __ss_FILE_ATTRIBUTE_NO_SCRUB_DATA = 131072;
   __ss_FILE_ATTRIBUTE_OFFLINE = 4096;
   __ss_FILE_ATTRIBUTE_READONLY = 1;
   __ss_FILE_ATTRIBUTE_REPARSE_POINT = 1024;
   __ss_FILE_ATTRIBUTE_SPARSE_FILE = 512;
   __ss_FILE_ATTRIBUTE_SYSTEM = 4;
   __ss_FILE_ATTRIBUTE_TEMPORARY = 256;
   __ss_FILE_ATTRIBUTE_VIRTUAL = 65536;

   /* linux statx attribute bits, likewise fixed in cpython's stat.py */
   __ss_STATX_ATTR_COMPRESSED = 0x00000004;
   __ss_STATX_ATTR_IMMUTABLE = 0x00000010;
   __ss_STATX_ATTR_APPEND = 0x00000020;
   __ss_STATX_ATTR_NODUMP = 0x00000040;
   __ss_STATX_ATTR_ENCRYPTED = 0x00000800;
   __ss_STATX_ATTR_AUTOMOUNT = 0x00001000;
   __ss_STATX_ATTR_MOUNT_ROOT = 0x00002000;
   __ss_STATX_ATTR_VERITY = 0x00100000;
   __ss_STATX_ATTR_DAX = 0x00200000;
   __ss_STATX_ATTR_WRITE_ATOMIC = 0x00400000;
}

__ss_bool __ss_S_ISDIR(__ss_int mode) {

    return __mbool(S_ISDIR(mode));
}

__ss_bool __ss_S_ISREG(__ss_int mode) {

    return __mbool(S_ISREG(mode));
}

/* S_IMODE/S_IFMT operate on literal bitmask constants only, with no
   dependency on the POSIX macros that are missing from MSVC's
   <sys/stat.h>, so they are compiled unconditionally. */
__ss_int __ss_S_IMODE(__ss_int mode) {
    return (mode&4095); /* XXX */
}

__ss_int __ss_S_IFMT(__ss_int mode) {
    return (mode&61440); /* XXX */
}

/* S_ISCHR/S_ISBLK/S_ISFIFO/S_ISLNK/S_ISSOCK used to be guarded out on
   MSVC (whose <sys/stat.h> defines neither the S_IS.. macros nor, for
   S_ISBLK/ISFIFO/ISLNK/ISSOCK, the underlying S_IF.. bits), which left
   them missing entirely rather than just wrong. They're implemented
   here against the same fixed POSIX mode-bit values as __ss_S_IFMT
   above and stat.py's own constants, so they compile and behave
   identically on every platform. */
__ss_bool __ss_S_ISCHR(__ss_int mode) {
    return __mbool((mode & 0170000) == 0020000);
}

__ss_bool __ss_S_ISBLK(__ss_int mode) {
    return __mbool((mode & 0170000) == 0060000);
}

__ss_bool __ss_S_ISFIFO(__ss_int mode) {
    return __mbool((mode & 0170000) == 0010000);
}

__ss_bool __ss_S_ISLNK(__ss_int mode) {
    return __mbool((mode & 0170000) == 0120000);
}

__ss_bool __ss_S_ISSOCK(__ss_int mode) {
    return __mbool((mode & 0170000) == 0140000);
}

/* S_ISDOOR/S_ISPORT/S_ISWHT go through the system macros where they
   exist (solaris doors and event ports, bsd/macos whiteouts) and are
   constant-false everywhere else, matching cpython on each platform. */
__ss_bool __ss_S_ISDOOR(__ss_int mode) {
    (void)mode; /* unused where the platform has no such file type */
    return __mbool(S_ISDOOR(mode));
}

__ss_bool __ss_S_ISPORT(__ss_int mode) {
    (void)mode; /* unused where the platform has no such file type */
    return __mbool(S_ISPORT(mode));
}

__ss_bool __ss_S_ISWHT(__ss_int mode) {
    (void)mode; /* unused where the platform has no such file type */
    return __mbool(S_ISWHT(mode));
}

str *filemode(__ss_int mode) {
    __GC_STRING perm;

    /* Use the literal POSIX mode-bit values directly rather than the
       __ss_S_* globals, purely to keep this function self-contained.
       The numeric values below are the same ones stat.py itself
       hardcodes, and __init() now assigns those same values to the
       globals unconditionally (see stat.cpp), so the two are always
       in sync on every platform. */
    const __ss_int SS_IFLNK  = 0120000, SS_IFSOCK = 0140000, SS_IFREG = 0100000,
                   SS_IFBLK  = 0060000, SS_IFDIR  = 0040000, SS_IFCHR = 0020000,
                   SS_IFIFO  = 0010000;
    const __ss_int SS_ISUID = 04000, SS_ISGID = 02000, SS_ISVTX = 01000,
                   SS_IRUSR = 0400,  SS_IWUSR = 0200,  SS_IXUSR = 0100,
                   SS_IRGRP = 0040,  SS_IWGRP = 0020,  SS_IXGRP = 0010,
                   SS_IROTH = 0004,  SS_IWOTH = 0002,  SS_IXOTH = 0001;

    __ss_int ftype = mode & 0170000; /* S_IFMT */
    if (ftype == SS_IFLNK) perm += 'l';
    else if (ftype == SS_IFSOCK) perm += 's';
    else if (ftype == SS_IFREG) perm += '-';
    else if (ftype == SS_IFBLK) perm += 'b';
    else if (ftype == SS_IFDIR) perm += 'd';
    else if (ftype == SS_IFCHR) perm += 'c';
    else if (ftype == SS_IFIFO) perm += 'p';
    else perm += '?';

    /* owner */
    perm += (mode & SS_IRUSR) ? 'r' : '-';
    perm += (mode & SS_IWUSR) ? 'w' : '-';
    if ((mode & (SS_IXUSR|SS_ISUID)) == (SS_IXUSR|SS_ISUID)) perm += 's';
    else if (mode & SS_ISUID) perm += 'S';
    else if (mode & SS_IXUSR) perm += 'x';
    else perm += '-';

    /* group */
    perm += (mode & SS_IRGRP) ? 'r' : '-';
    perm += (mode & SS_IWGRP) ? 'w' : '-';
    if ((mode & (SS_IXGRP|SS_ISGID)) == (SS_IXGRP|SS_ISGID)) perm += 's';
    else if (mode & SS_ISGID) perm += 'S';
    else if (mode & SS_IXGRP) perm += 'x';
    else perm += '-';

    /* other */
    perm += (mode & SS_IROTH) ? 'r' : '-';
    perm += (mode & SS_IWOTH) ? 'w' : '-';
    if ((mode & (SS_IXOTH|SS_ISVTX)) == (SS_IXOTH|SS_ISVTX)) perm += 't';
    else if (mode & SS_ISVTX) perm += 'T';
    else if (mode & SS_IXOTH) perm += 'x';
    else perm += '-';

    return new str(perm);
}

} // module namespace

