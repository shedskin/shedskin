#ifndef __OS_HPP
#define __OS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __os__ {

extern str *linesep, *name;
extern dict<str *, str *> *__ss_environ;
extern str *altsep, *curdir, *defpath, *devnull, *extsep, *pardir, *pathsep, *sep;


typedef OSError error;

class popen_pipe;
class __cstat;

list<str *> *listdir(str *path);
str *getcwd();
void *chdir(str *dir);
str *getenv(str *name, str *alternative=0);
void *rename(str *a, str *b);
void *remove(str *a);
void *rmdir(str *a);
void *removedirs(str *name);
void *mkdir(str *path, int mode=0777);
void *makedirs(str *name, int mode=0777);
void *abort();
int system(str *c);

extern class_ *cl___cstat;
class __cstat : public pyobj {
public:
    int st_mode, st_ino, st_dev, st_rdev, st_nlink, st_uid, st_gid, st_size, st_blksize, st_blocks;
    int __ss_st_mtime, __ss_st_atime, __ss_st_ctime;

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

int stat_float_times(int newvalue=-1);
str *strerror(int i);

int getpid();
void *putenv(str* varname, str* value);
int umask(int newmask);
void *unsetenv(str* var);
int chmod(str* path, int val);
void *renames(str* old, str* _new);
tuple2<int,int>* pipe();
int dup(int f1);
void *dup2(int f1, int f2);
void *execvp(str* file, list<str*>* args);
void *execv(str* file, list<str*>* args);
void *close(int fd);
file* fdopen(int fd);
file* fdopen(int fd, str* mode);
file* fdopen(int fd, str* mode, int bufsize);

class popen_pipe : public file {
public:
    popen_pipe(str *name, str *mode=0);
    popen_pipe(FILE* pipe);
    void *close();
};

popen_pipe* popen(str* cmd);
popen_pipe* popen(str* cmd, str* mode);
popen_pipe* popen(str* cmd, str* mode, int bufsize);

tuple2<file*,file*>* popen2(str* cmd);
tuple2<file*,file*>* popen2(str* cmd, str* mode, int bufsize);

tuple2<file*,file*>* popen3(str* cmd);
tuple2<file*,file*>* popen3(str* cmd, str* mode, int bufsize);

tuple2<file*,file*>* popen4(str* cmd);
tuple2<file*,file*>* popen4(str* cmd, str* mode, int bufsize);

#ifndef WIN32
str *readlink(str *path);
void *fchdir(int f1);
void *fdatasync(int f1);

int getuid();
int getgid();
list<int> *getgroups();
int getpgid(int pid);
int getpgrp();
str *getlogin();

void *chown(str *path, int uid, int gid);
void *chroot(str *path);
str *ctermid();

int fork();
#endif

void __init();

} // module namespace
#endif
