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

class stat_result;

/* dir_fd (and src_dir_fd/dst_dir_fd) arguments: a None is cast to void *
   (see cpp.py), so it cannot pass as fd 0; __SS_DIR_FD_CWD stands for no
   dir_fd (AT_FDCWD). keyword-only arguments come first, in reverse */
#define __SS_DIR_FD_CWD (-100)
inline int __ss_dirfd(void *) { return __SS_DIR_FD_CWD; }
inline int __ss_dirfd(__ss_int dir_fd) { return __ss_cint(dir_fd); }
[[noreturn]] void __ss_dir_fd_unavailable(const char *func); /* (windows) */

void *__rename_at(int src_dir_fd, str *a, int dst_dir_fd, str *b, bool replace);
void *__unlink_at(int dir_fd, str *path, bool dir, const char *func);
void *__mkdir_at(int dir_fd, str *path, __ss_int mode);
__ss_int __open_at(int dir_fd, str *path, __ss_int flags, __ss_int mode);
void *__symlink_at(str *src, int dir_fd, str *dst);
str *__readlink_at(int dir_fd, str *path);
void *__mkfifo_at(int dir_fd, str *path, __ss_int mode);
void *__mknod_at(int dir_fd, str *path, __ss_int mode, __ss_int device);

/* bytes paths: like CPython, these give bytes where a str path gives str.
   the bytes overloads go through fsdecode()/fsencode(), which round-trip
   exactly (surrogateescape), and then share the str implementation */
list<str *> *listdir(str *path);
list<bytes *> *listdir(bytes *path);
list<str *> *listdir(void *path=0); /* listdir(None), see cpp.py */
list<str *> *listdir(__ss_int fd); /* (as cpython: not on windows) */
str *getcwd();
bytes *getcwdb();
void *chdir(str *dir);
void *chdir(__ss_int fd); /* (fchdir; as cpython: not on windows) */
str *getenv(str *name_, str *default_=0);
list<str *> *get_exec_path(dict<str *, str *> *env=0);
void *rename(str *a, str *b);
void *replace(str *a, str *b);
template<class D1, class D2> void *rename(D2 dst_dir_fd, D1 src_dir_fd, str *a, str *b) {
    if(__ss_dirfd(src_dir_fd) == __SS_DIR_FD_CWD && __ss_dirfd(dst_dir_fd) == __SS_DIR_FD_CWD)
        return rename(a, b);
    return __rename_at(__ss_dirfd(src_dir_fd), a, __ss_dirfd(dst_dir_fd), b, false);
}
template<class D1, class D2> void *replace(D2 dst_dir_fd, D1 src_dir_fd, str *a, str *b) {
    if(__ss_dirfd(src_dir_fd) == __SS_DIR_FD_CWD && __ss_dirfd(dst_dir_fd) == __SS_DIR_FD_CWD)
        return replace(a, b);
    return __rename_at(__ss_dirfd(src_dir_fd), a, __ss_dirfd(dst_dir_fd), b, true);
}
__ss_int cpu_count();
__ss_int process_cpu_count();

/* utf-8 + surrogateescape (PEP 383), the only filesystem encoding for now;
   like cpython, bytes pass through fsencode() and str through fsdecode() */
bytes *fsencode(str *filename);
bytes *fsencode(bytes *filename);
str *fsdecode(bytes *filename);
str *fsdecode(str *filename);

/* os.fspath(): the identity for str/bytes, otherwise __fspath__() (DirEntry,
 * user classes). other functions taking a path do not accept os.PathLike */
inline str *fspath(str *path) { return path; }
inline bytes *fspath(bytes *path) { return path; }
template <class T> auto fspath(T *path) {
    return path->__fspath__();
}

