/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __OS_HPP
#define __OS_HPP

#include "builtin.hpp"

#include <filesystem>
#include <functional>

using namespace __shedskin__;
namespace __os__ {

extern str *linesep, *name;
extern dict<str *, str *> *__ss_environ;
extern dict<str *, __ss_int> *pathconf_names, *confstr_names, *sysconf_names;
extern str *altsep, *curdir, *defpath, *devnull, *extsep, *pardir, *pathsep, *sep;

extern __ss_int __ss_F_OK, __ss_R_OK, __ss_W_OK, __ss_X_OK, __ss_NGROUPS_MAX, __ss_TMP_MAX, __ss_WCONTINUED, __ss_WNOHANG, __ss_WUNTRACED, __ss_O_RDONLY, __ss_O_WRONLY, __ss_O_RDWR, __ss_O_NDELAY, __ss_O_NONBLOCK, __ss_O_APPEND, __ss_O_DSYNC, __ss_O_RSYNC, __ss_O_SYNC, __ss_O_NOCTTY, __ss_O_CREAT, __ss_O_EXCL, __ss_O_TRUNC, __ss_O_BINARY, __ss_O_TEXT, __ss_O_LARGEFILE, __ss_O_SHLOCK, __ss_O_EXLOCK, __ss_O_NOINHERIT, __ss__O_SHORT_LIVED, __ss_O_TEMPORARY, __ss_O_RANDOM, __ss_O_SEQUENTIAL, __ss_O_ASYNC, __ss_O_DIRECT, __ss_O_DIRECTORY, __ss_O_NOFOLLOW, __ss_O_NOATIME, __ss_EX_OK, __ss_EX_USAGE, __ss_EX_DATAERR, __ss_EX_NOINPUT, __ss_EX_NOUSER, __ss_EX_NOHOST, __ss_EX_UNAVAILABLE, __ss_EX_SOFTWARE, __ss_EX_OSERR, __ss_EX_OSFILE, __ss_EX_CANTCREAT, __ss_EX_IOERR, __ss_EX_TEMPFAIL, __ss_EX_PROTOCOL, __ss_EX_NOPERM, __ss_EX_CONFIG, __ss_EX_NOTFOUND, __ss_P_WAIT, __ss_P_NOWAIT, __ss_P_OVERLAY, __ss_P_NOWAITO, __ss_P_DETACH, __ss_SEEK_SET, __ss_SEEK_CUR, __ss_SEEK_END;

typedef OSError error;

class __cstat;

list<str *> *listdir(str *path=0);
str *getcwd();
bytes *getcwdb();
void *chdir(str *dir);
str *getenv(str *name_, str *default_=0);
list<str *> *get_exec_path(dict<str *, str *> *env=0);
void *rename(str *a, str *b);
void *replace(str *a, str *b);
__ss_int cpu_count();
__ss_int process_cpu_count();

/* utf-8 + surrogateescape (PEP 383), the only filesystem encoding for now;
   like cpython, bytes pass through fsencode() and str through fsdecode() */
bytes *fsencode(str *filename);
bytes *fsencode(bytes *filename);
str *fsdecode(bytes *filename);
str *fsdecode(str *filename);

/* os.fspath() is the identity function for the str/bytes paths that
 * shedskin supports (no os.PathLike protocol) */
template <class T> T *fspath(T *path) {
    return path;
}

void *remove(str *a);
void *rmdir(str *a);
void *removedirs(str *name_);
void *mkdir(str *path, __ss_int mode=0777);
void *makedirs(str *name_, __ss_int mode=0777, __ss_bool exist_ok=False, __ss_int parent_mode=-1);
void *abort();
__ss_int system(str *c);
void *unlink(str *path);

class namedtuple : public pyobj {
public:
    tuple2<__ss_int, __ss_int> *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);
    str *__repr__();
    virtual __ss_int __len__() = 0;
    virtual __ss_int __getitem__(__ss_int i) = 0;

    /* iteration (and so unpacking) goes through __getitem__ */
    typedef __ss_int for_in_unit;
    typedef __ss_int for_in_loop;
    inline __ss_int for_in_init() { return 0; }
    inline bool for_in_has_next(__ss_int i) { return i < __len__(); }
    inline __ss_int for_in_next(__ss_int &i) { return __getitem__(i++); }
};

extern class_ *cl___cstat;
class __cstat : public namedtuple {
public:
    __ss_int st_mode, st_ino, st_dev, st_rdev, st_nlink, st_uid, st_gid, st_size, st_blksize, st_blocks;
    __ss_float __ss_st_mtime, __ss_st_atime, __ss_st_ctime; /* float seconds, as in CPython */
    __ss_int st_atime_ns, st_mtime_ns, st_ctime_ns;
    __ss_int __atime_s, __mtime_s, __ctime_s; /* integer seconds, for indexing (items 7-9) */

