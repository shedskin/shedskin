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

namespace __stat__ {

__ss_int __ss_ST_MODE, __ss_ST_INO, __ss_ST_DEV, __ss_ST_NLINK, __ss_ST_UID, __ss_ST_GID, __ss_ST_SIZE, __ss_ST_ATIME, __ss_ST_MTIME, __ss_ST_CTIME, __ss_S_IFDIR, __ss_S_IFCHR, __ss_S_IFBLK, __ss_S_IFREG, __ss_S_IFIFO, __ss_S_IFLNK, __ss_S_IFSOCK, __ss_S_ISUID, __ss_S_ISGID, __ss_S_ENFMT, __ss_S_ISVTX, __ss_S_IREAD, __ss_S_IWRITE, __ss_S_IEXEC, __ss_S_IRWXU, __ss_S_IRUSR, __ss_S_IWUSR, __ss_S_IXUSR, __ss_S_IRWXG, __ss_S_IRGRP, __ss_S_IWGRP, __ss_S_IXGRP, __ss_S_IRWXO, __ss_S_IROTH, __ss_S_IWOTH, __ss_S_IXOTH;

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
#if !defined( _MSC_VER )
   __ss_S_IFIFO = S_IFIFO;
   __ss_S_IFBLK = S_IFBLK;
   __ss_S_IRWXU = S_IRWXU;
   __ss_S_IRUSR = S_IRUSR;
   __ss_S_IWUSR = S_IWUSR;
   __ss_S_IXUSR = S_IXUSR;
#endif

#ifndef WIN32
   __ss_S_ISUID = S_ISUID;
   __ss_S_ISGID = S_ISGID;
   __ss_S_ENFMT = S_ISGID;
   __ss_S_ISVTX = S_ISVTX;
   __ss_S_IFLNK = S_IFLNK;
   __ss_S_IFSOCK = S_IFSOCK;
   __ss_S_IRWXG = S_IRWXG;
   __ss_S_IRGRP = S_IRGRP;
   __ss_S_IWGRP = S_IWGRP;
   __ss_S_IXGRP = S_IXGRP;
   __ss_S_IRWXO = S_IRWXO;
   __ss_S_IROTH = S_IROTH;
   __ss_S_IWOTH = S_IWOTH;
   __ss_S_IXOTH = S_IXOTH;
#endif
}

__ss_int __ss_S_ISDIR(__ss_int mode) {

    return S_ISDIR(mode);
}

__ss_int __ss_S_ISREG(__ss_int mode) {

    return S_ISREG(mode);
}

/* S_IMODE/S_IFMT operate on literal bitmask constants only, with no
   dependency on the POSIX macros that are missing from MSVC's
   <sys/stat.h>, so they are compiled unconditionally. Only S_ISCHR,
   S_ISBLK and S_ISFIFO below depend on those missing macros and stay
   guarded for MSVC. */
__ss_int __ss_S_IMODE(__ss_int mode) {
    return (mode&4095); /* XXX */
}

__ss_int __ss_S_IFMT(__ss_int mode) {
    return (mode&61440); /* XXX */
}

#if !defined( _MSC_VER )
__ss_int __ss_S_ISCHR(__ss_int mode) {

    return S_ISCHR(mode);
}

__ss_int __ss_S_ISBLK(__ss_int mode) {

    return S_ISBLK(mode);
}

__ss_int __ss_S_ISFIFO(__ss_int mode) {

    return S_ISFIFO(mode);
}
#endif

#ifndef WIN32
__ss_int __ss_S_ISLNK(__ss_int mode) {

    return S_ISLNK(mode);
}

__ss_int __ss_S_ISSOCK(__ss_int mode) {

    return S_ISSOCK(mode);
}
#endif

str *filemode(__ss_int mode) {
    __GC_STRING perm;

    /* Use the literal POSIX mode-bit values directly rather than the
       __ss_S_* globals: those are only populated inside __init() under
       '#ifndef WIN32' / '#if !defined(_MSC_VER)' guards, so on a Windows
       build most of them (S_IFLNK, S_IFSOCK, S_IRGRP/IWGRP/IXGRP,
       S_IROTH/IWOTH/IXOTH, S_ISUID/ISGID/ISVTX, and on MSVC also
       S_IFBLK/IFIFO/IRUSR/IWUSR/IXUSR) stay at their default value of 0.
       Comparing against those zeroed globals produces false-positive
       matches (e.g. a plain permissions-only mode like 0644, which has
       no type bits set, would spuriously equal a zeroed __ss_S_IFLNK and
       be misreported as a symlink). The numeric values below are the
       same ones stat.py itself hardcodes, and are portable across
       platforms (see stat.py's own module docstring). */
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

