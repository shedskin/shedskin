#ifndef __OS_HPP
#define __OS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __os__ {

extern str *linesep, *name;
extern dict<str *, str *> *__ss_environ;
extern dict<str *, __ss_int> *pathconf_names, *confstr_names, *sysconf_names;
extern str *altsep, *curdir, *defpath, *devnull, *extsep, *pardir, *pathsep, *sep;

extern __ss_int __ss_F_OK, __ss_R_OK, __ss_W_OK, __ss_X_OK, __ss_NGROUPS_MAX, __ss_TMP_MAX, __ss_WCONTINUED, __ss_WNOHANG, __ss_WUNTRACED, __ss_O_RDONLY, __ss_O_WRONLY, __ss_O_RDWR, __ss_O_NDELAY, __ss_O_NONBLOCK, __ss_O_APPEND, __ss_O_DSYNC, __ss_O_RSYNC, __ss_O_SYNC, __ss_O_NOCTTY, __ss_O_CREAT, __ss_O_EXCL, __ss_O_TRUNC, __ss_O_BINARY, __ss_O_TEXT, __ss_O_LARGEFILE, __ss_O_SHLOCK, __ss_O_EXLOCK, __ss_O_NOINHERIT, __ss__O_SHORT_LIVED, __ss_O_TEMPORARY, __ss_O_RANDOM, __ss_O_SEQUENTIAL, __ss_O_ASYNC, __ss_O_DIRECT, __ss_O_DIRECTORY, __ss_O_NOFOLLOW, __ss_O_NOATIME, __ss_EX_OK, __ss_EX_USAGE, __ss_EX_DATAERR, __ss_EX_NOINPUT, __ss_EX_NOUSER, __ss_EX_NOHOST, __ss_EX_UNAVAILABLE, __ss_EX_SOFTWARE, __ss_EX_OSERR, __ss_EX_OSFILE, __ss_EX_CANTCREAT, __ss_EX_IOERR, __ss_EX_TEMPFAIL, __ss_EX_PROTOCOL, __ss_EX_NOPERM, __ss_EX_CONFIG, __ss_EX_NOTFOUND, __ss_P_WAIT, __ss_P_NOWAIT, __ss_P_OVERLAY, __ss_P_NOWAITO, __ss_P_DETACH, __ss_SEEK_SET, __ss_SEEK_CUR, __ss_SEEK_END;

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
void *mkdir(str *path, __ss_int mode=0777);
void *makedirs(str *name, __ss_int mode=0777);
void *abort();
__ss_int system(str *c);

class namedtuple : public pyobj {
public:
    tuple2<__ss_int, __ss_int> *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);
    str *__repr__();
    virtual __ss_int __len__() = 0;
    virtual __ss_int __getitem__(__ss_int i) = 0;
};

extern class_ *cl___cstat;
class __cstat : public namedtuple {
public:
    __ss_int st_mode, st_ino, st_dev, st_rdev, st_nlink, st_uid, st_gid, st_size, st_blksize, st_blocks;
    __ss_int __ss_st_mtime, __ss_st_atime, __ss_st_ctime;

    __cstat(str *path, __ss_int t);
    __cstat(__ss_int fd);
    void fill_er_up();

    __ss_int __len__();
    __ss_int __getitem__(__ss_int i);

};

__cstat *stat(str *path);
__cstat *lstat(str *path);
__cstat *fstat(__ss_int fd);

__ss_bool stat_float_times(__ss_int newvalue=-1);
str *strerror(__ss_int i);

void *putenv(str* varname, str* value);
__ss_int umask(__ss_int newmask);
__ss_int chmod(str* path, __ss_int val);
void *renames(str* old, str* _new);
tuple2<__ss_int,__ss_int>* pipe();
__ss_int dup(__ss_int f1);
void *dup2(__ss_int f1, __ss_int f2);
void *close(__ss_int fd);
__ss_int open(str *name, __ss_int flags);
file* fdopen(__ss_int fd, str* mode=NULL, __ss_int bufsize=-1);
str *read(__ss_int fd, __ss_int n);
__ss_int write(__ss_int fd, str *s);

class popen_pipe : public file {
public:
    popen_pipe(str *name, str *mode=0);
    popen_pipe(FILE* pipe);
    void *close();
};

popen_pipe* popen(str* cmd);
popen_pipe* popen(str* cmd, str* mode);
popen_pipe* popen(str* cmd, str* mode, __ss_int bufsize);

void _exit(__ss_int code);

#ifndef WIN32
__ss_int __ss_WCOREDUMP(__ss_int status);
__ss_int __ss_WEXITSTATUS(__ss_int status);
__ss_int __ss_WIFCONTINUED(__ss_int status);
__ss_int __ss_WIFEXITED(__ss_int status);
__ss_int __ss_WIFSIGNALED(__ss_int status);
__ss_int __ss_WIFSTOPPED(__ss_int status);
__ss_int __ss_WSTOPSIG(__ss_int status);
__ss_int __ss_WTERMSIG(__ss_int status);