    __cstat(str *path, __ss_int t);
    __cstat(__ss_int fd);
    void fill_er_up();

    __ss_int __len__();
    __ss_int __getitem__(__ss_int i);

};

__cstat *stat(str *path);
__cstat *stat(__ss_bool follow_symlinks, str *path); /* follow_symlinks is keyword-only */
__cstat *lstat(str *path);
__cstat *fstat(__ss_int fd);

extern class_ *cl_DirEntry;
class DirEntry : public pyobj {
public:
    str *name, *path;
    std::filesystem::directory_entry __entry; /* not exposed to Python side */

    DirEntry() { __class__ = cl_DirEntry; }
    DirEntry(const std::filesystem::directory_entry &entry);

    __ss_bool is_dir(__ss_bool follow_symlinks=True);
    __ss_bool is_file(__ss_bool follow_symlinks=True);
    __ss_bool is_symlink();
    __ss_bool is_junction();
    __ss_int inode();
    __cstat *stat(__ss_bool follow_symlinks=True);
    str *__repr__();
};

list<DirEntry *> *scandir(str *path=0);

typedef tuple3<str *, list<str *> *, list<str *> *> __walk_tuple;

typedef std::function<void(OSError *)> __walk_onerror;

class __walk_iter : public __iter<__walk_tuple *> {
public:
    __ss_bool topdown, followlinks;
    __walk_onerror onerror;      /* called with the OSError for directories that cannot be scanned */
    str *top;
    __GC_VECTOR(str *) pending;  /* directories still to be scanned (topdown) */
    __walk_tuple *last;          /* last yielded tuple; its dirnames may have been pruned by the caller */
    __GC_VECTOR(__walk_tuple *) results; /* precomputed post-order results (bottom-up) */
    size_t pos;
    bool collected;              /* bottom-up results computed (lazily, on the first __next__) */

    __walk_iter(str *top, __ss_bool topdown, __ss_bool followlinks, __walk_onerror onerror=nullptr);
    __walk_tuple *__scan(str *top, __GC_VECTOR(str *) &subdirs);
    void __onerror(str *path, std::error_code ec);
    void __collect(str *top);
    __walk_tuple *__next__();
};

__walk_iter *walk(str *top, __ss_bool topdown=True, void *onerror=0, __ss_bool followlinks=False);

/* onerror=<function>: the callback's argument type comes from type inference
   (normally OSError *, but any base class of it works as well) */
template<class R, class A> __walk_iter *walk(str *top, __ss_bool topdown, R (*onerror)(A), __ss_bool followlinks=False) {
    if(!onerror)
        return new __walk_iter(top, topdown, followlinks);
    return new __walk_iter(top, topdown, followlinks, [onerror](OSError *e) { onerror(e); });
}

str *strerror(__ss_int i);

void *putenv(str* varname, str* value);
__ss_int umask(__ss_int newmask);
__ss_int chmod(str* path, __ss_int val);
void *fchmod(__ss_int fd, __ss_int mode);
void *renames(str* old, str* _new);
tuple2<__ss_int,__ss_int>* pipe();
__ss_int dup(__ss_int f1);
__ss_int dup2(__ss_int f1, __ss_int f2, __ss_bool inheritable=True);
void *close(__ss_int fd);
__ss_int open(str *name_, __ss_int flags, __ss_int mode=0777);
file* fdopen(__ss_int fd, str* mode=NULL, __ss_int bufsize=-1);
bytes *read(__ss_int fd, __ss_int n);
__ss_int write(__ss_int fd, bytes *s);
__ss_int readinto(__ss_int fd, bytes *buffer);
void *reload_environ();

class popen_pipe : public file {
public:
    popen_pipe(str *cmd, str *mode=0);
    popen_pipe(FILE* pipe=0) : file(pipe) {}

    void *close();
};

popen_pipe* popen(str* cmd);
popen_pipe* popen(str* cmd, str* mode);
popen_pipe* popen(str* cmd, str* mode, __ss_int bufsize);

void _exit(__ss_int code);

/* os.utime(path, times=None, *, ns=None): the keyword-only ns comes first */
void *__utime_now(str *path);
void *__utime_float(str *path, __ss_float atime, __ss_float mtime);
void *__utime_ns(str *path, __ss_int atime_ns, __ss_int mtime_ns);
[[noreturn]] void __utime_error(const char *msg);

template<class T> inline void __utime_check_pair(T *t, const char *msg) {
    if(t->__len__() != 2)
        __utime_error(msg);
}

