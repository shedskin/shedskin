#ifndef __STAT_HPP
#define __STAT_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __stat__ {

extern int  S_IWRITE;
extern int  ST_MTIME;
extern int  S_IFLNK;
extern int  ST_INO;
extern int  S_IXOTH;
extern int  ST_UID;
extern int  S_IRGRP;
extern int  S_IXUSR;
extern int  S_IRUSR;
extern int  ST_NLINK;
extern int  S_IFBLK;
extern int  S_IFDIR;
extern int  ST_ATIME;
extern int  S_ISUID;
extern int  S_IRWXU;
extern int  S_IFCHR;
extern int  S_ISGID;
extern int  S_IFREG;
extern int  S_IREAD;
extern int  S_IFIFO;
extern int  S_IFSOCK;
extern int  S_ISVTX;
extern int  ST_MODE;
extern int  S_ENFMT;
extern int  S_IEXEC;
extern int  ST_CTIME;
extern int  S_IWOTH;
extern int  S_IXGRP;
extern int  S_IRWXG;
extern int  S_IWUSR;
extern int  ST_GID;
extern int  S_IROTH;
extern int  S_IWGRP;
extern int  S_IRWXO;
extern int  ST_DEV;
extern int  ST_SIZE;

int S_IMODE(int mode);
int S_IFMT(int mode);
int S_ISDIR(int mode);
int S_ISCHR(int mode);
int S_ISBLK(int mode);
int S_ISREG(int mode);
int S_ISFIFO(int mode);
int S_ISLNK(int mode);
int S_ISSOCK(int mode);

void __init();

} // module namespace
#endif