void *execl(__ss_int n, str *file, ...);
void *execlp(__ss_int n, str *file, ...);
void *execle(__ss_int n, str *file, ...);
void *execlpe(__ss_int n, str *file, ...);
void *execv(str *file, list<str*> *args);
void *execvp(str *file, list<str*> *args);
void *execve(str *file, list<str*> *args, dict<str *, str *> *env);
void *execvpe(str *file, list<str*> *args, dict<str *, str *> *env);

__ss_int spawnl(__ss_int n, __ss_int mode, str *file, ...);
__ss_int spawnlp(__ss_int n, __ss_int mode, str *file, ...);
__ss_int spawnle(__ss_int n, __ss_int mode, str *file, ...);
__ss_int spawnlpe(__ss_int n, __ss_int mode, str *file, ...);
__ss_int spawnv(__ss_int mode, str *file, list<str *> *args);
__ss_int spawnvp(__ss_int mode, str *file, list<str *> *args);
__ss_int spawnve(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env);
__ss_int spawnvpe(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env);

void *unsetenv(str* var);
__ss_int getpid();

tuple2<file*,file*>* popen2(str* cmd);
tuple2<file*,file*>* popen2(str* cmd, str* mode, __ss_int bufsize);

tuple2<file*,file*>* popen3(str* cmd);
tuple2<file*,file*>* popen3(str* cmd, str* mode, __ss_int bufsize);

tuple2<file*,file*>* popen4(str* cmd);
tuple2<file*,file*>* popen4(str* cmd, str* mode, __ss_int bufsize);

extern class_ *cl___vfsstat;
class __vfsstat : public namedtuple {
public:
    __ss_int f_bsize, f_frsize, f_blocks, f_bfree, f_bavail, f_files, f_ffree, f_favail, f_flag, f_namemax;

    __vfsstat(str *path);
    __vfsstat(__ss_int fd);
    void fill_er_up();

    __ss_int __len__();
    __ss_int __getitem__(__ss_int i);
};

__vfsstat *statvfs(str *path);
__vfsstat *fstatvfs(__ss_int fd);

__ss_int getuid();
void *setuid(__ss_int uid);
__ss_int geteuid();
void *seteuid(__ss_int euid);
__ss_int getgid();
void *setgid(__ss_int gid);
__ss_int getegid();
void *setegid(__ss_int egid);
__ss_int getpgid(__ss_int pid);
void *setpgid(__ss_int pid, __ss_int pgrp);
__ss_int getpgrp();
void *setpgrp();
__ss_int getppid();
void *setreuid(__ss_int ruid, __ss_int euid);
void *setregid(__ss_int rgid, __ss_int egid);
__ss_int getsid(__ss_int pid);
__ss_int setsid();
__ss_int tcgetpgrp(__ss_int fd);
void *tcsetpgrp(__ss_int fd, __ss_int pg);

void *lchown(str *path, __ss_int uid, __ss_int gid);
void *link(str *src, str *dst);
void *symlink(str *src, str *dst);

list<__ss_int> *getgroups();
void *setgroups(pyseq<__ss_int> *groups);
str *getlogin();

str *readlink(str *path);
void *fchdir(__ss_int f1);
void *fdatasync(__ss_int f1);
void *chown(str *path, __ss_int uid, __ss_int gid);
void *chroot(str *path);

str *ctermid();
__ss_bool isatty(__ss_int fd);
str *ttyname(__ss_int fd);

tuple2<str *, str *> *uname();

__ss_int fork();
tuple2<__ss_int, __ss_int> *forkpty();

tuple2<__ss_int, __ss_int> *openpty();

tuple2<__ss_int, __ss_int> *wait();
tuple2<__ss_int, __ss_int> *waitpid(__ss_int pid, __ss_int options);

__ss_int nice(__ss_int n);

void *kill(__ss_int pid, __ss_int sig);
void *killpg(__ss_int pgid, __ss_int sig);

__ss_int pathconf(str *path, str *name);
__ss_int pathconf(str *path, __ss_int name);
__ss_int fpathconf(__ss_int fd, str *name);
__ss_int fpathconf(__ss_int fd, __ss_int name);
str *confstr(str *name);
str *confstr(__ss_int name);
__ss_int sysconf(str *name);
__ss_int sysconf(__ss_int name);

void *ftruncate(__ss_int fd, __ss_int n);

tuple2<double, double> *getloadavg();
void *mkfifo(str *path, __ss_int mode=438);
void *unlink(str *path);

void *fsync(__ss_int fd);
void *lseek(__ss_int fd, __ss_int pos, __ss_int how);

str *urandom(__ss_int n);

void *utime(str *path, tuple2<__ss_int, __ss_int> *times);
void *utime(str *path, tuple2<__ss_int, double> *times);
void *utime(str *path, tuple2<double, __ss_int> *times);
void *utime(str *path, tuple2<double, double> *times);

__ss_bool access(str *path, __ss_int mode);
tuple2<double, double> *times();

str *tmpnam();
file *tmpfile();
str *tempnam(str *dir, str *prefix=NULL);

__ss_int __ss_makedev(__ss_int major, __ss_int minor);
__ss_int __ss_major(__ss_int dev);
__ss_int __ss_minor(__ss_int dev);

void *mknod(str *filename, __ss_int mode=438, __ss_int device=0);

#endif

void __init();

} // module namespace
#endif
