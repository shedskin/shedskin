#ifndef __STAT_HPP
#define __STAT_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __stat__ {

extern int __ss_S_IWRITE;
extern int __ss_ST_MTIME;
extern int __ss_S_IFLNK;
extern int __ss_ST_INO;
extern int __ss_S_IXOTH;
extern int __ss_ST_UID;
extern int __ss_S_IRGRP;
extern int __ss_S_IXUSR;
extern int __ss_S_IRUSR;
extern int __ss_ST_NLINK;
extern int __ss_S_IFBLK;
extern int __ss_S_IFDIR;
extern int __ss_ST_ATIME;
extern int __ss_S_ISUID;
extern int __ss_S_IRWXU;
extern int __ss_S_IFCHR;
extern int __ss_S_ISGID;
extern int __ss_S_IFREG;
extern int __ss_S_IREAD;
extern int __ss_S_IFIFO;
extern int __ss_S_IFSOCK;
extern int __ss_S_ISVTX;
extern int __ss_ST_MODE;
extern int __ss_S_ENFMT;
extern int __ss_S_IEXEC;
extern int __ss_ST_CTIME;
extern int __ss_S_IWOTH;
extern int __ss_S_IXGRP;
extern int __ss_S_IRWXG;
extern int __ss_S_IWUSR;
extern int __ss_ST_GID;
extern int __ss_S_IROTH;
extern int __ss_S_IWGRP;
extern int __ss_S_IRWXO;
extern int __ss_ST_DEV;
extern int __ss_ST_SIZE; 

int __ss_S_IMODE(int mode);
int __ss_S_IFMT(int mode);
int __ss_S_ISDIR(int mode);
int __ss_S_ISCHR(int mode);
int __ss_S_ISBLK(int mode);
int __ss_S_ISREG(int mode);
int __ss_S_ISFIFO(int mode);
int __ss_S_ISLNK(int mode);
int __ss_S_ISSOCK(int mode); 

void __init();

} // module namespace
#endif