void *remove(str *a);
void *rmdir(str *a);
template<class D> void *remove(D dir_fd, str *path) {
    return __ss_dirfd(dir_fd) == __SS_DIR_FD_CWD ? remove(path) : __unlink_at(__ss_dirfd(dir_fd), path, false, "remove");
}
template<class D> void *rmdir(D dir_fd, str *path) {
    return __ss_dirfd(dir_fd) == __SS_DIR_FD_CWD ? rmdir(path) : __unlink_at(__ss_dirfd(dir_fd), path, true, "rmdir");
}
void *removedirs(str *name_);
void *mkdir(str *path, __ss_int mode=0777);
template<class D> void *mkdir(D dir_fd, str *path, __ss_int mode) {
    return __ss_dirfd(dir_fd) == __SS_DIR_FD_CWD ? mkdir(path, mode) : __mkdir_at(__ss_dirfd(dir_fd), path, mode);
}
void *makedirs(str *name_, __ss_int mode=0777, __ss_bool exist_ok=False, __ss_int parent_mode=-1);
void *abort();
__ss_int system(str *c);
void *unlink(str *path);
template<class D> void *unlink(D dir_fd, str *path) {
    return __ss_dirfd(dir_fd) == __SS_DIR_FD_CWD ? unlink(path) : __unlink_at(__ss_dirfd(dir_fd), path, false, "unlink");
}

/* the struct sequences below (stat_result, terminal_size..) are tuples, with
   the items also as attributes: items are set once, as they are immutable */

extern class_ *cl_stat_result;
class stat_result : public tuple2<__ss_int, __ss_int> {
public:
    __ss_int st_mode, st_ino, st_dev, st_rdev, st_nlink, st_uid, st_gid, st_size, st_blksize, st_blocks;
    __ss_float __ss_st_mtime, __ss_st_atime, __ss_st_ctime; /* float seconds, as in CPython */
    __ss_int st_atime_ns, st_mtime_ns, st_ctime_ns;
    __ss_int __atime_s, __mtime_s, __ctime_s; /* integer seconds, which are items 7-9 */

    stat_result(str *path, __ss_int t);
    stat_result(__ss_int fd);
    stat_result(__ss_int dir_fd, str *path, bool follow_symlinks); /* os.stat(path, dir_fd=..) */
    void fill_er_up();
    void __set_items();
    str *__repr__() override;
    __SS_STRUCTSEQ_COPY(stat_result)
};

stat_result *stat(str *path);
stat_result *stat(bytes *path);
stat_result *stat(__ss_bool follow_symlinks, str *path); /* follow_symlinks is keyword-only */
/* os.stat(path, *, dir_fd=None, follow_symlinks=True): the keyword-only
   arguments come first (in reverse); a None dir_fd is cast to void * (see
   cpp.py), and path may also be an fd */
stat_result *stat(__ss_bool follow_symlinks, void *dir_fd, str *path);
stat_result *stat(__ss_bool follow_symlinks, void *dir_fd, bytes *path);
stat_result *stat(__ss_bool follow_symlinks, __ss_int dir_fd, str *path);
stat_result *stat(__ss_bool follow_symlinks, __ss_int dir_fd, bytes *path);
stat_result *stat(__ss_bool follow_symlinks, void *dir_fd, __ss_int fd);
stat_result *stat(__ss_bool follow_symlinks, __ss_int dir_fd, __ss_int fd);
stat_result *stat(__ss_bool follow_symlinks, bytes *path);
stat_result *lstat(str *path);
stat_result *lstat(bytes *path);
stat_result *lstat(void *dir_fd, str *path); /* lstat(path, *, dir_fd=None) */
stat_result *lstat(void *dir_fd, bytes *path);
stat_result *lstat(__ss_int dir_fd, str *path);
stat_result *lstat(__ss_int dir_fd, bytes *path);
stat_result *fstat(__ss_int fd);

extern class_ *cl_DirEntry;
class DirEntry : public pyobj {
public:
    str *name, *path;
    /* cached type (from d_type, without following symlinks). not the
       std::filesystem::directory_entry itself: its path lives in malloc'd
       memory, which leaks as the GC never runs destructors */
    std::filesystem::file_type __type; /* not exposed to Python side */
    int __dir_fd = -1; /* scandir(fd): name is relative to this (as cpython, path is just name) */
    __ss_int __ino = 0; /* (scandir(fd): d_ino) */

