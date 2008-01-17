#include "stat.hpp"

namespace __stat__ {

int ST_ATIME, ST_CTIME, ST_DEV, ST_GID, ST_INO, ST_MODE, ST_MTIME, ST_NLINK, ST_SIZE, ST_UID, S_ENFMT, S_IEXEC, S_IFBLK, S_IFCHR, S_IFDIR, S_IFIFO, S_IFLNK, S_IFREG, S_IFSOCK, S_IREAD, S_IRGRP, S_IROTH, S_IRUSR, S_IRWXG, S_IRWXO, S_IRWXU, S_ISGID, S_ISUID, S_ISVTX, S_IWGRP, S_IWOTH, S_IWRITE, S_IWUSR, S_IXGRP, S_IXOTH, S_IXUSR;

void __init() {
    ST_MODE = 0;
    ST_INO = 1;
    ST_DEV = 2;
    ST_NLINK = 3;
    ST_UID = 4;
    ST_GID = 5;
    ST_SIZE = 6;
    ST_ATIME = 7;
    ST_MTIME = 8;
    ST_CTIME = 9;
    S_IFDIR = 16384;
    S_IFCHR = 8192;
    S_IFBLK = 24576;
    S_IFREG = 32768;
    S_IFIFO = 4096;
    S_IFLNK = 40960;
    S_IFSOCK = 49152;
    S_ISUID = 2048;
    S_ISGID = 1024;
    S_ENFMT = S_ISGID;
    S_ISVTX = 512;
    S_IREAD = 256;
    S_IWRITE = 128;
    S_IEXEC = 64;
    S_IRWXU = 448;
    S_IRUSR = 256;
    S_IWUSR = 128;
    S_IXUSR = 64;
    S_IRWXG = 56;
    S_IRGRP = 32;
    S_IWGRP = 16;
    S_IXGRP = 8;
    S_IRWXO = 7;
    S_IROTH = 4;
    S_IWOTH = 2;
    S_IXOTH = 1;
}

int S_IMODE(int mode) {
    
    return (mode&4095);
}

int S_IFMT(int mode) {
    
    return (mode&61440);
}

int S_ISDIR(int mode) {
    
    return (S_IFMT(mode)==S_IFDIR);
}

int S_ISCHR(int mode) {
    
    return (S_IFMT(mode)==S_IFCHR);
}

int S_ISBLK(int mode) {
    
    return (S_IFMT(mode)==S_IFBLK);
}

int S_ISREG(int mode) {
    
    return (S_IFMT(mode)==S_IFREG);
}

int S_ISFIFO(int mode) {
    
    return (S_IFMT(mode)==S_IFIFO);
}

int S_ISLNK(int mode) {
    
    return (S_IFMT(mode)==S_IFLNK);
}

int S_ISSOCK(int mode) {
    
    return (S_IFMT(mode)==S_IFSOCK);
}

} // module namespace

