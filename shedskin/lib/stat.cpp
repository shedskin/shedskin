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