    DirEntry() : __type(std::filesystem::file_type::unknown) { __class__ = cl_DirEntry; }
    DirEntry(const std::filesystem::directory_entry &entry);
    DirEntry(int dir_fd, str *name, std::filesystem::file_type type, __ss_int ino);

    __ss_bool is_dir(__ss_bool follow_symlinks=True);
    __ss_bool is_file(__ss_bool follow_symlinks=True);
    __ss_bool is_symlink();
    __ss_bool is_junction();
    __ss_int inode();
    stat_result *stat(__ss_bool follow_symlinks=True);
    str *__repr__();
    str *__fspath__() { return path; }
};

/* entries are read eagerly; close() (or leaving a 'with' block) drops them,
   after which iteration stops, as in CPython */
extern class_ *cl_ScandirIterator;
class ScandirIterator : public __iter<DirEntry *> {
public:
    list<DirEntry *> *entries;
    __ss_int pos;

    ScandirIterator(list<DirEntry *> *entries_) : entries(entries_), pos(0) { __class__ = cl_ScandirIterator; }

    ScandirIterator *__iter__() { return this; }
    DirEntry *__next__();
    DirEntry *__get_next();
    ScandirIterator *__enter__() { return this; }
    void *__exit__() { close(); return NULL; }
    void *close() { entries = NULL; return NULL; }
    str *__repr__();
};

ScandirIterator *scandir(str *path=0);
ScandirIterator *scandir(void *); /* scandir(None), see cpp.py */
ScandirIterator *scandir(__ss_int fd); /* (as cpython: not on windows) */

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
void *chmod(str* path, __ss_int val);
void *fchmod(__ss_int fd, __ss_int mode);
/* chmod(path, mode, *, dir_fd=None, follow_symlinks=True); path may be an fd */
void *__chmod_at(int dir_fd, str *path, __ss_int mode, bool follow_symlinks);
[[noreturn]] void __ss_fd_with(const char *func, bool dir_fd); /* fd and dir_fd/follow_symlinks */
template<class D> void *chmod(__ss_bool follow_symlinks, D dir_fd, str *path, __ss_int mode) {
    if(__ss_dirfd(dir_fd) == __SS_DIR_FD_CWD && follow_symlinks)
        return chmod(path, mode);
    return __chmod_at(__ss_dirfd(dir_fd), path, mode, follow_symlinks);
}
template<class D> void *chmod(__ss_bool, D, __ss_int fd, __ss_int mode) { /* (as cpython: dir_fd and follow_symlinks are ignored) */
    return fchmod(fd, mode);
}
void *renames(str* old, str* _new);
tuple2<__ss_int,__ss_int>* pipe();
__ss_int dup(__ss_int f1);
__ss_int dup2(__ss_int f1, __ss_int f2, __ss_bool inheritable=True);
void *close(__ss_int fd);
__ss_int open(str *name_, __ss_int flags, __ss_int mode=0777);
template<class D> __ss_int open(D dir_fd, str *path, __ss_int flags, __ss_int mode) {
    return __ss_dirfd(dir_fd) == __SS_DIR_FD_CWD ? open(path, flags, mode) : __open_at(__ss_dirfd(dir_fd), path, flags, mode);
}
file* fdopen(__ss_int fd, str* mode=NULL, __ss_int buffering=-1, str *encoding=NULL, str *errors=NULL, str *newline=NULL);
file_binary* fdopen_binary(__ss_int fd, str* mode=NULL, __ss_int buffering=-1, str *encoding=NULL, str *errors=NULL, str *newline=NULL);
bytes *read(__ss_int fd, __ss_int n);
__ss_int write(__ss_int fd, bytes *s);
__ss_int readinto(__ss_int fd, bytes *buffer);
void *reload_environ();

/* popen_pipe.close() returns the exit status (0 for None), so it cannot
   override file::close, which returns void *. __popen_file does that, so
   closing through a file * (or by __exit__) still calls pclose */
#if defined(__GNUC__) || defined(__clang__) /* (MSVC: C4068) */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Woverloaded-virtual"
#endif
class __popen_file : public file {
public:
    __ss_int status = 0;

