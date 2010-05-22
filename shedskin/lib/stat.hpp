#ifndef __STAT_HPP
#define __STAT_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __stat__ {

extern __ss_int __ss_S_IWRITE;
extern __ss_int __ss_ST_MTIME;
extern __ss_int __ss_S_IFLNK;
extern __ss_int __ss_ST_INO;
extern __ss_int __ss_S_IXOTH;
extern __ss_int __ss_ST_UID;
extern __ss_int __ss_S_IRGRP;
extern __ss_int __ss_S_IXUSR;
extern __ss_int __ss_S_IRUSR;
extern __ss_int __ss_ST_NLINK;
extern __ss_int __ss_S_IFBLK;
extern __ss_int __ss_S_IFDIR;
extern __ss_int __ss_ST_ATIME;
extern __ss_int __ss_S_ISUID;
extern __ss_int __ss_S_IRWXU;
extern __ss_int __ss_S_IFCHR;
extern __ss_int __ss_S_ISGID;
extern __ss_int __ss_S_IFREG;
extern __ss_int __ss_S_IREAD;
extern __ss_int __ss_S_IFIFO;
extern __ss_int __ss_S_IFSOCK;
extern __ss_int __ss_S_ISVTX;
extern __ss_int __ss_ST_MODE;
extern __ss_int __ss_S_ENFMT;
extern __ss_int __ss_S_IEXEC;
extern __ss_int __ss_ST_CTIME;
extern __ss_int __ss_S_IWOTH;
extern __ss_int __ss_S_IXGRP;
extern __ss_int __ss_S_IRWXG;
extern __ss_int __ss_S_IWUSR;
extern __ss_int __ss_ST_GID;
extern __ss_int __ss_S_IROTH;
extern __ss_int __ss_S_IWGRP;
extern __ss_int __ss_S_IRWXO;
extern __ss_int __ss_ST_DEV;
extern __ss_int __ss_ST_SIZE;

#if !defined (_MSC_VER)
__ss_int __ss_S_IMODE(__ss_int mode);
__ss_int __ss_S_IFMT(__ss_int mode);
__ss_int __ss_S_ISDIR(__ss_int mode);
__ss_int __ss_S_ISCHR(__ss_int mode);
__ss_int __ss_S_ISBLK(__ss_int mode);
__ss_int __ss_S_ISREG(__ss_int mode);
__ss_int __ss_S_ISFIFO(__ss_int mode);
#endif
#ifndef WIN32
__ss_int __ss_S_ISLNK(__ss_int mode);
__ss_int __ss_S_ISSOCK(__ss_int mode);
#endif

void __init();

} // module namespace
#endif
