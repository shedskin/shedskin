#include "stat.hpp"

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

namespace __stat__ {

int __ss_ST_MODE, __ss_ST_INO, __ss_ST_DEV, __ss_ST_NLINK, __ss_ST_UID, __ss_ST_GID, __ss_ST_SIZE, __ss_ST_ATIME, __ss_ST_MTIME, __ss_ST_CTIME, __ss_S_IFDIR, __ss_S_IFCHR, __ss_S_IFBLK, __ss_S_IFREG, __ss_S_IFIFO, __ss_S_IFLNK, __ss_S_IFSOCK, __ss_S_ISUID, __ss_S_ISGID, __ss_S_ENFMT, __ss_S_ISVTX, __ss_S_IREAD, __ss_S_IWRITE, __ss_S_IEXEC, __ss_S_IRWXU, __ss_S_IRUSR, __ss_S_IWUSR, __ss_S_IXUSR, __ss_S_IRWXG, __ss_S_IRGRP, __ss_S_IWGRP, __ss_S_IXGRP, __ss_S_IRWXO, __ss_S_IROTH, __ss_S_IWOTH, __ss_S_IXOTH;

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
    __ss_S_IFBLK = S_IFBLK;
    __ss_S_IFREG = S_IFREG;
    __ss_S_IFIFO = S_IFIFO;
    __ss_S_IFLNK = S_IFLNK;
    __ss_S_IFSOCK = S_IFSOCK;
    __ss_S_ISUID = S_ISUID;
    __ss_S_ISGID = S_ISGID;
    __ss_S_ENFMT = S_ISGID;
    __ss_S_ISVTX = S_ISVTX;
    __ss_S_IREAD = S_IREAD;
    __ss_S_IWRITE = S_IWRITE;
    __ss_S_IEXEC = S_IEXEC;
    __ss_S_IRWXU = S_IRWXU;
    __ss_S_IRUSR = S_IRUSR;
    __ss_S_IWUSR = S_IWUSR;
    __ss_S_IXUSR = S_IXUSR;
    __ss_S_IRWXG = S_IRWXG;
    __ss_S_IRGRP = S_IRGRP;
    __ss_S_IWGRP = S_IWGRP;
    __ss_S_IXGRP = S_IXGRP;
    __ss_S_IRWXO = S_IRWXO;
    __ss_S_IROTH = S_IROTH;
    __ss_S_IWOTH = S_IWOTH;
    __ss_S_IXOTH = S_IXOTH;
}

int __ss_S_IMODE(int mode) {
    return (mode&4095); /* XXX */
}

int __ss_S_IFMT(int mode) {
    return (mode&61440); /* XXX */
}

int __ss_S_ISDIR(int mode) {
    
    return S_ISDIR(mode);
}

int __ss_S_ISCHR(int mode) {
    
    return S_ISCHR(mode);
}

int __ss_S_ISBLK(int mode) {
    
    return S_ISBLK(mode);
}

int __ss_S_ISREG(int mode) {
    
    return S_ISREG(mode);
}

int __ss_S_ISFIFO(int mode) {
    
    return S_ISFIFO(mode);
}

int __ss_S_ISLNK(int mode) {
    
    return S_ISLNK(mode);
}

int __ss_S_ISSOCK(int mode) {
    
    return S_ISSOCK(mode);
} 

} // module namespace