    __popen_file(FILE* pipe=0) : file(pipe) {}

    void *close();
};

class popen_pipe : public __popen_file {
public:
    popen_pipe(str *cmd, str *mode=0);
    popen_pipe(FILE* pipe=0) : __popen_file(pipe) {}

    __ss_int close(__ss_int=0); /* (hides __popen_file::close on purpose) */
    popen_pipe *__enter__() { return this; } /* (CPython: no closed check) */
};
#if defined(__GNUC__) || defined(__clang__)
#pragma GCC diagnostic pop
#endif

popen_pipe* popen(str* cmd);
popen_pipe* popen(str* cmd, str* mode);
popen_pipe* popen(str* cmd, str* mode, __ss_int bufsize);

void _exit(__ss_int code);

/* os.utime(path, times=None, *, ns=None, dir_fd=None, follow_symlinks=True):
   the keyword-only arguments come first (in reverse); a None is cast to
   void * (see cpp.py), so a None dir_fd cannot pass as fd 0 */
void *__utime_now(str *path, int dir_fd, bool follow_symlinks);
void *__utime_float(str *path, __ss_float atime, __ss_float mtime, int dir_fd, bool follow_symlinks);
void *__utime_ns(str *path, __ss_int atime_ns, __ss_int mtime_ns, int dir_fd, bool follow_symlinks);
[[noreturn]] void __utime_error(const char *msg);

template<class T> inline void __utime_check_pair(T *t, const char *msg) {
    if(t->__len__() != 2)
        __utime_error(msg);
}

template<class D> void *utime(__ss_bool follow_symlinks, D dir_fd, void *, str *path, void *) {
    return __utime_now(path, __ss_dirfd(dir_fd), follow_symlinks);
}
template<class D, class T> void *utime(__ss_bool follow_symlinks, D dir_fd, void *, str *path, T *times) {
    __utime_check_pair(times, "utime: 'times' must be either a tuple of two numbers or None");
    return __utime_float(path, (__ss_float)times->__getfirst__(), (__ss_float)times->__getsecond__(), __ss_dirfd(dir_fd), follow_symlinks);
}
template<class D, class N> void *utime(__ss_bool follow_symlinks, D dir_fd, N *ns, str *path, void *) {
    __utime_check_pair(ns, "utime: 'ns' must be a tuple of two ints");
    return __utime_ns(path, (__ss_int)ns->__getfirst__(), (__ss_int)ns->__getsecond__(), __ss_dirfd(dir_fd), follow_symlinks);
}
template<class D, class N, class T> void *utime(__ss_bool, D, N *, str *, T *) {
    __utime_error("utime: you may specify either 'times' or 'ns' but not both");
}

bytes *urandom(__ss_int n);
bytes *getrandom(__ss_int size, __ss_int flags=0);

__ss_bool isatty(__ss_int fd);

void *unsetenv(str* var);
__ss_int lseek(__ss_int fd, __ss_int pos, __ss_int how);

/* available on both posix and windows (windows versions in __init__.cpp) */
void *symlink(str *src, str *dst, __ss_bool target_is_directory=False);
template<class D> void *symlink(D dir_fd, str *src, str *dst, __ss_bool target_is_directory) {
    return __ss_dirfd(dir_fd) == __SS_DIR_FD_CWD ? symlink(src, dst, target_is_directory) : __symlink_at(src, __ss_dirfd(dir_fd), dst);
}
__ss_int getpid();
__ss_int getppid();
void *ftruncate(__ss_int fd, __ss_int n);
void *fsync(__ss_int fd);
__ss_bool access(str *path, __ss_int mode);
/* access(path, mode, *, dir_fd=None, effective_ids=False, follow_symlinks=True) */
__ss_bool __access_at(int dir_fd, str *path, __ss_int mode, bool effective_ids, bool follow_symlinks);
template<class D> __ss_bool access(__ss_bool follow_symlinks, __ss_bool effective_ids, D dir_fd, str *path, __ss_int mode) {
    if(__ss_dirfd(dir_fd) == __SS_DIR_FD_CWD && !effective_ids && follow_symlinks)
        return access(path, mode);
    return __access_at(__ss_dirfd(dir_fd), path, mode, effective_ids, follow_symlinks);
}