void *utime(void *ns, str *path, void *times);
template<class T> void *utime(void *, str *path, T *times) {
    __utime_check_pair(times, "utime: 'times' must be either a tuple of two numbers or None");
    return __utime_float(path, (__ss_float)times->__getfirst__(), (__ss_float)times->__getsecond__());
}
template<class N> void *utime(N *ns, str *path, void *) {
    __utime_check_pair(ns, "utime: 'ns' must be a tuple of two ints");
    return __utime_ns(path, (__ss_int)ns->__getfirst__(), (__ss_int)ns->__getsecond__());
}
template<class N, class T> void *utime(N *, str *, T *) {
    __utime_error("utime: you may specify either 'times' or 'ns' but not both");
}

bytes *urandom(__ss_int n);
bytes *getrandom(__ss_int size, __ss_int flags=0);

__ss_bool isatty(__ss_int fd);

void *unsetenv(str* var);
__ss_int lseek(__ss_int fd, __ss_int pos, __ss_int how);

/* available on both posix and windows (windows versions in __init__.cpp) */
void *symlink(str *src, str *dst, __ss_bool target_is_directory=False);
__ss_int getpid();
__ss_int getppid();
void *ftruncate(__ss_int fd, __ss_int n);
void *fsync(__ss_int fd);
__ss_bool access(str *path, __ss_int mode);

extern class_ *cl_times_result;
class times_result : public pyobj {
public:
    __ss_float user, system, children_user, children_system, elapsed;

    times_result(__ss_float user, __ss_float system, __ss_float children_user, __ss_float children_system, __ss_float elapsed);
    times_result(tuple<__ss_float> *t);
    times_result(tuple<__ss_int> *t);

    tuple<__ss_float> *__tuple();
    __ss_int __len__();
    __ss_float __getitem__(__ss_int i);
    tuple<__ss_float> *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);
    __ss_bool __contains__(__ss_float x);
    __ss_int count(__ss_float x);
    __ss_int index(__ss_float x, __ss_int start, __ss_void_struct stop); /* stop not given */
    __ss_int index(__ss_float x, __ss_int start, __ss_int stop);
    str *__repr__();

    /* iteration (and so unpacking) goes through __getitem__ */
    typedef __ss_float for_in_unit;
    typedef __ss_int for_in_loop;
    inline __ss_int for_in_init() { return 0; }
    inline bool for_in_has_next(__ss_int i) { return i < 5; }
    inline __ss_float for_in_next(__ss_int &i) { return __getitem__(i++); }
};

times_result *times();

void *truncate(str *path, __ss_int length);
void *closerange(__ss_int fd_low, __ss_int fd_high);
__ss_int waitstatus_to_exitcode(__ss_int status);
__ss_bool get_inheritable(__ss_int fd);
void *set_inheritable(__ss_int fd, __ss_bool inheritable);
__ss_bool get_blocking(__ss_int fd);
void *set_blocking(__ss_int fd, __ss_bool blocking);
str *device_encoding(__ss_int fd);

extern class_ *cl_terminal_size;
class terminal_size : public namedtuple {
public:
    __ss_int columns, lines;

    terminal_size(__ss_int columns, __ss_int lines);
    terminal_size(tuple<__ss_int> *t);

    __ss_int __len__();
    __ss_int __getitem__(__ss_int i);
    str *__repr__();
};

terminal_size *get_terminal_size(__ss_int fd=1);

/* process management and links, available on both posix and windows */
void *kill(__ss_int pid, __ss_int sig);
tuple2<__ss_int, __ss_int> *waitpid(__ss_int pid, __ss_int options);
void *link(str *src, str *dst);
str *readlink(str *path);
str *getlogin();

void *execv(str *file, list<str*> *args);
void *execvp(str *file, list<str*> *args);
void *execve(str *file, list<str*> *args, dict<str *, str *> *env);
void *execvpe(str *file, list<str*> *args, dict<str *, str *> *env);

__ss_int spawnv(__ss_int mode, str *file, list<str *> *args);
__ss_int spawnvp(__ss_int mode, str *file, list<str *> *args);
__ss_int spawnve(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env);
__ss_int spawnvpe(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env);

template <class ... Args> void *execlp(__ss_int n, str *file, Args ... args) {
    list<str *> *vals = new list<str *>();
    (vals->append(args), ...);
    execvp(file, vals);
    return NULL;
}

template <class ... Args> void *execl(__ss_int n, str *file, Args ... args) {
    list<str *> *vals = new list<str *>();
    (vals->append(args), ...);
    execv(file, vals);
    return NULL;
}


template <class ... Args> void *execle(__ss_int n, str *file, dict<str *, str *> *env, Args ... args) {
    list<str *> *vals = new list<str *>();
    (vals->append(args), ...);
    execve(file, vals, env);
    return NULL;
}

