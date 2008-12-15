#ifndef __OS_HPP
#define __OS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __os__ {

extern str *linesep, *name;
extern dict<str *, str *> *__ss_environ;
extern str *altsep, *curdir, *defpath, *devnull, *extsep, *pardir, *pathsep, *sep;
extern int __ss_O_APPEND, __ss_O_CREAT, __ss_O_EXCL, __ss_O_RDONLY, __ss_O_RDWR, __ss_O_TRUNC, __ss_O_WRONLY;

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
int open(str *name, int flags);
file* fdopen(int fd, str* mode=NULL, int bufsize=-1);
str *read(int fd, int n);
int write(int fd, str *s);

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
int getuid();
int geteuid();
int getgid();
int getegid();
int getpgid(int pid);
int getpgrp();
int getppid();
int getsid(int pid);

void *lchown(str *path, int uid, int gid);
void *link(str *src, str *dst);
void *symlink(str *src, str *dst);

list<int> *getgroups();
str *getlogin();

str *readlink(str *path);
void *fchdir(int f1);
void *fdatasync(int f1);
void *chown(str *path, int uid, int gid);
void *chroot(str *path);

str *ctermid();
int isatty(int fd);
str *ttyname(int fd);

tuple2<str *, str *> *uname();

int fork();
tuple2<int, int> *wait();
#endif

void __init();

} // module namespace
#endif