extern class_ *cl_times_result;
class times_result : public tuple2<__ss_float, __ss_float> {
public:
    __ss_float user, system, children_user, children_system, elapsed;

    times_result(__ss_float user, __ss_float system, __ss_float children_user, __ss_float children_system, __ss_float elapsed);
    times_result(tuple<__ss_float> *t);
    times_result(tuple<__ss_int> *t);

    str *__repr__() override;
    __SS_STRUCTSEQ_COPY(times_result)
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
class terminal_size : public tuple2<__ss_int, __ss_int> {
public:
    __ss_int columns, lines;

    terminal_size(__ss_int columns, __ss_int lines);
    terminal_size(tuple<__ss_int> *t);

    str *__repr__() override;
    __SS_STRUCTSEQ_COPY(terminal_size)
};

terminal_size *get_terminal_size(__ss_int fd=1);

/* process management and links, available on both posix and windows */
void *kill(__ss_int pid, __ss_int sig);
tuple2<__ss_int, __ss_int> *waitpid(__ss_int pid, __ss_int options);
void *link(str *src, str *dst);
/* link(src, dst, *, src_dir_fd=None, dst_dir_fd=None, follow_symlinks=True):
   as CPython, plain link() (which does not follow a symlink on linux)
   unless a dir_fd is given or follow_symlinks is False */
void *__link_at(int src_dir_fd, str *src, int dst_dir_fd, str *dst, bool follow_symlinks);
template<class D1, class D2> void *link(__ss_bool follow_symlinks, D2 dst_dir_fd, D1 src_dir_fd, str *src, str *dst) {
    if(__ss_dirfd(src_dir_fd) == __SS_DIR_FD_CWD && __ss_dirfd(dst_dir_fd) == __SS_DIR_FD_CWD && follow_symlinks)
        return link(src, dst);
    return __link_at(__ss_dirfd(src_dir_fd), src, __ss_dirfd(dst_dir_fd), dst, follow_symlinks);
}
str *readlink(str *path);
template<class D> str *readlink(D dir_fd, str *path) {
    return __ss_dirfd(dir_fd) == __SS_DIR_FD_CWD ? readlink(path) : __readlink_at(__ss_dirfd(dir_fd), path);
}
str *getlogin();

void *execv(str *file, list<str*> *args);
void *execvp(str *file, list<str*> *args);
void *execve(str *file, list<str*> *args, dict<str *, str *> *env);
void *execvpe(str *file, list<str*> *args, dict<str *, str *> *env);

__ss_int spawnv(__ss_int mode, str *file, list<str *> *args);
__ss_int spawnvp(__ss_int mode, str *file, list<str *> *args);
__ss_int spawnve(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env);
__ss_int spawnvpe(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env);

/* argv as a tuple */
inline void *execv(str *file, tuple<str *> *args) { return execv(file, new list<str *>(args)); }
inline void *execvp(str *file, tuple<str *> *args) { return execvp(file, new list<str *>(args)); }
inline void *execve(str *file, tuple<str *> *args, dict<str *, str *> *env) { return execve(file, new list<str *>(args), env); }
inline void *execvpe(str *file, tuple<str *> *args, dict<str *, str *> *env) { return execvpe(file, new list<str *>(args), env); }
inline __ss_int spawnv(__ss_int mode, str *file, tuple<str *> *args) { return spawnv(mode, file, new list<str *>(args)); }
inline __ss_int spawnvp(__ss_int mode, str *file, tuple<str *> *args) { return spawnvp(mode, file, new list<str *>(args)); }
inline __ss_int spawnve(__ss_int mode, str *file, tuple<str *> *args, dict<str *, str *> *env) { return spawnve(mode, file, new list<str *>(args), env); }
inline __ss_int spawnvpe(__ss_int mode, str *file, tuple<str *> *args, dict<str *, str *> *env) { return spawnvpe(mode, file, new list<str *>(args), env); }

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
__ss_bool __ss_WCOREDUMP(__ss_int status);
__ss_int __ss_WEXITSTATUS(__ss_int status);
__ss_bool __ss_WIFCONTINUED(__ss_int status);
__ss_bool __ss_WIFEXITED(__ss_int status);
__ss_bool __ss_WIFSIGNALED(__ss_int status);
__ss_bool __ss_WIFSTOPPED(__ss_int status);
__ss_int __ss_WSTOPSIG(__ss_int status);
__ss_int __ss_WTERMSIG(__ss_int status);

extern class_ *cl_statvfs_result;
class statvfs_result : public tuple2<__ss_int, __ss_int> {
public:
    __ss_int f_bsize, f_frsize, f_blocks, f_bfree, f_bavail, f_files, f_ffree, f_favail, f_flag, f_namemax, f_fsid;

