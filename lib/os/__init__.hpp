#ifndef __OS_HPP
#define __OS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __os__ {

extern str *linesep, *name;
extern dict<str *, str *> *__ss_environ;
extern dict<str *, int> *pathconf_names, *confstr_names, *sysconf_names;
extern str *altsep, *curdir, *defpath, *devnull, *extsep, *pardir, *pathsep, *sep;

extern int __ss_F_OK, __ss_R_OK, __ss_W_OK, __ss_X_OK, __ss_NGROUPS_MAX, __ss_TMP_MAX, __ss_WCONTINUED, __ss_WNOHANG, __ss_WUNTRACED, __ss_O_RDONLY, __ss_O_WRONLY, __ss_O_RDWR, __ss_O_NDELAY, __ss_O_NONBLOCK, __ss_O_APPEND, __ss_O_DSYNC, __ss_O_RSYNC, __ss_O_SYNC, __ss_O_NOCTTY, __ss_O_CREAT, __ss_O_EXCL, __ss_O_TRUNC, __ss_O_BINARY, __ss_O_TEXT, __ss_O_LARGEFILE, __ss_O_SHLOCK, __ss_O_EXLOCK, __ss_O_NOINHERIT, __ss__O_SHORT_LIVED, __ss_O_TEMPORARY, __ss_O_RANDOM, __ss_O_SEQUENTIAL, __ss_O_ASYNC, __ss_O_DIRECT, __ss_O_DIRECTORY, __ss_O_NOFOLLOW, __ss_O_NOATIME, __ss_EX_OK, __ss_EX_USAGE, __ss_EX_DATAERR, __ss_EX_NOINPUT, __ss_EX_NOUSER, __ss_EX_NOHOST, __ss_EX_UNAVAILABLE, __ss_EX_SOFTWARE, __ss_EX_OSERR, __ss_EX_OSFILE, __ss_EX_CANTCREAT, __ss_EX_IOERR, __ss_EX_TEMPFAIL, __ss_EX_PROTOCOL, __ss_EX_NOPERM, __ss_EX_CONFIG, __ss_EX_NOTFOUND, __ss_P_WAIT, __ss_P_NOWAIT, __ss_P_OVERLAY, __ss_P_NOWAITO, __ss_P_DETACH;

typedef OSError error;

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

class namedtuple : public pyobj {
public:
    tuple2<int, int> *__slice__(int x, int l, int u, int s);
    str *__repr__();
    virtual int __len__() = 0;
    virtual int __getitem__(int i) = 0;
};

extern class_ *cl___cstat;
class __cstat : public namedtuple {
public:
    int st_mode, st_ino, st_dev, st_rdev, st_nlink, st_uid, st_gid, st_size, st_blksize, st_blocks;
    int __ss_st_mtime, __ss_st_atime, __ss_st_ctime;

    __cstat(str *path, int t);
    __cstat(int fd);
    void fill_er_up();

    int __len__();
    int __getitem__(int i);

};

__cstat *stat(str *path);
__cstat *lstat(str *path);
__cstat *fstat(int fd);

int stat_float_times(int newvalue=-1);
str *strerror(int i);

void *putenv(str* varname, str* value);
int umask(int newmask);
int chmod(str* path, int val);
void *renames(str* old, str* _new);
tuple2<int,int>* pipe();
int dup(int f1);
void *dup2(int f1, int f2);
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

#ifndef WIN32
int __ss_WCOREDUMP(int status);
int __ss_WEXITSTATUS(int status);
int __ss_WIFCONTINUED(int status);
int __ss_WIFEXITED(int status);
int __ss_WIFSIGNALED(int status);
int __ss_WIFSTOPPED(int status);
int __ss_WSTOPSIG(int status);
int __ss_WTERMSIG(int status);

