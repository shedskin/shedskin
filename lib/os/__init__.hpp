#ifndef __OS_HPP
#define __OS_HPP

#include "builtin.hpp"

#ifdef WIN32
#undef environ
#endif

using namespace __shedskin__;
namespace __os__ {

extern str *linesep, *name;
extern dict<str *, str *> *environ;
extern str *altsep, *curdir, *defpath, *devnull, *extsep, *pardir, *pathsep, *sep;

list<str *> *listdir(str *path);

str *getcwd();
int chdir(str *dir);
str *getenv(str *name, str *alternative=0);
int rename(str *a, str *b);
int remove(str *a);
int rmdir(str *a);
int removedirs(str *name);
int mkdir(str *path, int mode=0777);
int makedirs(str *name, int mode=0777);
int abort();
int system(str *c);

class __cstat;

extern class_ *cl___cstat;
class __cstat : public pyobj {
public:
    int st_mode, st_ino, st_dev, st_rdev, st_nlink, st_uid, st_gid, st_size, st_blksize, st_blocks;
    int _st_mtime, _st_atime, _st_ctime;

    __cstat(str *path, int t);
    __cstat(int fd);
    void fill_er_up();

    int __len__();
    int __getitem__(int i);
    tuple2<int, int> *__slice__(int x, int l, int u, int s);

    str *__repr__();
};

__cstat *stat(str *path);
__cstat *lstat(str *path);
__cstat *fstat(int fd);

#ifndef WIN32
str *readlink(str *path);

int getuid();
int getgid();
int chown(str *path, int uid, int gid);

int fork();
#endif

int stat_float_times(int newvalue=-1);
str *strerror(int i);

int getpid();
int putenv(str* varname, str* value);
int umask(int newmask);
int unsetenv(str* var);
int chmod(str* path, int val);
int renames(str* old, str* _new);

typedef OSError error;

void __init();

} // module namespace
#endif