    statvfs_result(str *path);
    statvfs_result(__ss_int fd);
    void fill_er_up();
    str *__repr__() override;
    __SS_STRUCTSEQ_COPY(statvfs_result)
};

statvfs_result *statvfs(str *path);
statvfs_result *fstatvfs(__ss_int fd);

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
void *setsid();
__ss_int tcgetpgrp(__ss_int fd);
void *tcsetpgrp(__ss_int fd, __ss_int pg);

void *lchown(str *path, __ss_int uid, __ss_int gid);

list<__ss_int> *getgroups();
void *setgroups(pyseq<__ss_int> *groups);

void *fchdir(__ss_int f1);
void *fdatasync(__ss_int f1);
void *chown(str *path, __ss_int uid, __ss_int gid);
/* chown(path, uid, gid, *, dir_fd=None, follow_symlinks=True); path may be an fd */
void *__chown_at(int dir_fd, str *path, __ss_int uid, __ss_int gid, bool follow_symlinks);
void *__fchown(__ss_int fd, __ss_int uid, __ss_int gid);
template<class D> void *chown(__ss_bool follow_symlinks, D dir_fd, str *path, __ss_int uid, __ss_int gid) {
    if(__ss_dirfd(dir_fd) == __SS_DIR_FD_CWD && follow_symlinks)
        return chown(path, uid, gid);
    return __chown_at(__ss_dirfd(dir_fd), path, uid, gid, follow_symlinks);
}
template<class D> void *chown(__ss_bool follow_symlinks, D dir_fd, __ss_int fd, __ss_int uid, __ss_int gid) {
    if(__ss_dirfd(dir_fd) != __SS_DIR_FD_CWD)
        __ss_fd_with("chown", true);
    if(!follow_symlinks)
        __ss_fd_with("chown", false);
    return __fchown(fd, uid, gid);
}
void *chroot(str *path);

str *ctermid();
str *ttyname(__ss_int fd);

extern class_ *cl_uname_result;
class uname_result : public tuple2<str *, str *> {
public:
    str *sysname, *nodename, *release, *version, *machine;

    uname_result(str *sysname, str *nodename, str *release, str *version, str *machine);
    uname_result(tuple<str *> *t);

    str *__repr__() override;
    __SS_STRUCTSEQ_COPY(uname_result)
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
template<class D> void *mkfifo(D dir_fd, str *path, __ss_int mode) {
    return __ss_dirfd(dir_fd) == __SS_DIR_FD_CWD ? mkfifo(path, mode) : __mkfifo_at(__ss_dirfd(dir_fd), path, mode);
}



__ss_int __ss_makedev(__ss_int major, __ss_int minor);
__ss_int __ss_major(__ss_int dev);
__ss_int __ss_minor(__ss_int dev);

void *mknod(str *filename, __ss_int mode=0600, __ss_int device=0);
template<class D> void *mknod(D dir_fd, str *path, __ss_int mode, __ss_int device) {
    return __ss_dirfd(dir_fd) == __SS_DIR_FD_CWD ? mknod(path, mode, device) : __mknod_at(__ss_dirfd(dir_fd), path, mode, device);
}

#endif

void __init();

} // module namespace
#endif