template <class ... Args> void *execlpe(__ss_int n, str *file, dict<str *, str *> *env, Args ... args) {
    list<str *> *vals = new list<str *>();
    (vals->append(args), ...);
    execvpe(file, vals, env);
    return NULL;
}


template <class ... Args> __ss_int spawnl(__ss_int n, __ss_int mode, str *file, Args ... args) {
    list<str *> *vals = new list<str *>();
    (vals->append(args), ...);
    return spawnv(mode, file, vals);
}

template <class ... Args> __ss_int spawnlp(__ss_int n, __ss_int mode, str *file, Args ... args) {
    list<str *> *vals = new list<str *>();
    (vals->append(args), ...);
    return spawnvp(mode, file, vals);
}

template <class ... Args> __ss_int spawnle(__ss_int n, __ss_int mode, str *file, dict<str *, str *> *env, Args ... args) {
    list<str *> *vals = new list<str *>();
    (vals->append(args), ...);
    return spawnve(mode, file, vals, env);
}

template <class ... Args> __ss_int spawnlpe(__ss_int n, __ss_int mode, str *file, dict<str *, str *> *env, Args ... args) {
    list<str *> *vals = new list<str *>();
    (vals->append(args), ...);
    return spawnvpe(mode, file, vals, env);
}


#ifndef WIN32
__ss_int __ss_WCOREDUMP(__ss_int status);
__ss_int __ss_WEXITSTATUS(__ss_int status);
__ss_int __ss_WIFCONTINUED(__ss_int status);
__ss_int __ss_WIFEXITED(__ss_int status);
__ss_int __ss_WIFSIGNALED(__ss_int status);
__ss_int __ss_WIFSTOPPED(__ss_int status);
__ss_int __ss_WSTOPSIG(__ss_int status);
__ss_int __ss_WTERMSIG(__ss_int status);

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
void *setreuid(__ss_int ruid, __ss_int euid);
void *setregid(__ss_int rgid, __ss_int egid);
__ss_int getsid(__ss_int pid);
__ss_int setsid();
__ss_int tcgetpgrp(__ss_int fd);
void *tcsetpgrp(__ss_int fd, __ss_int pg);

void *lchown(str *path, __ss_int uid, __ss_int gid);

list<__ss_int> *getgroups();
void *setgroups(pyseq<__ss_int> *groups);

void *fchdir(__ss_int f1);
void *fdatasync(__ss_int f1);
void *chown(str *path, __ss_int uid, __ss_int gid);
void *chroot(str *path);

str *ctermid();
str *ttyname(__ss_int fd);

extern class_ *cl_uname_result;
class uname_result : public pyobj {
public:
    str *sysname, *nodename, *release, *version, *machine;

    uname_result(str *sysname, str *nodename, str *release, str *version, str *machine);
    uname_result(tuple<str *> *t);

    tuple<str *> *__tuple();
    __ss_int __len__();
    str *__getitem__(__ss_int i);
    tuple<str *> *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);
    __ss_bool __contains__(str *x);
    __ss_int count(str *x);
    __ss_int index(str *x, __ss_int start, __ss_void_struct stop); /* stop not given */
    __ss_int index(str *x, __ss_int start, __ss_int stop);
    str *__repr__();

    /* iteration (and so unpacking) goes through __getitem__ */
    typedef str *for_in_unit;
    typedef __ss_int for_in_loop;
    inline __ss_int for_in_init() { return 0; }
    inline bool for_in_has_next(__ss_int i) { return i < 5; }
    inline str *for_in_next(__ss_int &i) { return __getitem__(i++); }
};

uname_result *uname();

__ss_int fork();
tuple2<__ss_int, __ss_int> *forkpty();

tuple2<__ss_int, __ss_int> *openpty();

tuple2<__ss_int, __ss_int> *wait();

__ss_int nice(__ss_int n);

void *killpg(__ss_int pgid, __ss_int sig);

__ss_int pathconf(str *path, str *name_);
__ss_int pathconf(str *path, __ss_int name_);
__ss_int fpathconf(__ss_int fd, str *name_);
__ss_int fpathconf(__ss_int fd, __ss_int name_);
str *confstr(str *name_);
str *confstr(__ss_int name_);
__ss_int sysconf(str *name_);
__ss_int sysconf(__ss_int name_);


tuple2<__ss_float, __ss_float> *getloadavg();
void *mkfifo(str *path, __ss_int mode=438);



__ss_int __ss_makedev(__ss_int major, __ss_int minor);
__ss_int __ss_major(__ss_int dev);
__ss_int __ss_minor(__ss_int dev);

void *mknod(str *filename, __ss_int mode=0600, __ss_int device=0);

#endif

void __init();

} // module namespace
#endif