void *execl(int n, str *file, ...);
void *execlp(int n, str *file, ...);
void *execle(int n, str *file, ...);
void *execlpe(int n, str *file, ...);
void *execv(str *file, list<str*> *args);
void *execvp(str *file, list<str*> *args);
void *execve(str *file, list<str*> *args, dict<str *, str *> *env);
void *execvpe(str *file, list<str*> *args, dict<str *, str *> *env);

int spawnl(int n, int mode, str *file, ...);
int spawnlp(int n, int mode, str *file, ...);
int spawnle(int n, int mode, str *file, ...);
int spawnlpe(int n, int mode, str *file, ...);
int spawnv(int mode, str *file, list<str *> *args);
int spawnvp(int mode, str *file, list<str *> *args);
int spawnve(int mode, str *file, list<str *> *args, dict<str *, str *> *env);
int spawnvpe(int mode, str *file, list<str *> *args, dict<str *, str *> *env);

void *unsetenv(str* var);
int getpid();

tuple2<file*,file*>* popen2(str* cmd);
tuple2<file*,file*>* popen2(str* cmd, str* mode, int bufsize);

tuple2<file*,file*>* popen3(str* cmd);
tuple2<file*,file*>* popen3(str* cmd, str* mode, int bufsize);

tuple2<file*,file*>* popen4(str* cmd);
tuple2<file*,file*>* popen4(str* cmd, str* mode, int bufsize);

extern class_ *cl___vfsstat;
class __vfsstat : public namedtuple {
public:
    int f_bsize, f_frsize, f_blocks, f_bfree, f_bavail, f_files, f_ffree, f_favail, f_flag, f_namemax; 

    __vfsstat(str *path);
    __vfsstat(int fd);
    void fill_er_up();

    int __len__();
    int __getitem__(int i);
};

__vfsstat *statvfs(str *path);
__vfsstat *fstatvfs(int fd);

int getuid();
void *setuid(int uid);
int geteuid();
void *seteuid(int euid);
int getgid();
void *setgid(int gid);
int getegid();
void *setegid(int egid);
int getpgid(int pid);
void *setpgid(int pid, int pgrp);
int getpgrp();
void *setpgrp();
int getppid();
void *setreuid(int ruid, int euid);
void *setregid(int rgid, int egid);
int getsid(int pid);
int setsid();
int tcgetpgrp(int fd);
void *tcsetpgrp(int fd, int pg);

void *lchown(str *path, int uid, int gid);
void *link(str *src, str *dst);
void *symlink(str *src, str *dst);

list<int> *getgroups();
void *setgroups(pyseq<int> *groups);
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
tuple2<int, int> *forkpty();

tuple2<int, int> *openpty();

tuple2<int, int> *wait();
tuple2<int, int> *waitpid(int pid, int options);

int nice(int n);

void *kill(int pid, int sig);
void *killpg(int pgid, int sig);

int pathconf(str *path, str *name); 
int pathconf(str *path, int name); 
int fpathconf(int fd, str *name); 
int fpathconf(int fd, int name); 
str *confstr(str *name);
str *confstr(int name);
int sysconf(str *name);
int sysconf(int name);

void *ftruncate(int fd, int n);

tuple2<double, double> *getloadavg();
void *mkfifo(str *path, int mode=438);
void *unlink(str *path);

void *fsync(int fd);
void *lseek(int fd, int pos, int how);

str *urandom(int n);

void *utime(str *path, tuple2<int, int> *times);
void *utime(str *path, tuple2<int, double> *times);
void *utime(str *path, tuple2<double, int> *times);
void *utime(str *path, tuple2<double, double> *times);

int access(str *path, int mode);
tuple2<double, double> *times();

str *tmpnam();
file *tmpfile();
str *tempnam(str *dir, str *prefix=NULL);

int __ss_makedev(int major, int minor);
int __ss_major(int dev);
int __ss_minor(int dev);

void *mknod(str *filename, int mode=438, int device=0);

#endif

void __init();

} // module namespace
#endif
