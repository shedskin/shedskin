/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "__init__.hpp"
#include "path.hpp"

#include <cstdlib>
#include <cstring>
#include <sstream>
#include <sys/stat.h>
#include <stdio.h>
#include <climits>
#include <errno.h>
#include <sys/types.h>
#include <fcntl.h>
#include <filesystem>
#include <system_error>
#include <thread>

#ifdef _MSC_VER
#include <direct.h>
#include <io.h>
#elif defined(WIN32)
#include <io.h> /* _get_osfhandle */
#else
#include <sys/time.h>
#include <utime.h>
#include <unistd.h>
#endif

#ifndef WIN32
#include <sys/times.h>
#include <sys/wait.h>
#include <sys/utsname.h>
#include <sys/statvfs.h>
#include <dirent.h> /* listdir(fd) */

#if !defined(__APPLE__) && !defined(__FreeBSD__)
#include <sys/sysmacros.h>
#endif

#include <grp.h>
#include <sysexits.h>
#include <sys/ioctl.h>
#include <signal.h>
#if defined(__linux__) && defined(__has_include)
#if __has_include(<sys/random.h>)
#include <sys/random.h> /* getrandom(2): needs no fd, as CPython's os.urandom */
#define __SS_HAVE_GETRANDOM
#endif
#endif
#endif

#ifdef __linux__
#include <sched.h>
#endif

#ifdef WIN32
#ifdef _MSC_VER
#ifndef NOMINMAX
#define NOMINMAX
#endif
#endif
#include <windows.h>
#include <tlhelp32.h>
#include <io.h>
#include <process.h> /* _wexecv, _wspawnv, _cwait */
#endif

#ifdef __FreeBSD__
#include <libutil.h>
extern char **environ;
#endif

#ifdef __APPLE__
#include <crt_externs.h>
#include <util.h>
#include <signal.h>
#define environ (*_NSGetEnviron())
#endif

#ifdef __sun
#include <sys/mkdev.h>
#include <sys/loadavg.h>
#include <signal.h>
extern char **environ;
#endif

#if !defined(__APPLE__) && !defined(__FreeBSD__) && !defined(__sun) && !defined(WIN32)
#include <pty.h>
#endif

namespace __os__ {

/* CPython's name for the os implementation module (in struct sequence errors) */
#ifdef WIN32
#define __SS_POSIX_MOD "nt"
#else
#define __SS_POSIX_MOD "posix"
#endif

/* as CPython's fildes_converter (fsync, fchdir, ..) */
static int __ss_fildes(__ss_int fd) {
    if (fd < 0)
        throw new ValueError(__add_strs(3, new str("file descriptor cannot be a negative integer ("), __str(fd), new str(")")));
    return __ss_cint(fd);
}

/* the msvc crt calls its invalid parameter handler (which aborts by default)
   for a bad file descriptor; like cpython, suppress that around calls that
   may legitimately receive one, so they fail with EBADF instead */
#ifdef _MSC_VER
static void __noop_iph(const wchar_t *, const wchar_t *, const wchar_t *, unsigned int, uintptr_t) {}
struct __suppress_iph {
    _invalid_parameter_handler old;
    __suppress_iph() { old = _set_thread_local_invalid_parameter_handler(__noop_iph); }
    ~__suppress_iph() { _set_thread_local_invalid_parameter_handler(old); }
};
#else
struct __suppress_iph { __suppress_iph() {} }; /* (avoid unused-variable warnings) */
#endif

#ifdef WIN32
/* map a win32 error code (GetLastError()) to errno, so __throw_oserror()
   picks the same OSError subclass as cpython does for the common cases */
[[noreturn]] static void __throw_winerror(DWORD err, str *fname=0, str *fname2=0) {
    switch(err) {
        case ERROR_FILE_NOT_FOUND:
        case ERROR_PATH_NOT_FOUND:
        case ERROR_INVALID_NAME:
        case ERROR_BAD_NETPATH: errno = ENOENT; break;
        case ERROR_ACCESS_DENIED:
        case ERROR_SHARING_VIOLATION:
        case ERROR_LOCK_VIOLATION: errno = EACCES; break;
        case ERROR_PRIVILEGE_NOT_HELD: errno = EPERM; break;
        case ERROR_ALREADY_EXISTS:
        case ERROR_FILE_EXISTS: errno = EEXIST; break;
        case ERROR_NOT_SAME_DEVICE: errno = EXDEV; break;
        case ERROR_DIRECTORY: errno = ENOTDIR; break;
        case ERROR_DIR_NOT_EMPTY: errno = ENOTEMPTY; break;
        case ERROR_NOT_ENOUGH_MEMORY:
        case ERROR_OUTOFMEMORY: errno = ENOMEM; break;
        default: errno = EINVAL; break;
    }
    __throw_oserror(fname, fname2);
}

/* str (code points) <-> native wide strings. (not via std::filesystem::path,
   whose conversions throw on lone surrogates) */
static std::wstring __to_wide(str *s, const char *func = 0, const char *arg = "path") {
    __ss_check_nul(s, func, arg);
    return __to_utf16<wchar_t>(s->unit);
}

static str *__from_wide(const wchar_t *w) {
    return new str(__from_utf16<wchar_t>(w, wcslen(w)));
}
#endif

/* str <-> std::filesystem::path. constructing a path from the code points
   directly would go through the standard codecvt, which throws on the lone
   surrogates that stand in for undecodable bytes (PEP 383); and on Windows
   path::string() converts to the (lossy) ansi code page. so use the native
   representation: utf-8 bytes (with surrogateescape) on posix, utf-16 on
   Windows. */
static std::filesystem::path __fspath(str *s, const char *func = 0, const char *arg = "path") {
#ifdef WIN32
    return std::filesystem::path(__to_wide(s, func, arg));
#else
    __ss_check_nul(s, func, arg);
    __GC_BYTES b = __to_utf8_se(s);
    return std::filesystem::path(std::string(b.data(), b.size()));
#endif
}

/* bytes from the os (posix): utf-8 with surrogateescape, as fsdecode() */
static inline str *__fsdecode_c(const char *b, size_t n) {
    str *s = new str();
    __decode_into(s->unit, b, n, __SS_ENC_UTF8, __SS_ERR_SURROGATEESCAPE, NULL);
    return s;
}

static str *__fsstr(const std::filesystem::path &p) {
    const auto &n = p.native();
#ifdef WIN32
    return new str(__from_utf16<wchar_t>(n.data(), n.size()));
#else
    /* as fsdecode(): strict utf-8 + surrogateescape, so an encoded surrogate
       (ed a0 80) gives three escapes, which round-trip (not a lone surrogate) */
    str *s = new str();
    __decode_into(s->unit, n.data(), n.size(), __SS_ENC_UTF8, __SS_ERR_SURROGATEESCAPE, NULL);
    return s;
#endif
}


str *linesep, *name;
dict<str *, str *> *__ss_environ;
dict<str *, __ss_int> *pathconf_names, *confstr_names, *sysconf_names;

struct stat sbuf;
#ifndef WIN32
struct statvfs vbuf;
#endif

const __ss_int MAXENTRIES = 4096; /* XXX fix functions that use this */

str *altsep, *curdir, *defpath, *devnull, *extsep, *pardir, *pathsep, *sep;

__ss_int __ss_F_OK, __ss_R_OK, __ss_W_OK, __ss_X_OK, __ss_NGROUPS_MAX, __ss_TMP_MAX, __ss_WCONTINUED, __ss_WNOHANG, __ss_WUNTRACED, __ss_O_RDONLY, __ss_O_WRONLY, __ss_O_RDWR, __ss_O_NDELAY, __ss_O_NONBLOCK, __ss_O_APPEND, __ss_O_DSYNC, __ss_O_RSYNC, __ss_O_SYNC, __ss_O_NOCTTY, __ss_O_CREAT, __ss_O_EXCL, __ss_O_TRUNC, __ss_O_BINARY, __ss_O_TEXT, __ss_O_LARGEFILE, __ss_O_SHLOCK, __ss_O_EXLOCK, __ss_O_NOINHERIT, __ss__O_SHORT_LIVED, __ss_O_TEMPORARY, __ss_O_RANDOM, __ss_O_SEQUENTIAL, __ss_O_ASYNC, __ss_O_DIRECT, __ss_O_DIRECTORY, __ss_O_NOFOLLOW, __ss_O_NOATIME, __ss_EX_OK, __ss_EX_USAGE, __ss_EX_DATAERR, __ss_EX_NOINPUT, __ss_EX_NOUSER, __ss_EX_NOHOST, __ss_EX_UNAVAILABLE, __ss_EX_SOFTWARE, __ss_EX_OSERR, __ss_EX_OSFILE, __ss_EX_CANTCREAT, __ss_EX_IOERR, __ss_EX_TEMPFAIL, __ss_EX_PROTOCOL, __ss_EX_NOPERM, __ss_EX_CONFIG, __ss_EX_NOTFOUND, __ss_P_WAIT, __ss_P_NOWAIT, __ss_P_OVERLAY, __ss_P_NOWAITO, __ss_P_DETACH, __ss_SEEK_SET, __ss_SEEK_CUR, __ss_SEEK_END, __ss_SEEK_DATA, __ss_SEEK_HOLE, __ss_GRND_NONBLOCK, __ss_GRND_RANDOM;

/* std::filesystem errors carry an error_code rather than setting errno
   (on Windows it is a system error code), so map it back to errno */
[[noreturn]] static void __throw_fs_error(std::filesystem::filesystem_error const& e, str *path) {
    std::error_condition c = e.code().default_error_condition();
    errno = (c.category() == std::generic_category()) ? c.value() : EIO;
    __throw_oserror(path);
}

list<str *> *listdir(str *path) {
    if(!path)
        path = new str(".");

    list<str *> *r = new list<str *>();

    try {
        for (const auto & entry : std::filesystem::directory_iterator(__fspath(path, "listdir")))
            r->append(__fsstr(entry.path().filename()));
    } catch (std::filesystem::filesystem_error const& e) {
        __throw_fs_error(e, path);
    }

    return r;
}

list<str *> *listdir(void *) {
    return listdir(new str("."));
}

list<str *> *listdir(__ss_int fd) {
#ifdef WIN32
    (void)fd;
    throw new TypeError(new str("listdir: path should be string, bytes, os.PathLike or None, not int"));
#else
    /* as cpython: read a dup of the fd from the start, leaving the fd open */
    int fd2 = ::dup(__ss_cint(fd));
    if(fd2 == -1)
        __throw_oserror();
    DIR *dir = ::fdopendir(fd2);
    if(!dir) {
        int e = errno;
        ::close(fd2);
        errno = e;
        __throw_oserror();
    }
    ::rewinddir(dir);
    list<str *> *r = new list<str *>();
    errno = 0;
    while(struct dirent *ent = ::readdir(dir)) {
        if(strcmp(ent->d_name, ".") != 0 && strcmp(ent->d_name, "..") != 0)
            r->append(__fsstr(std::filesystem::path(ent->d_name)));
    }
    int e = errno;
    ::rewinddir(dir); /* (shares the fd's position) */
    ::closedir(dir);
    if(e) {
        errno = e;
        __throw_oserror();
    }
    return r;
#endif
}

list<bytes *> *listdir(bytes *path) {
    list<str *> *names = listdir(fsdecode(path));

    list<bytes *> *r = new list<bytes *>();
    r->units.reserve(names->units.size());
    for (str *name : names->units)
        r->units.push_back(fsencode(name));

    return r;
}

str *getcwd() {
    str *r;
#ifdef WIN32
    wchar_t *d = ::_wgetcwd(0, 0);
    if (!d)
        __throw_oserror();
    r = __from_wide(d);
#else
    char *d = ::getcwd(0, 0); /* (glibc, bsd, macos: any length; 0 + errno on failure) */
    if (!d)
        __throw_oserror();
    r = new str();
    __decode_into(r->unit, d, strlen(d), __SS_ENC_UTF8, __SS_ERR_SURROGATEESCAPE, NULL);
#endif
    free(d);
    return r;
}

bytes *getcwdb() {
#ifdef WIN32
    return new bytes(__to_utf8(getcwd()->unit)); /* as CPython: fs encoding */
#else
    char *d = ::getcwd(0, 0); /* (any length: ERANGE past 255 bytes otherwise) */
    if (!d)
        __throw_oserror();
    bytes *r = new bytes(d);
    free(d);
    return r;
#endif
}

/* like CPython: utf-8 with surrogateescape on posix, so only U+DC80..U+DCFF
   escapes map back to bytes and other lone surrogates raise. Windows uses
   surrogatepass, which the lenient (wtf-8) internal conversions match */
bytes *fsencode(str *filename) {
#ifdef WIN32
    return new bytes(__to_utf8(filename->unit));
#else
    bytes *b = new bytes(1);
    __encode_into(b->unit, filename, __SS_ENC_UTF8, __SS_ERR_SURROGATEESCAPE, NULL);
    return b;
#endif
}

bytes *fsencode(bytes *filename) {
    return filename;
}

str *fsdecode(bytes *filename) {
#ifdef WIN32
    return new str(__from_utf8(filename->unit));
#else
    str *s = new str();
    __decode_into(s->unit, filename->unit.data(), filename->unit.size(), __SS_ENC_UTF8, __SS_ERR_SURROGATEESCAPE, NULL);
    return s;
#endif
}

str *fsdecode(str *filename) {
    return filename;
}

void *chdir(__ss_int fd) {
#ifdef WIN32
    (void)fd;
    throw new TypeError(new str("chdir: path should be string, bytes or os.PathLike, not int"));
#else
    if(::fchdir(__ss_cint(fd)) == -1)
        __throw_oserror();
    return NULL;
#endif
}

void *chdir(str *dir) {
#ifdef WIN32
    if(::_wchdir(__to_wide(dir, "chdir").c_str()) == -1)
#else
    if(::chdir(__ss_cpath(dir, "chdir")) == -1)
#endif
        __throw_oserror(dir);
    return NULL;
}

str *strerror(__ss_int i) {
    return new str(::strerror(__ss_cint(i)));
}

__ss_int system(str *c) {
    return std::system(__ss_cpath(c));
}

str *getenv(str *name_, str *default_) {
    /* like CPython, consult os.environ (so assignments to it are seen) */
#ifdef WIN32
    /* environment variable names are case-insensitive on Windows */
    str *key = name_->upper();
    for (auto const& [k, v] : __ss_environ->gcd)
        if (__eq(k->upper(), key))
            return v;
    return default_;
#else
    return __ss_environ->get(name_, default_);
#endif
}

void *rename(str *a, str *b) {
#ifdef WIN32
    if(::_wrename(__to_wide(a, "rename", "src").c_str(), __to_wide(b, "rename", "dst").c_str()) == -1) {
#else
    if(std::rename(__ss_cpath(a, "rename", "src"), __ss_cpath(b, "rename", "dst")) == -1) {
#endif
        __throw_oserror(a, b);
    }
    return NULL;
}

/* dir_fd variants (*at() calls), as CPython; not on windows */
void __ss_dir_fd_unavailable(const char *func) {
    throw new NotImplementedError(new str((std::string(func) + ": dir_fd unavailable on this platform").c_str()));
}

#ifdef WIN32
void *__rename_at(int, str *, int, str *, bool replace) { __ss_dir_fd_unavailable(replace ? "replace" : "rename"); }
void *__unlink_at(int, str *, bool, const char *func) { __ss_dir_fd_unavailable(func); }
void *__mkdir_at(int, str *, __ss_int) { __ss_dir_fd_unavailable("mkdir"); }
__ss_int __open_at(int, str *, __ss_int, __ss_int) { __ss_dir_fd_unavailable("open"); }
void *__symlink_at(str *, int, str *) { __ss_dir_fd_unavailable("symlink"); }
str *__readlink_at(int, str *) { __ss_dir_fd_unavailable("readlink"); }
#else
static inline int __at_fd(int dir_fd) { return dir_fd == __SS_DIR_FD_CWD ? AT_FDCWD : dir_fd; }

void *__rename_at(int src_dir_fd, str *a, int dst_dir_fd, str *b, bool replace) {
    const char *func = replace ? "replace" : "rename";
    if(::renameat(__at_fd(src_dir_fd), __ss_cpath(a, func, "src"), __at_fd(dst_dir_fd), __ss_cpath(b, func, "dst")) == -1)
        __throw_oserror(a, b);
    return NULL;
}

void *__unlink_at(int dir_fd, str *path, bool dir, const char *func) {
    if(::unlinkat(__at_fd(dir_fd), __ss_cpath(path, func), dir ? AT_REMOVEDIR : 0) == -1)
        __throw_oserror(path);
    return NULL;
}

void *__mkdir_at(int dir_fd, str *path, __ss_int mode) {
    if(::mkdirat(__at_fd(dir_fd), __ss_cpath(path, "mkdir"), (mode_t)__ss_cint(mode)) == -1)
        __throw_oserror(path);
    return NULL;
}

__ss_int __open_at(int dir_fd, str *path, __ss_int flags, __ss_int mode) {
    int fd = ::openat(__at_fd(dir_fd), __ss_cpath(path, "open"), __ss_cint(flags) | O_CLOEXEC, __ss_cint(mode));
    if(fd == -1)
        __throw_oserror(path);
    return fd;
}

void *__symlink_at(str *src, int dir_fd, str *dst) {
    if(::symlinkat(__ss_cpath(src, "symlink", "src"), __at_fd(dir_fd), __ss_cpath(dst, "symlink", "dst")) == -1)
        __throw_oserror(src, dst);
    return NULL;
}

str *__readlink_at(int dir_fd, str *path) {
    size_t size = 256;
    for(;;) {
        std::string buffer(size, '\0');
        ssize_t n = ::readlinkat(__at_fd(dir_fd), __ss_cpath(path, "readlink"), &buffer[0], size);
        if(n == -1)
            __throw_oserror(path);
        if((size_t)n < size) {
            buffer.resize((size_t)n);
            return __fsdecode_c(buffer.c_str(), strlen(buffer.c_str()));
        }
        size *= 2;
    }
}
#endif

void __ss_fd_with(const char *func, bool dir_fd) {
    if(dir_fd)
        throw new ValueError(new str((std::string(func) + ": can't specify both dir_fd and fd").c_str()));
    throw new ValueError(new str((std::string(func) + ": cannot use fd and follow_symlinks together").c_str()));
}

[[noreturn]] static void __ss_arg_unavailable(const char *func, const char *arg) {
    throw new NotImplementedError(new str((std::string(func) + ": " + arg + " unavailable on this platform").c_str()));
}

#ifdef WIN32
void *__chmod_at(int dir_fd, str *, __ss_int, bool) {
    if(dir_fd != __SS_DIR_FD_CWD)
        __ss_dir_fd_unavailable("chmod");
    __ss_arg_unavailable("chmod", "follow_symlinks");
}
__ss_bool __access_at(int dir_fd, str *, __ss_int, bool effective_ids, bool) {
    if(dir_fd != __SS_DIR_FD_CWD)
        __ss_dir_fd_unavailable("access");
    __ss_arg_unavailable("access", effective_ids ? "effective_ids" : "follow_symlinks");
}
void *__link_at(int src_dir_fd, str *, int dst_dir_fd, str *, bool) {
    if(src_dir_fd != __SS_DIR_FD_CWD || dst_dir_fd != __SS_DIR_FD_CWD)
        __ss_dir_fd_unavailable("link");
    __ss_arg_unavailable("link", "follow_symlinks");
}
#else
void *__chmod_at(int dir_fd, str *path, __ss_int mode, bool follow_symlinks) {
    if(::fchmodat(__at_fd(dir_fd), __ss_cpath(path, "chmod"), (mode_t)__ss_cint(mode), follow_symlinks ? 0 : AT_SYMLINK_NOFOLLOW) == -1) {
        /* as CPython: the C library may refuse not to follow a symlink (linux) */
        if(!follow_symlinks && (errno == ENOTSUP || errno == EOPNOTSUPP)) {
            if(dir_fd == __SS_DIR_FD_CWD)
                __ss_arg_unavailable("chmod", "follow_symlinks");
            throw new ValueError(new str("chmod: cannot use dir_fd and follow_symlinks together"));
        }
        __throw_oserror(path);
    }
    return NULL;
}

__ss_bool __access_at(int dir_fd, str *path, __ss_int mode, bool effective_ids, bool follow_symlinks) {
    int flags = (effective_ids ? AT_EACCESS : 0) | (follow_symlinks ? 0 : AT_SYMLINK_NOFOLLOW);
    return __mbool(::faccessat(__at_fd(dir_fd), __ss_cpath(path, "access"), __ss_cint(mode), flags) == 0);
}

void *__link_at(int src_dir_fd, str *src, int dst_dir_fd, str *dst, bool follow_symlinks) {
    if(::linkat(__at_fd(src_dir_fd), __ss_cpath(src, "link", "src"), __at_fd(dst_dir_fd), __ss_cpath(dst, "link", "dst"), follow_symlinks ? AT_SYMLINK_FOLLOW : 0) == -1)
        __throw_oserror(src, dst);
    return NULL;
}
#endif

/* mkfifoat()/mknodat(): not on windows, and only since macOS 13 */
#if defined(WIN32) || defined(__APPLE__)
void *__mkfifo_at(int, str *, __ss_int) { __ss_dir_fd_unavailable("mkfifo"); }
void *__mknod_at(int, str *, __ss_int, __ss_int) { __ss_dir_fd_unavailable("mknod"); }
#else
void *__mkfifo_at(int dir_fd, str *path, __ss_int mode) {
    if(::mkfifoat(__at_fd(dir_fd), __ss_cpath(path, "mkfifo"), (mode_t)__ss_cint(mode)) == -1)
        __throw_oserror();
    return NULL;
}
#endif

void *replace(str *a, str *b) {
    /* std::rename() already atomically replaces an existing destination
     * on POSIX, but on Windows it fails with EEXIST in that case instead.
     * std::filesystem::rename() is specified to have POSIX-like overwrite
     * semantics on every platform, so use that here instead to match what
     * os.replace() promises. */
    std::error_code ec;
    std::filesystem::rename(__fspath(a, "replace", "src"), __fspath(b, "replace", "dst"), ec);
    if (ec) {
        /* the error_code overload doesn't throw and isn't guaranteed to
         * leave errno set, so set it explicitly from ec before constructing
         * the exception, which reads the global errno */
        errno = ec.value();
        __throw_oserror(a, b);
    }
    return NULL;
}

__ss_int cpu_count() {
    /* CPython can return None here if the count can't be determined;
     * shedskin doesn't allow mixing None with a scalar int return type
     * (see docs/documentation.md), so we fall back to 1 instead */
    unsigned int n = std::thread::hardware_concurrency();
    if (n == 0)
        n = 1;
    return (__ss_int)n;
}

/* like cpython: the number of cpus the calling thread may run on (its
   affinity mask) where the platform can tell, else cpu_count() */
__ss_int process_cpu_count() {
#ifdef __linux__
    cpu_set_t set;
    if (sched_getaffinity(0, sizeof(set), &set) == 0) {
        int n = CPU_COUNT(&set);
        if (n > 0)
            return (__ss_int)n;
    }
#endif
    return cpu_count();
}

static void __remove(str *path, const char *func) {
#ifdef WIN32
    if(::_wremove(__to_wide(path, func).c_str()) == -1) {
#else
    if(::unlink(__ss_cpath(path, func)) == -1) { /* not std::remove: that also removes empty directories */
#endif
        __throw_oserror(path);
    }
}

void *remove(str *path) {
    __remove(path, "remove");
    return NULL;
}

void *unlink(str *path) {
    __remove(path, "unlink");
    return NULL;
}

void *rmdir(str *a) {
#ifdef WIN32
    if (::_wrmdir(__to_wide(a, "rmdir").c_str()) == -1)
#else
    if (::rmdir(__ss_cpath(a, "rmdir")) == -1)
#endif
        __throw_oserror(a);
    return NULL;
}

void *removedirs(str *name_) {
    tuple<str *> *__0, *__1, *__5;
    str *__2, *head, *tail;

    rmdir(name_);
    __0 = __path__::split(name_);
    head = __0->__getfirst__();
    tail = __0->__getsecond__();
    if ((!___bool(tail))) {
        __1 = __path__::split(head);
        head = __1->__getfirst__();
        tail = __1->__getsecond__();
    }

    while(___bool(__AND(head, tail, 2))) {
        try {
            rmdir(head);
        } catch (OSError *) {
            break;
        }
        __5 = __path__::split(head);
        head = __5->__getfirst__();
        tail = __5->__getsecond__();
    }
    return NULL;
}


void *mkdir(str *path, __ss_int mode) {
#ifdef WIN32
    __ss_cint(mode); /* not used, but checked as in cpython */
    if (::_wmkdir(__to_wide(path, "mkdir").c_str()) == -1)
#else
    if (::mkdir(__ss_cpath(path, "mkdir"), (mode_t)__ss_cint(mode)) == -1)
#endif
        __throw_oserror(path);
    return NULL;
}

void _exit(__ss_int code) {
    ::_exit(__ss_cint(code)); /* no atexit handlers or stdio flushing (matters after fork) */
}

void *makedirs(str *name_, __ss_int mode, __ss_bool exist_ok, __ss_int parent_mode) {
    /**
    parent_mode controls the mode used for intermediate directories.
    parent_mode==-1 (the "None" sentinel; shedskin has no Optional[int])
    means intermediate directories are created with the default mode
    0777, matching CPython's behaviour. Pass parent_mode=mode explicitly
    to restore the pre-3.7 CPython behaviour of applying mode recursively.
    */
    tuple<str *> *__0, *__1;
    str *head, *tail;
    __ss_int recurse_mode;

    __0 = __path__::split(name_);
    head = __0->__getfirst__();
    tail = __0->__getsecond__();
    if ((!___bool(tail))) {
        __1 = __path__::split(head);
        head = __1->__getfirst__();
        tail = __1->__getsecond__();
    }
    if ((___bool(head) && ___bool(tail) && (!__path__::exists(head)))) {
        recurse_mode = (parent_mode == -1) ? 0777 : parent_mode;
        try {
            makedirs(head, recurse_mode, exist_ok, parent_mode);
        } catch (OSError *e) {
            if (e->__ss_errno != EEXIST) {
                throw; /* keep the dynamic type (FileExistsError..) */
            }
        }
        if (__eq(tail, __path__::curdir)) {
            return NULL;
        }
    }
    try {
        mkdir(name_, mode);
    } catch (OSError *e) {
        if (!(exist_ok.value && e->__ss_errno == EEXIST && __path__::isdir(name_).value)) {
            throw;
        }
    }
    return NULL;
}

void *abort() {
    std::abort();
}

/* class stat_result */

class_ *cl_stat_result;

/* set float seconds, integer nanoseconds and integer seconds for one timestamp,
   computed the same way as CPython (float: sec + nsec * 1e-9) */
static void __set_stat_time(__ss_float &f, __ss_int &ns, __ss_int &s, long long sec, long nsec) {
    f = (__ss_float)((double)sec + (double)nsec * 1e-9);
    ns = (__ss_int)(sec * 1000000000LL + nsec);
    s = (__ss_int)sec;
}

#ifdef WIN32
/* the CRT stat() leaves st_ino zero, reports the drive number as st_dev and
   has second resolution only, so like CPython take these from the Win32 API */
static void __set_stat_filetime(__ss_float &f, __ss_int &ns, __ss_int &s, const FILETIME &ft) {
    ULARGE_INTEGER u;
    u.LowPart = ft.dwLowDateTime;
    u.HighPart = ft.dwHighDateTime;
    long long in = (long long)u.QuadPart; /* 100ns units since 1601-01-01 */
    __set_stat_time(f, ns, s, in / 10000000LL - 11644473600LL, (long)(in % 10000000LL) * 100);
}

static void __stat_win32_info(stat_result *st, HANDLE h) {
    BY_HANDLE_FILE_INFORMATION info;
    if (h == INVALID_HANDLE_VALUE || !GetFileInformationByHandle(h, &info))
        return; /* keep the CRT values */
    st->st_ino = (__ss_int)(((unsigned long long)info.nFileIndexHigh << 32) | info.nFileIndexLow);
    st->st_dev = (__ss_int)info.dwVolumeSerialNumber;
    st->st_nlink = (__ss_int)info.nNumberOfLinks;
    __set_stat_filetime(st->__ss_st_atime, st->st_atime_ns, st->__atime_s, info.ftLastAccessTime);
    __set_stat_filetime(st->__ss_st_mtime, st->st_mtime_ns, st->__mtime_s, info.ftLastWriteTime);
    __set_stat_filetime(st->__ss_st_ctime, st->st_ctime_ns, st->__ctime_s, info.ftCreationTime);
}
#endif

stat_result::stat_result(str *path, __ss_int t) {
    this->__class__ = cl_stat_result;

    int r = -1;
    if(t==1) {
#ifdef WIN32
        /* (struct stat is the 64-bit time, 32-bit size variant) */
        static_assert(sizeof(struct stat) == sizeof(struct _stat64i32));
        r = ::_wstat64i32(__to_wide(path, "stat").c_str(), (struct _stat64i32 *)&sbuf);
#else
        r = ::stat(__ss_cpath(path, "stat"), &sbuf);
#endif
    } else if (t==2) {
#ifndef WIN32
        r = ::lstat(__ss_cpath(path, "lstat"), &sbuf);
#endif
    }
#ifdef WIN32
    bool device = false;
    if (r == -1) {
        /* The CRT stat() fails on device names such as 'nul' or 'con'.
           Like CPython (since 3.8), fall back to opening the path and
           reporting it as a character device/pipe. */
        HANDLE h = CreateFileW(__to_wide(path).c_str(), 0,
                               FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                               NULL, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, NULL);
        if (h != INVALID_HANDLE_VALUE) {
            DWORD type = GetFileType(h);
            CloseHandle(h);
            if (type == FILE_TYPE_CHAR || type == FILE_TYPE_PIPE) {
                memset(&sbuf, 0, sizeof(sbuf));
                sbuf.st_mode = (type == FILE_TYPE_CHAR) ? _S_IFCHR : _S_IFIFO;
                r = 0;
                device = true;
            }
        }
    }
#endif
    if (r == -1) {
        __throw_oserror(path);
    }

    fill_er_up();

#ifdef WIN32
    if (!device) {
        HANDLE h = CreateFileW(__to_wide(path).c_str(), 0,
                               FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                               NULL, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, NULL);
        if (h != INVALID_HANDLE_VALUE) {
            __stat_win32_info(this, h);
            CloseHandle(h);
        }
    }
#endif
    __set_items();
}

stat_result::stat_result(__ss_int dir_fd, str *path, bool follow_symlinks) {
    this->__class__ = cl_stat_result;
#ifdef WIN32
    (void)dir_fd; (void)path; (void)follow_symlinks;
    throw new NotImplementedError(new str("stat: dir_fd unavailable on this platform"));
#else
    if(::fstatat(__ss_cint(dir_fd), __ss_cpath(path, "stat"), &sbuf, follow_symlinks ? 0 : AT_SYMLINK_NOFOLLOW) == -1)
        __throw_oserror(path);
    fill_er_up();
    __set_items();
#endif
}

stat_result::stat_result(__ss_int fd) {
    this->__class__ = cl_stat_result;

    int r;
    {
        __suppress_iph guard;
        r = ::fstat(__ss_cint(fd), &sbuf);
    }
    if(r == -1)
        __throw_oserror();

    fill_er_up();

#ifdef WIN32
    __stat_win32_info(this, (HANDLE)_get_osfhandle((int)fd));
#endif
    __set_items();
}

void stat_result::fill_er_up() {
    this->st_mode = (__ss_int)sbuf.st_mode;
    this->st_ino = (__ss_int)sbuf.st_ino;
    this->st_dev = (__ss_int)sbuf.st_dev;
    this->st_rdev = (__ss_int)sbuf.st_rdev;
    this->st_nlink = (__ss_int)sbuf.st_nlink;
#if defined(WIN32)
    long atime_nsec = 0, mtime_nsec = 0, ctime_nsec = 0; /* overridden by __stat_win32_info */
#elif defined(__APPLE__)
    long atime_nsec = sbuf.st_atimespec.tv_nsec, mtime_nsec = sbuf.st_mtimespec.tv_nsec, ctime_nsec = sbuf.st_ctimespec.tv_nsec;
#else
    long atime_nsec = sbuf.st_atim.tv_nsec, mtime_nsec = sbuf.st_mtim.tv_nsec, ctime_nsec = sbuf.st_ctim.tv_nsec;
#endif
    __set_stat_time(this->__ss_st_atime, this->st_atime_ns, this->__atime_s, (long long)sbuf.st_atime, atime_nsec);
    __set_stat_time(this->__ss_st_mtime, this->st_mtime_ns, this->__mtime_s, (long long)sbuf.st_mtime, mtime_nsec);
    __set_stat_time(this->__ss_st_ctime, this->st_ctime_ns, this->__ctime_s, (long long)sbuf.st_ctime, ctime_nsec);
    this->st_uid = (__ss_int)sbuf.st_uid;
    this->st_gid = (__ss_int)sbuf.st_gid;
    this->st_size = (__ss_int)sbuf.st_size;
#ifndef WIN32
    this->st_blksize = (__ss_int)sbuf.st_blksize;
    this->st_blocks = (__ss_int)sbuf.st_blocks;
#endif
}

/* the items, once all fields are known (on windows, after __stat_win32_info) */
void stat_result::__set_items() {
    this->units.assign({st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, __atime_s, __mtime_s, __ctime_s});
}

str *stat_result::__repr__() {
    return __mod6(new str("os.stat_result(st_mode=%d, st_ino=%d, st_dev=%d, st_nlink=%d, st_uid=%d, st_gid=%d, st_size=%d, st_atime=%d, st_mtime=%d, st_ctime=%d)"), 10,
        st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, __atime_s, __mtime_s, __ctime_s);
}

stat_result *stat(str *path) {
    return new stat_result(path, 1);
}
stat_result *stat(bytes *path) {
    return stat(fsdecode(path));
}
stat_result *stat(__ss_bool follow_symlinks, str *path) {
    if(follow_symlinks)
        return stat(path);
    return lstat(path);
}
stat_result *stat(__ss_bool follow_symlinks, bytes *path) {
    return stat(follow_symlinks, fsdecode(path));
}
stat_result *stat(__ss_bool follow_symlinks, void *, str *path) {
    return stat(follow_symlinks, path);
}
stat_result *stat(__ss_bool follow_symlinks, void *, bytes *path) {
    return stat(follow_symlinks, fsdecode(path));
}
stat_result *stat(__ss_bool follow_symlinks, __ss_int dir_fd, str *path) {
    return new stat_result(dir_fd, path, follow_symlinks);
}
stat_result *stat(__ss_bool follow_symlinks, __ss_int dir_fd, bytes *path) {
    return new stat_result(dir_fd, fsdecode(path), follow_symlinks);
}
stat_result *stat(__ss_bool follow_symlinks, void *, __ss_int fd) {
    /* (as cpython: an fd is not followed, so follow_symlinks=False is refused) */
    if(!follow_symlinks)
        throw new ValueError(new str("stat: cannot use fd and follow_symlinks together"));
    return fstat(fd);
}
stat_result *stat(__ss_bool, __ss_int, __ss_int) {
    throw new ValueError(new str("stat: can't specify dir_fd without matching path"));
}
stat_result *lstat(str *path) {
#ifndef WIN32
    return new stat_result(path, 2);
#else
    return new stat_result(path, 1);
#endif
}
stat_result *lstat(bytes *path) {
    return lstat(fsdecode(path));
}
stat_result *lstat(void *, str *path) {
    return lstat(path);
}
stat_result *lstat(void *, bytes *path) {
    return lstat(fsdecode(path));
}
stat_result *lstat(__ss_int dir_fd, str *path) {
    return new stat_result(dir_fd, path, false);
}
stat_result *lstat(__ss_int dir_fd, bytes *path) {
    return new stat_result(dir_fd, fsdecode(path), false);
}
stat_result *fstat(__ss_int fd) {
    return new stat_result(fd);
}

/* class DirEntry */

class_ *cl_DirEntry;

DirEntry::DirEntry(const std::filesystem::directory_entry &entry) {
    this->__class__ = cl_DirEntry;
    this->name = __fsstr(entry.path().filename());
    this->path = __fsstr(entry.path());

    /* these use the type cached by the directory iterator, if any */
    std::error_code ec;
    if(entry.is_symlink(ec))
        __type = std::filesystem::file_type::symlink;
    else if(entry.is_directory(ec))
        __type = std::filesystem::file_type::directory;
    else if(entry.is_regular_file(ec))
        __type = std::filesystem::file_type::regular;
    else
        __type = std::filesystem::file_type::unknown;
}

DirEntry::DirEntry(int dir_fd, str *name, std::filesystem::file_type type, __ss_int ino) {
    this->__class__ = cl_DirEntry;
    this->name = this->path = name;
    __type = type;
    __dir_fd = dir_fd;
    __ino = ino;
}

#ifndef WIN32
/* scandir(fd): the type of what a symlink points to (unknown if it cannot
   be stat'ed, as for a dangling link). with 'raise', only a missing target
   is unknown, as CPython's DirEntry.is_dir()/is_file() catch only
   FileNotFoundError (e.g. a symlink loop raises) */
static std::filesystem::file_type __entry_type_at(int dir_fd, str *name, bool follow_symlinks, bool raise=false, str *path=0) {
    struct stat sb;
    int r = dir_fd == -1 ? ::stat(__ss_cpath(path, "stat"), &sb)
                         : ::fstatat(dir_fd, __ss_cpath(name, "scandir"), &sb, follow_symlinks ? 0 : AT_SYMLINK_NOFOLLOW);
    if(r == -1) {
        if(raise && errno != ENOENT)
            __throw_oserror(dir_fd == -1 ? path : name);
        return std::filesystem::file_type::unknown;
    }
    if(S_ISDIR(sb.st_mode))
        return std::filesystem::file_type::directory;
    if(S_ISREG(sb.st_mode))
        return std::filesystem::file_type::regular;
    if(S_ISLNK(sb.st_mode))
        return std::filesystem::file_type::symlink;
    return std::filesystem::file_type::unknown;
}
#endif

__ss_bool DirEntry::is_dir(__ss_bool follow_symlinks) {
    if(__type == std::filesystem::file_type::symlink) {
#ifndef WIN32
        return __mbool(follow_symlinks && __entry_type_at(__dir_fd, name, true, true, this->path) == std::filesystem::file_type::directory);
#else
        std::error_code ec;
        return __mbool(follow_symlinks && std::filesystem::is_directory(__fspath(this->path), ec));
#endif
    }
    return __mbool(__type == std::filesystem::file_type::directory);
}

__ss_bool DirEntry::is_file(__ss_bool follow_symlinks) {
    if(__type == std::filesystem::file_type::symlink) {
#ifndef WIN32
        return __mbool(follow_symlinks && __entry_type_at(__dir_fd, name, true, true, this->path) == std::filesystem::file_type::regular);
#else
        std::error_code ec;
        return __mbool(follow_symlinks && std::filesystem::is_regular_file(__fspath(this->path), ec));
#endif
    }
    return __mbool(__type == std::filesystem::file_type::regular);
}

__ss_bool DirEntry::is_symlink() {
    return __mbool(__type == std::filesystem::file_type::symlink);
}

__ss_bool DirEntry::is_junction() {
    return __path__::isjunction(this->path); /* always False except on Windows */
}

__ss_int DirEntry::inode() {
    if(__dir_fd != -1)
        return __ino;
    return __os__::lstat(this->path)->st_ino;
}

stat_result *DirEntry::stat(__ss_bool follow_symlinks) {
    if(__dir_fd != -1)
        return new stat_result((__ss_int)__dir_fd, name, follow_symlinks);
    if(follow_symlinks)
        return __os__::stat(this->path);
    return __os__::lstat(this->path);
}

str *DirEntry::__repr__() {
    std::stringstream ss;
    ss << "<DirEntry " << repr(this->name)->c_str() << ">";
    return new str(ss.str().c_str());
}

/* class ScandirIterator */

class_ *cl_ScandirIterator;

DirEntry *ScandirIterator::__next__() {
    if(!entries || pos == len(entries))
        __throw_stop_iteration();
    return entries->units[pos++];
}

DirEntry *ScandirIterator::__get_next() { /* no exception at the end (see __iter) */
    if(!entries || pos == len(entries)) {
        this->__stop_iteration = true;
        return NULL;
    }
    return entries->units[pos++];
}

str *ScandirIterator::__repr__() {
    std::stringstream ss;
#ifdef WIN32
    ss << "<nt.ScandirIterator object at " << (void *)this << ">";
#else
    ss << "<posix.ScandirIterator object at " << (void *)this << ">";
#endif
    return new str(ss.str().c_str());
}

ScandirIterator *scandir(str *path) {
    if(!path)
        path = new str(".");

    list<DirEntry *> *r = new list<DirEntry *>();

    try {
        for (const auto & entry : std::filesystem::directory_iterator(__fspath(path, "scandir")))
            r->append(new DirEntry(entry));
    } catch (std::filesystem::filesystem_error const& e) {
        __throw_fs_error(e, path);
    }

    return new ScandirIterator(r);
}

ScandirIterator *scandir(void *) {
    return scandir(new str("."));
}

ScandirIterator *scandir(__ss_int fd) {
#ifdef WIN32
    (void)fd;
    throw new TypeError(new str("scandir: path should be string, bytes, os.PathLike or None, not int"));
#else
    /* as cpython: read a dup of the fd from the start; the entries stat()
       relative to fd, which must stay open */
    int fd_ = __ss_cint(fd);
    int fd2 = ::dup(fd_);
    if(fd2 == -1)
        __throw_oserror();
    DIR *dir = ::fdopendir(fd2);
    if(!dir) {
        int e = errno;
        ::close(fd2);
        errno = e;
        __throw_oserror();
    }
    ::rewinddir(dir);
    list<DirEntry *> *r = new list<DirEntry *>();
    errno = 0;
    while(struct dirent *ent = ::readdir(dir)) {
        if(strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0)
            continue;
        str *name = __fsstr(std::filesystem::path(ent->d_name));
        std::filesystem::file_type type;
        switch(ent->d_type) {
            case DT_DIR: type = std::filesystem::file_type::directory; break;
            case DT_REG: type = std::filesystem::file_type::regular; break;
            case DT_LNK: type = std::filesystem::file_type::symlink; break;
            case DT_UNKNOWN: type = __entry_type_at(fd_, name, false); break;
            default: type = std::filesystem::file_type::unknown;
        }
        r->append(new DirEntry(fd_, name, type, (__ss_int)ent->d_ino));
    }
    int e = errno;
    ::rewinddir(dir);
    ::closedir(dir);
    if(e) {
        errno = e;
        __throw_oserror();
    }
    return new ScandirIterator(r);
#endif
}

/* os.walk */

static str *__walk_join(str *top, str *name) {
    if(top->unit.empty())
        return name;
    __ss_char last = top->unit.back();
#ifdef WIN32
    /* (as ntpath.join: a bare drive 'C:' gets no separator, 'C:sub') */
    if(last == '/' || last == '\\' || (top->unit.size() == 2 && last == ':'))
#else
    if(last == '/') /* (a backslash is an ordinary character here) */
#endif
        return new str(top->unit + name->unit);
#ifdef WIN32
    return new str(top->unit + __gcs("\\") + name->unit);
#else
    return new str(top->unit + __gcs("/") + name->unit);
#endif
}

__walk_iter::__walk_iter(str *top_, __ss_bool topdown_, __ss_bool followlinks_, __walk_onerror onerror_) {
    top = top_;
    topdown = topdown_;
    followlinks = followlinks_;
    onerror = onerror_;
    last = NULL;
    pos = 0;
    collected = false;
    if(topdown)
        pending.push_back(top);
}

/* report a directory that cannot be scanned to the onerror callback (if any),
   with the same OSError subclass/errno/filename as e.g. os.scandir(path) */
void __walk_iter::__onerror(str *path, std::error_code ec) {
    if(!onerror)
        return;
    OSError *err = NULL;
    int saved = errno;
    errno = ec.default_error_condition().value();
    try {
        __throw_oserror(path);
    } catch (OSError *e) {
        err = e;
    }
    errno = saved;
    onerror(err);
}

/* scan a directory into a (dirpath, dirnames, filenames) tuple; returns NULL if
   it cannot be read (reported to onerror, then skipped) */
__walk_tuple *__walk_iter::__scan(str *top, __GC_VECTOR(str *) &subdirs) {
    list<str *> *dirs = new list<str *>();
    list<str *> *files = new list<str *>();

    std::error_code ec;
    std::filesystem::directory_iterator it(__fspath(top, "scandir"), ec);
    if(ec) {
        __onerror(top, ec);
        return NULL;
    }
    try {
        for (const auto & entry : it) {
            std::error_code ec2;
            str *name = __fsstr(entry.path().filename());
            if(entry.is_directory(ec2)) {
                dirs->append(name);
                if(followlinks || !entry.is_symlink(ec2))
                    subdirs.push_back(name);
            } else
                files->append(name);
        }
    } catch (std::filesystem::filesystem_error const &e) {
        __onerror(top, e.code());
        return NULL;
    }

    return new __walk_tuple(3, top, dirs, files);
}

/* bottom-up: precompute results in post-order (no pruning possible) */
void __walk_iter::__collect(str *top) {
    __GC_VECTOR(str *) subdirs;
    __walk_tuple *t = __scan(top, subdirs);
    if(!t)
        return;
    for(str *name : subdirs)
        __collect(__walk_join(top, name));
    results.push_back(t);
}

__walk_tuple *__walk_iter::__next__() {
    if(!topdown) {
        if(!collected) { /* like the CPython generator, nothing happens before the first next() */
            collected = true;
            __collect(top);
        }
        if(pos >= results.size())
            throw new StopIteration();
        return results[pos++];
    }

    /* descend into the (possibly pruned) dirnames of the last yielded tuple */
    if(last) {
        list<str *> *dirs = last->__getsecond__();
        for(size_t i = dirs->units.size(); i > 0; i--) {
            str *name = dirs->units[i-1];
            std::error_code ec;
            str *path = __walk_join(last->__getfirst__(), name);
            if(followlinks || !std::filesystem::is_symlink(__fspath(path), ec))
                pending.push_back(path);
        }
        last = NULL;
    }

    while(!pending.empty()) {
        str *top = pending.back();
        pending.pop_back();
        __GC_VECTOR(str *) subdirs; /* unused for topdown: recursion uses last->dirnames */
        __walk_tuple *t = __scan(top, subdirs);
        if(t) {
            last = t;
            return t;
        }
    }
    throw new StopIteration();
}

__walk_iter *walk(str *top, __ss_bool topdown, void *, __ss_bool followlinks) {
    return new __walk_iter(top, topdown, followlinks);
}

void *putenv(str* varname, str* value) {
    /* (::putenv() keeps the pointer it is passed, so use the copying variants) */
#ifdef WIN32
    /* as CPython: on windows a leading '=' is fine (hidden variables) */
    if(varname->unit.empty() || varname->unit.find('=', 1) != __GC_STR::npos)
        throw new ValueError(new str("illegal environment variable name"));
    if(::_putenv_s(__ss_cpath(varname), __ss_cpath(value)) != 0)
        __throw_oserror();
#else
    /* (an empty name is left to setenv(): EINVAL, as CPython) */
    if(varname->unit.find('=') != __GC_STR::npos)
        throw new ValueError(new str("illegal environment variable name"));
    if(::setenv(__ss_cpath(varname), __ss_cpath(value), 1) == -1)
        __throw_oserror();
#endif
    return NULL;
}

void *unsetenv(str* var) {
#ifdef WIN32
    /* MSVC has no unsetenv(); passing "NAME=" to _putenv removes NAME
       from the environment. */
    if(var->unit.empty() || var->unit.find('=', 1) != __GC_STR::npos) /* (as CPython) */
        throw new ValueError(new str("illegal environment variable name"));
    std::stringstream ss;
    ss << __ss_cpath(var) << '=';
    if(_putenv(const_cast<char*>(ss.str().c_str())) != 0)
        __throw_oserror();
#else
    if (::unsetenv(__ss_cpath(var)) == -1) /* e.g. '' or 'a=b': EINVAL, as CPython */
        __throw_oserror();
#endif
    return NULL;
}

__ss_int umask(__ss_int newmask)  {
    return (__ss_int)::umask((unsigned)__ss_cint(newmask));
}

void *chmod(str* path, __ss_int val) {
#ifdef WIN32
    /* windows only honours the write permission bit (read-only attribute) */
    if(::_wchmod(__to_wide(path, "chmod").c_str(), __ss_cint(val)) == -1)
#else
    if(::chmod(__ss_cpath(path, "chmod"), (mode_t)__ss_cint(val)) == -1)
#endif
        __throw_oserror(path);
    return NULL;
}

void *fchmod(__ss_int fd_, __ss_int mode_) {
    int fd = __ss_cint(fd_), mode = __ss_cint(mode_);
#ifdef WIN32
    /* like cpython (3.13+): only the write permission bit, as the read-only
       attribute of the open file */
    HANDLE h;
    {
        __suppress_iph guard;
        h = (HANDLE)::_get_osfhandle(fd);
    }
    if (h == INVALID_HANDLE_VALUE) {
        errno = EBADF;
        __throw_oserror();
    }
    FILE_BASIC_INFO info;
    if (!GetFileInformationByHandleEx(h, FileBasicInfo, &info, sizeof(info)))
        throw new OSError(new str("os.fchmod"));
    if (mode & _S_IWRITE)
        info.FileAttributes &= ~(DWORD)FILE_ATTRIBUTE_READONLY;
    else
        info.FileAttributes |= FILE_ATTRIBUTE_READONLY;
    if (!SetFileInformationByHandle(h, FileBasicInfo, &info, sizeof(info)))
        throw new OSError(new str("os.fchmod"));
#else
    if (::fchmod(fd, (mode_t)mode) == -1)
        __throw_oserror();
#endif
    return NULL;
}

void *renames(str* old, str* _new) {
    /* as CPython: create the new leaf's parents, then prune the old ones as
       far as they are empty (errors there are ignored) */
    tuple<str *> *t = __path__::split(_new);
    str *head = t->__getfirst__(), *tail = t->__getsecond__();
    if(___bool(head) && ___bool(tail) && !__path__::exists(head))
        makedirs(head);
    rename(old, _new);
    t = __path__::split(old);
    head = t->__getfirst__();
    tail = t->__getsecond__();
    if(___bool(head) && ___bool(tail)) {
        try {
            removedirs(head);
        } catch (OSError *) {
        }
    }
    return NULL;
}

/* popen is declared unconditionally in __init__.hpp; msvc spells it _popen */
static FILE *__ss_popen(const char *cmd, const char *mode) {
#ifdef _MSC_VER
    return ::_popen(cmd, mode);
#else
    return ::popen(cmd, mode);
#endif
}

static int __ss_pclose(FILE *f) {
#ifdef _MSC_VER
    return ::_pclose(f);
#else
    return ::pclose(f);
#endif
}

popen_pipe::popen_pipe(str *cmd, str *flags) {
    if(flags == 0)
        flags = new str("r");
    f = __ss_popen(__ss_cpath(cmd), flags->c_str());
    if(f == 0)
        __throw_oserror(cmd);
    name = cmd;
    mode = flags;
    __errors = __SS_ERR_STRICT;
    errors = new str("strict");
}

/* as CPython: the exit code shifted left by 8, minus the signal number
   shifted left by 8 if the process was killed, or the exit code on windows */
void *__popen_file::close() {
    if(f and not closed) {
        int st = __ss_pclose(f);
        closed = True;
        __close_buffer();
        if(st == -1)
            __throw_oserror();
#ifndef WIN32
        if(WIFSIGNALED(st))
            st = -(WTERMSIG(st) << 8);
        else if(WIFEXITED(st))
            st = WEXITSTATUS(st) << 8;
#endif
        status = st;
    }
    return NULL;
}

__ss_int popen_pipe::close(__ss_int) {
    __popen_file::close();
    return status;
}

popen_pipe* popen(str* cmd) {
    return popen(cmd, new str("r"), -1);
}

popen_pipe* popen(str* cmd, str* mode) {
    return popen(cmd, mode, -1);
}

popen_pipe* popen(str* cmd, str* mode, __ss_int bufsize) {
    if(!mode)
        mode = new str("r");
    /* as cpython: text pipes only, either way */
    if(!(mode->unit == U"r" || mode->unit == U"w"))
        throw new ValueError(__add_strs(2, new str("invalid mode "), repr(mode)));
    if(bufsize == 0)
        throw new ValueError(new str("popen() does not support unbuffered streams"));
    FILE* fp = __ss_popen(__ss_cpath(cmd), mode->c_str());

    if(!fp) __throw_oserror(cmd);
    return new popen_pipe(fp);
}

/* like cpython (PEP 446): new file descriptors are non-inheritable */
__ss_int dup(__ss_int f1) {
    __ss_int f2;
    {
        __suppress_iph guard;
#ifdef WIN32
        f2 = ::dup(__ss_cint(f1));
#else
        f2 = ::fcntl(__ss_cint(f1), F_DUPFD_CLOEXEC, 0);
#endif
    }
    if (f2 == -1)
        __throw_oserror();
#ifdef WIN32
    set_inheritable(f2, False);
#endif
    return f2;
}

__ss_int dup2(__ss_int f1, __ss_int f2, __ss_bool inheritable) {
    /* (2**32+1 must not become 1, replacing stdout) */
    int fd1 = __ss_cint(f1), fd2 = __ss_cint(f2);
    int r;
    {
        __suppress_iph guard;
        r = ::dup2(fd1, fd2);
    }
    if (r == -1)
        __throw_oserror();
    /* like cpython: the new descriptor is inheritable unless asked otherwise */
#ifdef WIN32
    set_inheritable(f2, inheritable);
#else
    if (!inheritable)
        set_inheritable(f2, False);
#endif
    return f2;
}

#if !defined(__APPLE__) && !defined(__FreeBSD__) && !defined(WIN32)
void *fdatasync(__ss_int f1) {
    if (::fdatasync(__ss_fildes(f1)) == -1)
        __throw_oserror();
    return NULL;
}
#endif

__ss_int open(str *name_, __ss_int flags, __ss_int mode) {
#ifdef WIN32
    __ss_int fp = ::_wopen(__to_wide(name_, "open").c_str(), __ss_cint(flags) | _O_NOINHERIT, __ss_cint(mode));
#else
    __ss_int fp = ::open(__ss_cpath(name_, "open"), __ss_cint(flags) | O_CLOEXEC, __ss_cint(mode));
#endif
    if(fp == -1)
        __throw_oserror(name_);
    return fp;
}


/* (as CPython, where os.fdopen() is io.open()) */
file* fdopen(__ss_int fd, str* mode, __ss_int buffering, str *encoding, str *errors, str *newline, __ss_int closefd) {
    return __shedskin__::open(fd, mode, buffering, encoding, errors, newline, closefd);
}

file_binary* fdopen_binary(__ss_int fd, str* mode, __ss_int buffering, str *encoding, str *errors, str *newline, __ss_int closefd) {
    return __shedskin__::open_binary(fd, mode, buffering, encoding, errors, newline, closefd);
}

bytes *read(__ss_int fd, __ss_int n) {
    /* like CPython: a single read(2), so we return whatever is available
       (e.g. on a pipe) instead of blocking until n bytes have arrived */
    int fd_ = __ss_cint(fd);
    if(n < 0) {
        errno = EINVAL;
        __throw_oserror();
    }
    if(n > INT_MAX)
        n = INT_MAX;
    bytes *s = new bytes();
    s->unit.resize((size_t)n);
    decltype(::read(0, 0, 0)) nr;
    {
        __suppress_iph guard;
        nr = ::read(fd_, &s->unit[0], (unsigned int)n);
    }
    if(nr < 0)
        __throw_oserror();
    s->unit.resize((size_t)nr);
    if((size_t)nr * 2 < (size_t)n) /* (don't keep n bytes for a short read, e.g. read(fd, 65536) on a pipe) */
        s->unit.shrink_to_fit();
    return s;
}

__ss_int write(__ss_int fd, bytes *s) {
    size_t r, n = s->unit.size();
#ifdef WIN32
    n = std::min(n, (size_t)INT_MAX); /* (as CPython: _write takes an unsigned int, and returns an int) */
#endif
    {
        __suppress_iph guard;
        r = (size_t)::write(__ss_cint(fd), s->c_str(), n);
    }
    if(r == std::string::npos)
        __throw_oserror();
    return (__ss_int)r;
}


/* like cpython: a single read(2) into a writable buffer (a bytearray) */
__ss_int readinto(__ss_int fd, bytes *buffer) {
    int fd_ = __ss_cint(fd);
    if(buffer->frozen)
        throw new TypeError(new str("readinto() argument 2 must be read-write bytes-like object, not bytes"));
    size_t n = buffer->unit.size();
    if(n == 0)
        return 0;
    if(n > INT_MAX)
        n = INT_MAX;
    decltype(::read(0, 0, 0)) nr;
    {
        __suppress_iph guard;
        nr = ::read(fd_, &buffer->unit[0], (unsigned int)n);
    }
    if(nr < 0)
        __throw_oserror();
    return (__ss_int)nr;
}

void *close(__ss_int fd) {
   int r;
   {
       __suppress_iph guard;
       r = ::close(__ss_cint(fd));
   }
   if(r < 0)
       __throw_oserror();
   return NULL;
}

/* utime */

/* split float seconds into seconds and nanoseconds like CPython does for
   os.utime() (_PyTime_DoubleToDenominator with ROUND_FLOOR) */
static void __utime_split(double t, long long &sec, long &nsec) {
    /* as CPython (and time.cpp): the casts below would be undefined */
    if (std::isnan(t))
        throw new ValueError(new str("Invalid value NaN (not a number)"));
    const double lim = std::ldexp(1.0, (int)(sizeof(time_t) * 8 - 1));
    if (!(std::floor(t) >= -lim && std::floor(t) < lim))
        throw new OverflowError(new str("timestamp out of range for platform time_t"));
    double intpart;
    double floatpart = modf(t, &intpart);
    floatpart = floor(floatpart * 1e9);
    if (floatpart >= 1e9) {
        floatpart -= 1e9;
        intpart += 1.0;
    } else if (floatpart < 0) {
        floatpart += 1e9;
        intpart -= 1.0;
    }
    sec = (long long)intpart;
    nsec = (long)floatpart;
}

/* set atime/mtime of path, as whole seconds plus nanoseconds */
#ifdef WIN32
/* win32 implementation based on cpython */

static __int64 secs_between_epochs = 11644473600; /* Seconds between 1.1.1601 and 1.1.1970 */

static void
time_t_to_FILE_TIME(long long time_in, long nsec_in, FILETIME *out_ptr)
{
    ULARGE_INTEGER out;
    out.QuadPart = (ULONGLONG)((time_in + secs_between_epochs) * 10000000 + nsec_in / 100);
    out_ptr->dwLowDateTime = out.LowPart;
    out_ptr->dwHighDateTime = out.HighPart;
}

static void __utime_win32(str *path, FILETIME *atime, FILETIME *mtime) {
    HANDLE hFile;
    hFile = CreateFileW(__to_wide(path, "utime").c_str(), FILE_WRITE_ATTRIBUTES, 0, NULL, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, NULL);
    if (hFile == INVALID_HANDLE_VALUE)
       __throw_winerror(GetLastError(), path);
    if (!SetFileTime(hFile, NULL, atime, mtime)) {
       DWORD err = GetLastError();
       CloseHandle(hFile);
       __throw_winerror(err, path);
    }
    CloseHandle(hFile);
}

/* (as cpython: neither is available on windows, and no fd for path) */
[[noreturn]] static void __utime_no_fd() {
    throw new TypeError(new str("utime: path should be string, bytes, os.PathLike or None, not int"));
}

static void __utime_check_args(int dir_fd, bool follow_symlinks) {
    if(dir_fd != __SS_DIR_FD_CWD)
        throw new NotImplementedError(new str("utime: dir_fd unavailable on this platform"));
    if(!follow_symlinks)
        throw new NotImplementedError(new str("utime: follow_symlinks unavailable on this platform"));
}

void *__utime_now(str *path, int dir_fd, bool follow_symlinks) {
    if(!path)
        __utime_no_fd();
    __utime_check_args(dir_fd, follow_symlinks);
    FILETIME now;
    GetSystemTimeAsFileTime(&now);
    __utime_win32(path, &now, &now);
    return NULL;
}

static void __utime_set(str *path, long long asec, long ansec, long long msec, long mnsec, int dir_fd, bool follow_symlinks) {
    if(!path)
        __utime_no_fd();
    __utime_check_args(dir_fd, follow_symlinks);
    FILETIME atime, mtime;
    time_t_to_FILE_TIME(asec, ansec, &atime);
    time_t_to_FILE_TIME(msec, mnsec, &mtime);
    __utime_win32(path, &atime, &mtime);
}

#else
static void __utime_at(str *path, struct timespec *ts, int dir_fd, bool follow_symlinks) {
    if(!path) { /* path was an fd (see __utime_p) */
        if(::futimens(dir_fd, ts) == -1)
            __throw_oserror();
        return;
    }
    if(dir_fd == __SS_DIR_FD_CWD)
        dir_fd = AT_FDCWD;
    if(::utimensat(dir_fd, __ss_cpath(path, "utime"), ts, follow_symlinks ? 0 : AT_SYMLINK_NOFOLLOW) == -1)
        __throw_oserror(path);
}

static void __utime_set(str *path, long long asec, long ansec, long long msec, long mnsec, int dir_fd, bool follow_symlinks) {
    struct timespec ts[2];
    ts[0].tv_sec = (time_t)asec;
    ts[0].tv_nsec = ansec;
    ts[1].tv_sec = (time_t)msec;
    ts[1].tv_nsec = mnsec;
    __utime_at(path, ts, dir_fd, follow_symlinks);
}

void *__utime_now(str *path, int dir_fd, bool follow_symlinks) {
    __utime_at(path, NULL, dir_fd, follow_symlinks);
    return NULL;
}
#endif

void *__utime_float(str *path, __ss_float atime, __ss_float mtime, int dir_fd, bool follow_symlinks) {
    long long asec, msec;
    long ansec, mnsec;
    __utime_split((double)atime, asec, ansec);
    __utime_split((double)mtime, msec, mnsec);
    __utime_set(path, asec, ansec, msec, mnsec, dir_fd, follow_symlinks);
    return NULL;
}

/* split nanoseconds into seconds and nanoseconds (floor division) */
static void __utime_split_ns(__ss_int t, long long &sec, long &nsec) {
    long long v = (long long)t;
    sec = v / 1000000000LL;
    long long r = v % 1000000000LL;
    if (r < 0) {
        r += 1000000000LL;
        sec -= 1;
    }
    nsec = (long)r;
}

void *__utime_ns(str *path, __ss_int atime_ns, __ss_int mtime_ns, int dir_fd, bool follow_symlinks) {
    long long asec, msec;
    long ansec, mnsec;
    __utime_split_ns(atime_ns, asec, ansec);
    __utime_split_ns(mtime_ns, msec, mnsec);
    __utime_set(path, asec, ansec, msec, mnsec, dir_fd, follow_symlinks);
    return NULL;
}

void __utime_error(const char *msg) {
    if (strstr(msg, "not both"))
        throw new ValueError(new str(msg));
    throw new TypeError(new str(msg));
}

bytes *urandom(__ss_int n) {
    if(n < 0)
        throw new ValueError(new str("negative argument not allowed"));
#ifdef WIN32
    /* like cpython: BCryptGenRandom with the system-preferred rng; looked up
       at run-time, so no extra link library is needed */
    typedef LONG (WINAPI *genrandom_t)(void *, PUCHAR, ULONG, ULONG);
    static genrandom_t genrandom = NULL;
    if(!genrandom) {
        HMODULE lib = LoadLibraryA("bcrypt.dll");
        if(lib)
            genrandom = (genrandom_t)(void *)GetProcAddress(lib, "BCryptGenRandom");
        if(!genrandom)
            __throw_winerror(GetLastError());
    }
    bytes *s = new bytes();
    s->unit.resize((size_t)n);
    size_t done = 0;
    while(done < (size_t)n) {
        ULONG chunk = (ULONG)std::min((size_t)n - done, (size_t)0x40000000);
        if(genrandom(NULL, (PUCHAR)&s->unit[done], chunk, 0x00000002 /* BCRYPT_USE_SYSTEM_PREFERRED_RNG */) < 0)
            throw new OSError(new str("os.urandom"));
        done += chunk;
    }
    return s;
#else
#ifdef __SS_HAVE_GETRANDOM
    {
        bytes *s = new bytes();
        s->unit.resize((size_t)n);
        size_t done = 0;
        while(done < (size_t)n) {
            ssize_t r = ::getrandom(&s->unit[done], (size_t)n - done, 0);
            if(r < 0) {
                if(errno == EINTR)
                    continue;
                if(errno == ENOSYS) /* (an old kernel: /dev/urandom below) */
                    break;
                __throw_oserror();
            }
            done += (size_t)r;
        }
        if(done == (size_t)n)
            return s;
    }
#endif
    __ss_int fd = open(new str("/dev/urandom"), __ss_O_RDONLY);
    bytes *s = new bytes();
    s->unit.resize((size_t)n);
    size_t done = 0;
    while(done < (size_t)n) { /* a single read may return less (32MB max on linux) */
        auto r = ::read((int)fd, &s->unit[done], (size_t)n - done);
        if(r <= 0) {
            if(r < 0 and errno == EINTR)
                continue;
            int err = (r < 0) ? errno : EIO;
            ::close((int)fd); /* don't leak the fd */
            errno = err;
            __throw_oserror(new str("/dev/urandom"));
        }
        done += (size_t)r;
    }
    ::close((int)fd);
    return s;
#endif
}

/* os.getrandom(): as CPython, one getrandom(2) call with the flags where
 * the system has it (linux); elsewhere urandom(), ignoring the flags (which,
 * like in CPython, must fit a C int) */
bytes *getrandom(__ss_int size, __ss_int flags) {
    __ss_cint(flags);
    if (size < 0) { /* (as CPython: from the system call, unlike urandom) */
        errno = EINVAL;
        __throw_oserror();
    }
#ifdef __SS_HAVE_GETRANDOM
    /* as CPython: one call, with the flags (so EINVAL for bad ones) */
    bytes *s = new bytes();
    s->unit.resize((size_t)size);
    ssize_t r;
    do
        r = ::getrandom(size ? &s->unit[0] : 0, (size_t)size, (unsigned int)flags);
    while(r < 0 && errno == EINTR);
    if(r < 0)
        __throw_oserror();
    s->unit.resize((size_t)r);
    return s;
#else
    return urandom(size);
#endif
}

#ifdef WIN32
__ss_bool isatty(__ss_int fd) {
    __suppress_iph guard;
    return __mbool(::_isatty(__ss_cint(fd)));
}
#endif

/* UNIX-only functionality */

#ifndef WIN32
/* the macOS W*() macros take the address of their argument */

__ss_bool __ss_WCOREDUMP(__ss_int status) {
    int st = __ss_cint(status);
    return __mbool(WCOREDUMP(st));
}

__ss_int __ss_WEXITSTATUS(__ss_int status) {
    int st = __ss_cint(status);
    return WEXITSTATUS(st);
}

__ss_bool __ss_WIFCONTINUED(__ss_int status) {
    int st = __ss_cint(status);
    return __mbool(WIFCONTINUED(st));
}

__ss_bool __ss_WIFEXITED(__ss_int status) {
    int st = __ss_cint(status);
    return __mbool(WIFEXITED(st));
}

__ss_bool __ss_WIFSIGNALED(__ss_int status) {
    int st = __ss_cint(status);
    return __mbool(WIFSIGNALED(st));
}

__ss_bool __ss_WIFSTOPPED(__ss_int status) {
    int st = __ss_cint(status);
    return __mbool(WIFSTOPPED(st));
}

__ss_int __ss_WSTOPSIG(__ss_int status) {
    int st = __ss_cint(status);
    return WSTOPSIG(st);
}

__ss_int __ss_WTERMSIG(__ss_int status) {
    int st = __ss_cint(status);
    return WTERMSIG(st);
}

void *fchdir(__ss_int f1) {
    if (::fchdir(__ss_fildes(f1)) == -1)
        __throw_oserror();
    return NULL;
}

str *readlink(str *path) {
    size_t size = 255;
    str *r;

    while (1)
      {
        std::string buffer(size, '\0');
        size_t nchars = (size_t)::readlink(__ss_cpath(path, "readlink"), &buffer[0], size);
        if (nchars == std::string::npos) {
            __throw_oserror(path);
        }
        if (nchars < size) {
            buffer.resize(nchars);
            r = __fsdecode_c(buffer.c_str(), strlen(buffer.c_str()));
            return r;
        }
        size *= 2;
      }
}

/* a uid_t/gid_t argument as cpython converts it: -1 means 'unchanged' (as
   does its unsigned equivalent), anything else must fit */
template<class T> static T __ss_id(__ss_int v, const char *what) {
    if(v == -1)
        return (T)-1;
    if constexpr (sizeof(__ss_int) > sizeof(long)) {
        if(v > LONG_MAX) {
            if(v > (__ss_int)ULONG_MAX || (T)v == (T)-1 || (__ss_int)(T)v != v)
                throw new OverflowError(__add_strs(2, new str(what), new str(" is greater than maximum")));
            return (T)v;
        }
    }
    if(v < 0 || (__ss_int)(T)v != v)
        throw new OverflowError(__add_strs(2, new str(what), new str(" is less than minimum")));
    return (T)v;
}
static uid_t __ss_uid(__ss_int v) { return __ss_id<uid_t>(v, "uid"); }
static gid_t __ss_gid(__ss_int v) { return __ss_id<gid_t>(v, "gid"); }

__ss_int getuid() { return (__ss_int)::getuid(); }
void *setuid(__ss_int uid) {
    if(::setuid(__ss_uid(uid)) == -1)
        __throw_oserror();
    return NULL;
}

__ss_int getgid() { return (__ss_int)::getgid(); }
void *setgid(__ss_int gid) {
    if(::setgid(__ss_gid(gid)) == -1)
        __throw_oserror();
    return NULL;
}

__ss_int geteuid() { return (__ss_int)::geteuid(); }
void *seteuid(__ss_int euid) {
    if(::seteuid(__ss_uid(euid)) == -1)
        __throw_oserror();
    return NULL;
}

__ss_int getegid() { return (__ss_int)::getegid(); }
void *setegid(__ss_int egid) {
    if(::setegid(__ss_gid(egid)) == -1)
        __throw_oserror();
    return NULL;
}

void *setreuid(__ss_int ruid, __ss_int euid) {
    if(::setreuid(__ss_uid(ruid), __ss_uid(euid)) == -1)
        __throw_oserror();
    return NULL;
}

void *setregid(__ss_int rgid, __ss_int egid) {
    if(::setregid(__ss_gid(rgid), __ss_gid(egid)) == -1)
        __throw_oserror();
    return NULL;
}

__ss_int tcgetpgrp(__ss_int fd) {
    __ss_int nr;
    nr = ::tcgetpgrp(__ss_cint(fd));
    if(nr == -1)
        __throw_oserror();
    return nr;
}

void *tcsetpgrp(__ss_int fd, __ss_int pg) {
    int fd_ = __ss_cint_i(fd);
    pid_t pg_ = __ss_cint_i(pg);
    if(::tcsetpgrp(fd_, pg_) == -1)
        __throw_oserror();
    return NULL;
}

__ss_int fork() {
    __ss_int ret;
    if ((ret = ::fork()) == -1)
        __throw_oserror();
    return ret;
}

#if !defined(__sun)
tuple<__ss_int> *forkpty() {
    __ss_int ret;
    int amaster;
    if ((ret = ::forkpty(&amaster, NULL, NULL, NULL)) == -1)
        __throw_oserror();
    return new tuple<__ss_int>(2, ret, (__ss_int)amaster);
}
tuple<__ss_int> *openpty() {
    int amaster, aslave;
    if (::openpty(&amaster, &aslave, NULL, NULL, NULL) == -1)
        __throw_oserror();
    set_inheritable(amaster, False);
    set_inheritable(aslave, False);
    return new tuple<__ss_int>(2, (__ss_int)amaster, (__ss_int)aslave);
}
#endif

tuple<__ss_int> *wait() {
    int pid, status;
    if((pid = ::wait(&status)) == -1)
        __throw_oserror();
    return new tuple<__ss_int>(2, (__ss_int)pid, (__ss_int)status);
}

tuple<__ss_int> *waitpid(__ss_int pid, __ss_int options) {
    int status = 0; /* (WNOHANG: unset when no child is ready) */
    pid_t pid_ = __ss_cint_i(pid);
    int options_ = __ss_cint_i(options);
    if((pid = ::waitpid(pid_, &status, options_)) == -1)
        __throw_oserror();
    return new tuple<__ss_int>(2, pid, (__ss_int)status);
}

__ss_int nice(__ss_int n) {
    int n_ = __ss_cint(n);
    errno = 0; /* (as CPython: -1 is also a valid niceness) */
    __ss_int m = ::nice(n_);
    if(m == -1 && errno != 0)
        __throw_oserror();
    return m;
}

void *kill(__ss_int pid, __ss_int sig) {
    /* (like cpython, sig is truncated) */
    if(::kill((pid_t)__ss_cint_i(pid), (int)sig) == -1)
        __throw_oserror();
    return NULL;
}
void *killpg(__ss_int pgid, __ss_int sig) {
    pid_t pgid_ = __ss_cint_i(pgid);
    int sig_ = __ss_cint_i(sig);
    if(::killpg(pgid_, sig_) == -1)
        __throw_oserror();
    return NULL;
}

str *getlogin() {
    char *name_ = ::getlogin();
    if(!name_)
        __throw_oserror();
    return new str(name_);
}

void *chown(str *path, __ss_int uid, __ss_int gid) {
    if (::chown(__ss_cpath(path, "chown"), __ss_uid(uid), __ss_gid(gid)) == -1)
        __throw_oserror(path);
    return NULL;
}

void *__chown_at(int dir_fd, str *path, __ss_int uid, __ss_int gid, bool follow_symlinks) {
    if (::fchownat(__at_fd(dir_fd), __ss_cpath(path, "chown"), __ss_uid(uid), __ss_gid(gid), follow_symlinks ? 0 : AT_SYMLINK_NOFOLLOW) == -1)
        __throw_oserror(path);
    return NULL;
}

void *__fchown(__ss_int fd, __ss_int uid, __ss_int gid) {
    if (::fchown(__ss_cint(fd), __ss_uid(uid), __ss_gid(gid)) == -1)
        __throw_oserror();
    return NULL;
}

void *lchown(str *path, __ss_int uid, __ss_int gid) {
    if (::lchown(__ss_cpath(path, "lchown"), __ss_uid(uid), __ss_gid(gid)) == -1)
        __throw_oserror(path);
    return NULL;
}

void *chroot(str *path) {
    if (::chroot(__ss_cpath(path, "chroot")) == -1)
        __throw_oserror(path);
    return NULL;
}

str *ctermid() {
    char term[L_ctermid];
    char *ptr = ::ctermid(term);
    return new str(ptr);
}

__ss_bool isatty(__ss_int fd) {
    return __mbool(::isatty(__ss_cint(fd)));
}

str *ttyname(__ss_int fd) {
    char *name_ = ::ttyname(__ss_cint(fd));
    if(!name_)
        __throw_oserror();
    return new str(name_);
}

class_ *cl_uname_result;

uname_result::uname_result(str *sysname, str *nodename, str *release, str *version, str *machine) : tuple2<str *, str *>(5, sysname, nodename, release, version, machine) {
    this->__class__ = cl_uname_result;
    this->sysname = sysname;
    this->nodename = nodename;
    this->release = release;
    this->version = version;
    this->machine = machine;
}

uname_result::uname_result(tuple<str *> *t) : tuple2<str *, str *>(t) {
    this->__class__ = cl_uname_result;
    if (len(t) != 5)
        throw new TypeError(__add_strs(3, new str(__SS_POSIX_MOD ".uname_result() takes a 5-sequence ("), __str(len(t)), new str("-sequence given)")));
    sysname = t->__getitem__(0);
    nodename = t->__getitem__(1);
    release = t->__getitem__(2);
    version = t->__getitem__(3);
    machine = t->__getitem__(4);
}

str *uname_result::__repr__() {
    return __add_strs(12, name, new str(".uname_result(sysname="), repr(sysname), new str(", nodename="), repr(nodename), new str(", release="), repr(release), new str(", version="), repr(version), new str(", machine="), repr(machine), new str(")"));
}

uname_result *uname() {
    struct utsname name_;
    if (::uname(&name_) == -1)
        __throw_oserror();
    return new uname_result(new str(name_.sysname), new str(name_.nodename), new str(name_.release), new str(name_.version), new str(name_.machine));
}

list<__ss_int> *getgroups() {
    gid_t l[MAXENTRIES];
    __ss_int nr = ::getgroups(MAXENTRIES, l);
    if(nr == -1)
        __throw_oserror();
    list<__ss_int> *r = new list<__ss_int>();
    for(__ss_int i=0;i<nr;i++)
        r->append((__ss_int)l[i]);
    return r;
}
void *setgroups(pyseq<__ss_int> *groups) {
    if(len(groups) > MAXENTRIES)
        throw new ValueError(new str("too many groups"));
    gid_t l[MAXENTRIES];
    for(__ss_int i=0; i<len(groups); i++)
        l[i] = __ss_gid(groups->__getitem__(i));
    if(::setgroups((size_t)len(groups), l) == -1)
        __throw_oserror();
    return NULL;
}

__ss_int getsid(__ss_int pid) {
    __ss_int nr = ::getsid((pid_t)__ss_cint_i(pid));
    if(nr == -1)
        __throw_oserror();
    return nr;
}
void *setsid() {
    if(::setsid() == -1)
        __throw_oserror();
    return NULL;
}

__ss_int getpgid(__ss_int pid) {
    __ss_int nr = ::getpgid((pid_t)__ss_cint_i(pid));
    if(nr == -1)
        __throw_oserror();
    return nr;
}
void *setpgid(__ss_int pid, __ss_int pgrp) {
    pid_t pid_ = __ss_cint_i(pid), pgrp_ = __ss_cint_i(pgrp);
    if(::setpgid(pid_, pgrp_) == -1)
        __throw_oserror();
    return NULL;
}

__ss_int getpgrp() {
    return getpgid(0);
}
void *setpgrp() {
    if(::setpgid(0, 0) == -1)
        __throw_oserror();
    return NULL;
}

void *link(str *src, str *dst) {
    if(::link(__ss_cpath(src, "link", "src"), __ss_cpath(dst, "link", "dst")) == -1)
        __throw_oserror(src, dst);
    return NULL;
}


__ss_int pathconf(str *path, str *name_) {
    if(!pathconf_names->__contains__(name_))
        throw new ValueError(new str("unrecognized configuration name"));
    return pathconf(path, pathconf_names->__getitem__(name_));
}
__ss_int pathconf(str *path, __ss_int name_) {
    /* -1 with errno unchanged means 'no limit' */
    errno = 0;
    long result = ::pathconf(__ss_cpath(path, "pathconf"), __ss_cint(name_));
    if(result == -1 and errno != 0) {
        if(errno == EINVAL) /* as CPython: it could be the name rather than the path */
            __throw_oserror();
        __throw_oserror(path);
    }
    return (__ss_int)result;
}

__ss_int fpathconf(__ss_int fd, str *name_) {
    if(!pathconf_names->__contains__(name_))
        throw new ValueError(new str("unrecognized configuration name"));
    return fpathconf(fd, pathconf_names->__getitem__(name_));
}
__ss_int fpathconf(__ss_int fd, __ss_int name_) {
    int fd_ = __ss_fildes(fd), name2 = __ss_cint(name_);
    errno = 0;
    long result = ::fpathconf(fd_, name2);
    if(result == -1 and errno != 0)
        __throw_oserror();
    return (__ss_int)result;
}

str *confstr(str *name_) {
    if(!confstr_names->__contains__(name_))
        throw new ValueError(new str("unrecognized configuration name"));
    return confstr(confstr_names->__getitem__(name_));
}
str *confstr(__ss_int name_) {
    char buf[MAXENTRIES];
    int name2 = __ss_cint(name_);
    errno = 0;
    size_t size = ::confstr(name2, buf, MAXENTRIES);
    if(size == 0 and errno != 0)
        __throw_oserror();
    if(size == 0)
        return new str(); /* XXX CPython returns None */
    return new str(buf);
}

__ss_int sysconf(str *name_) {
    if(!sysconf_names->__contains__(name_))
        throw new ValueError(new str("unrecognized configuration name"));
    return sysconf(sysconf_names->__getitem__(name_));
}
__ss_int sysconf(__ss_int name_) {
    int name2 = __ss_cint(name_);
    errno = 0;
    long result = ::sysconf(name2);
    if(result == -1 and errno != 0)
        __throw_oserror();
    return (__ss_int)result;
}

tuple<__ss_float> *getloadavg() {
#ifdef __CYGWIN__
    throw new NotImplementedError();
#else
    double load[3];
    if(::getloadavg(load, 3) != 3)
        throw new OSError(new str("os.getloadavg"));
    return new tuple<__ss_float>(3, load[0], load[1], load[2]);
#endif
}

void *mkfifo(str *path, __ss_int mode) {
    if(::mkfifo(__ss_cpath(path, "mkfifo"), (mode_t)__ss_cint(mode)) == -1)
        __throw_oserror();
    return NULL;
}

/* class statvfs_result */

class_ *cl_statvfs_result;

statvfs_result::statvfs_result(str *path) {
    this->__class__ = cl_statvfs_result;
    if(statvfs(__ss_cpath(path, "statvfs"), &vbuf) == -1)
        __throw_oserror(path);
    fill_er_up();
}

statvfs_result::statvfs_result(__ss_int fd) {
    this->__class__ = cl_statvfs_result;
    if(fstatvfs(__ss_cint(fd), &vbuf) == -1)
        __throw_oserror();
    fill_er_up();
}

void statvfs_result::fill_er_up() {
    this->f_bsize = (__ss_int)vbuf.f_bsize;
    this->f_frsize = (__ss_int)vbuf.f_frsize;
    this->f_blocks = (__ss_int)vbuf.f_blocks;
    this->f_bfree = (__ss_int)vbuf.f_bfree;
    this->f_bavail = (__ss_int)vbuf.f_bavail;
    this->f_files = (__ss_int)vbuf.f_files;
    this->f_ffree = (__ss_int)vbuf.f_ffree;
    this->f_favail = (__ss_int)vbuf.f_favail;
    this->f_flag = (__ss_int)vbuf.f_flag;
    this->f_namemax = (__ss_int)vbuf.f_namemax;
    this->f_fsid = (__ss_int)vbuf.f_fsid;
    this->units.assign({f_bsize, f_frsize, f_blocks, f_bfree, f_bavail, f_files, f_ffree, f_favail, f_flag, f_namemax});
}

str *statvfs_result::__repr__() {
    return __mod6(new str("os.statvfs_result(f_bsize=%d, f_frsize=%d, f_blocks=%d, f_bfree=%d, f_bavail=%d, f_files=%d, f_ffree=%d, f_favail=%d, f_flag=%d, f_namemax=%d)"), 10,
        f_bsize, f_frsize, f_blocks, f_bfree, f_bavail, f_files, f_ffree, f_favail, f_flag, f_namemax);
}

statvfs_result *statvfs(str *path) {
    return new statvfs_result(path);
}
statvfs_result *fstatvfs(__ss_int fd) {
    return new statvfs_result(fd);
}

#endif /* WIN32 */

#ifdef WIN32
/* windows versions of posix functionality that cpython also offers there */

/* like cpython: CTRL_C_EVENT/CTRL_BREAK_EVENT go to the console process
   group, anything else terminates the process with sig as its exit code */
void *kill(__ss_int pid, __ss_int sig) {
    if (sig == CTRL_C_EVENT || sig == CTRL_BREAK_EVENT) {
        if (!GenerateConsoleCtrlEvent((DWORD)sig, (DWORD)pid))
            __throw_winerror(GetLastError());
        return NULL;
    }
    HANDLE handle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, (DWORD)pid);
    if (handle == NULL)
        __throw_winerror(GetLastError());
    if (!TerminateProcess(handle, (UINT)sig)) {
        DWORD err = GetLastError();
        CloseHandle(handle);
        __throw_winerror(err);
    }
    CloseHandle(handle);
    return NULL;
}

/* like cpython: pid is a process handle (as returned by spawn*(P_NOWAIT)),
   and the exit code is shifted left by 8 bits in the returned status */
tuple<__ss_int> *waitpid(__ss_int pid, __ss_int options) {
    int status = 0;
    intptr_t res;
    {
        __suppress_iph guard;
        res = ::_cwait(&status, (intptr_t)pid, __ss_cint_i(options));
    }
    if (res == -1)
        __throw_oserror();
    return new tuple<__ss_int>(2, (__ss_int)res, (__ss_int)(((unsigned long long)(unsigned int)status) << 8));
}

void *link(str *src, str *dst) {
    if (!CreateHardLinkW(__to_wide(dst, "link", "dst").c_str(), __to_wide(src, "link", "src").c_str(), NULL))
        __throw_winerror(GetLastError(), src, dst);
    return NULL;
}

str *readlink(str *path) {
    std::error_code ec;
    std::filesystem::path target = std::filesystem::read_symlink(__fspath(path, "readlink"), ec);
    if (ec) {
        std::error_condition c = ec.default_error_condition();
        errno = (c.category() == std::generic_category()) ? c.value() : EINVAL;
        __throw_oserror(path);
    }
    return __fsstr(target);
}

str *getlogin() {
    wchar_t buffer[257]; /* UNLEN + 1 */
    DWORD size = 257;
    if (!GetUserNameW(buffer, &size))
        __throw_winerror(GetLastError());
    return __from_wide(buffer);
}

/* argument and environment vectors for the wide crt exec/spawn functions */
struct __wide_vector {
    std::vector<std::wstring> strings;
    std::vector<const wchar_t *> pointers;

    __wide_vector(list<str *> *args) {
        for (size_t i = 0; i < args->units.size(); i++)
            strings.push_back(__to_wide(args->units[i]));
        finish();
    }
    __wide_vector(dict<str *, str *> *env) {
        for (auto const& [k, v] : env->gcd) {
            if (k->unit.empty() || k->unit.find(U'=', 1) != std::string::npos) /* (as CPython, and posix below) */
                throw new ValueError(new str("illegal environment variable name"));
            strings.push_back(__to_wide(__add_strs(3, k, new str("="), v)));
        }
        finish();
    }
    void finish() {
        for (size_t i = 0; i < strings.size(); i++)
            pointers.push_back(strings[i].c_str());
        pointers.push_back(NULL);
    }
    const wchar_t *const *data() { return pointers.data(); }
};

/* as CPython: 'execv() arg 2 ..', but 'execve: argv ..' (as the posix version below) */
static void __check_exec_args(list<str *> *args, const char *func) {
    bool ve = std::string(func) == "execve()";
    if (args->units.empty())
        throw new ValueError(new str(ve ? "execve: argv must not be empty" : (std::string(func) + " arg 2 must not be empty").c_str()));
    if (args->units[0]->unit.empty())
        throw new ValueError(new str(ve ? "execve: argv first element cannot be empty" : (std::string(func) + " arg 2 first element cannot be empty").c_str()));
}

void *execv(str *file, list<str *> *args) {
    __check_exec_args(args, "execv()");
    __wide_vector argv(args);
    {
        __suppress_iph guard;
        ::_wexecv(__to_wide(file, "execv").c_str(), argv.data());
    }
    __throw_oserror();
}

void *execvp(str *file, list<str *> *args) {
    __check_exec_args(args, "execv()"); /* (CPython: os.execvp calls os.execv) */
    __wide_vector argv(args);
    {
        __suppress_iph guard;
        ::_wexecvp(__to_wide(file, "execv").c_str(), argv.data());
    }
    __throw_oserror();
}

void *execve(str *file, list<str *> *args, dict<str *, str *> *env) {
    __check_exec_args(args, "execve()");
    __wide_vector argv(args), envp(env);
    {
        __suppress_iph guard;
        ::_wexecve(__to_wide(file, "execve").c_str(), argv.data(), envp.data());
    }
    __throw_oserror(file);
}

void *execvpe(str *file, list<str *> *args, dict<str *, str *> *env) {
    __check_exec_args(args, "execve()"); /* (os.execvpe calls os.execve) */
    __wide_vector argv(args), envp(env);
    {
        __suppress_iph guard;
        ::_wexecvpe(__to_wide(file, "execve").c_str(), argv.data(), envp.data());
    }
    __throw_oserror();
}

/* like cpython: P_WAIT returns the exit code, P_NOWAIT a process handle */
static __ss_int __spawn_result(intptr_t r) {
    if (r == -1)
        __throw_oserror();
    return (__ss_int)r;
}

__ss_int spawnv(__ss_int mode, str *file, list<str *> *args) {
    __check_exec_args(args, "spawnv()");
    __wide_vector argv(args);
    __suppress_iph guard;
    return __spawn_result(::_wspawnv(__ss_cint(mode), __to_wide(file).c_str(), argv.data()));
}

__ss_int spawnvp(__ss_int mode, str *file, list<str *> *args) {
    __check_exec_args(args, "spawnvp()");
    __wide_vector argv(args);
    __suppress_iph guard;
    return __spawn_result(::_wspawnvp(__ss_cint(mode), __to_wide(file).c_str(), argv.data()));
}

__ss_int spawnve(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env) {
    __check_exec_args(args, "spawnve()");
    __wide_vector argv(args), envp(env);
    __suppress_iph guard;
    return __spawn_result(::_wspawnve(__ss_cint(mode), __to_wide(file).c_str(), argv.data(), envp.data()));
}

__ss_int spawnvpe(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env) {
    __check_exec_args(args, "spawnvpe()");
    __wide_vector argv(args), envp(env);
    __suppress_iph guard;
    return __spawn_result(::_wspawnvpe(__ss_cint(mode), __to_wide(file).c_str(), argv.data(), envp.data()));
}

#endif /* WIN32 */

/* getpid/getppid/access/fsync/ftruncate/times are declared unconditionally
   in __init__.hpp: posix versions first, then the win32 equivalents. */
#ifndef WIN32

__ss_int getpid() { return (__ss_int)::getpid(); }
__ss_int getppid() { return (__ss_int)::getppid(); }

__ss_bool access(str *path, __ss_int mode) {
    return __mbool(::access(__ss_cpath(path, "access"), __ss_cint(mode)) == 0);
}

void *fsync(__ss_int fd) {
    if(::fsync(__ss_fildes(fd)) == -1)
        __throw_oserror();
    return NULL;
}

void *ftruncate(__ss_int fd, __ss_int n) {
    if (::ftruncate(__ss_cint(fd), n) == -1)
        __throw_oserror();
    return NULL;
}

times_result *times() {
    struct tms buf;
    clock_t c;
    double ticks_per_second = (double)::sysconf(_SC_CLK_TCK);
    if((c = ::times(&buf)) == -1)
        __throw_oserror();
    return new times_result(((__ss_float)buf.tms_utime / ticks_per_second), ((__ss_float)buf.tms_stime / ticks_per_second), ((__ss_float)buf.tms_cutime / ticks_per_second), ((__ss_float)buf.tms_cstime / ticks_per_second), ((__ss_float)c / ticks_per_second));
}

#else /* WIN32 */

__ss_int getpid() { return (__ss_int)GetCurrentProcessId(); }

/* like cpython: walk the process snapshot to find our parent's id */
__ss_int getppid() {
    DWORD pid = GetCurrentProcessId();
    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (snap == INVALID_HANDLE_VALUE)
        throw new OSError(new str("os.getppid"));
    PROCESSENTRY32 pe;
    pe.dwSize = sizeof(pe);
    __ss_int ppid = -1;
    if (Process32First(snap, &pe)) {
        do {
            if (pe.th32ProcessID == pid) {
                ppid = (__ss_int)pe.th32ParentProcessID;
                break;
            }
        } while (Process32Next(snap, &pe));
    }
    CloseHandle(snap);
    if (ppid == -1)
        throw new OSError(new str("os.getppid"));
    return ppid;
}

/* _access() knows 0 (exists), 2 (write), 4 (read) and 6 (read+write); like
   cpython, treat X_OK as 'exists'. */
__ss_bool access(str *path, __ss_int mode) {
    int m = __ss_cint(mode) & (__ss_R_OK | __ss_W_OK);
    return __mbool(::_waccess(__to_wide(path, "access").c_str(), m) == 0);
}

void *fsync(__ss_int fd) {
    int r;
    {
        __suppress_iph guard;
        r = ::_commit(__ss_fildes(fd));
    }
    if(r == -1)
        __throw_oserror();
    return NULL;
}

void *ftruncate(__ss_int fd, __ss_int n) {
    errno_t r;
    {
        __suppress_iph guard;
        r = ::_chsize_s(__ss_cint(fd), (__int64)n);
    }
    if (r != 0)
        __throw_oserror();
    return NULL;
}

/* like cpython: (user, system, children_user=0, children_system=0, elapsed) */
times_result *times() {
    FILETIME create, exit_, kernel, user;
    if (!GetProcessTimes(GetCurrentProcess(), &create, &exit_, &kernel, &user))
        throw new OSError(new str("os.times"));
    ULARGE_INTEGER k, u;
    k.LowPart = kernel.dwLowDateTime; k.HighPart = kernel.dwHighDateTime;
    u.LowPart = user.dwLowDateTime; u.HighPart = user.dwHighDateTime;
    __ss_float elapsed = (__ss_float)GetTickCount64() / 1000.0;
    return new times_result((__ss_float)u.QuadPart / 1e7, (__ss_float)k.QuadPart / 1e7, (__ss_float)0.0, (__ss_float)0.0, elapsed);
}

#endif

/* truncate, closerange, waitstatus_to_exitcode, get/set_inheritable,
   device_encoding and get_terminal_size are declared unconditionally in
   __init__.hpp: posix versions first, then the win32 equivalents. */

class_ *cl_terminal_size;

terminal_size::terminal_size(__ss_int columns, __ss_int lines) : tuple2<__ss_int, __ss_int>(2, columns, lines) {
    this->__class__ = cl_terminal_size;
    this->columns = columns;
    this->lines = lines;
}

terminal_size::terminal_size(tuple<__ss_int> *t) : tuple2<__ss_int, __ss_int>(t) {
    this->__class__ = cl_terminal_size;
    if (len(t) != 2)
        throw new TypeError(__add_strs(3, new str("os.terminal_size() takes a 2-sequence ("), __str(len(t)), new str("-sequence given)")));
    this->columns = t->__getitem__(0);
    this->lines = t->__getitem__(1);
}

str *terminal_size::__repr__() {
    return __add_strs(5, new str("os.terminal_size(columns="), __str(columns), new str(", lines="), __str(lines), new str(")"));
}

class_ *cl_times_result;

times_result::times_result(__ss_float user, __ss_float system, __ss_float children_user, __ss_float children_system, __ss_float elapsed) : tuple2<__ss_float, __ss_float>(5, user, system, children_user, children_system, elapsed) {
    this->__class__ = cl_times_result;
    this->user = user;
    this->system = system;
    this->children_user = children_user;
    this->children_system = children_system;
    this->elapsed = elapsed;
}

times_result::times_result(tuple<__ss_float> *t) : tuple2<__ss_float, __ss_float>(t) {
    this->__class__ = cl_times_result;
    if (len(t) != 5)
        throw new TypeError(__add_strs(3, new str(__SS_POSIX_MOD ".times_result() takes a 5-sequence ("), __str(len(t)), new str("-sequence given)")));
    user = t->__getitem__(0);
    system = t->__getitem__(1);
    children_user = t->__getitem__(2);
    children_system = t->__getitem__(3);
    elapsed = t->__getitem__(4);
}

times_result::times_result(tuple<__ss_int> *t) {
    this->__class__ = cl_times_result;
    if (len(t) != 5)
        throw new TypeError(__add_strs(3, new str(__SS_POSIX_MOD ".times_result() takes a 5-sequence ("), __str(len(t)), new str("-sequence given)")));
    user = (__ss_float)t->__getitem__(0);
    system = (__ss_float)t->__getitem__(1);
    children_user = (__ss_float)t->__getitem__(2);
    children_system = (__ss_float)t->__getitem__(3);
    elapsed = (__ss_float)t->__getitem__(4);
    this->units.assign({user, system, children_user, children_system, elapsed});
}

str *times_result::__repr__() {
    return __add_strs(12, name, new str(".times_result(user="), repr(user), new str(", system="), repr(system), new str(", children_user="), repr(children_user), new str(", children_system="), repr(children_system), new str(", elapsed="), repr(elapsed), new str(")"));
}

#ifndef WIN32

void *truncate(str *path, __ss_int length) {
    if (::truncate(__ss_cpath(path, "truncate"), (off_t)length) == -1)
        __throw_oserror(path);
    return NULL;
}

void *closerange(__ss_int fd_low, __ss_int fd_high) {
    __ss_cint(fd_low);
    __ss_cint(fd_high);
    /* descriptors can't be (much) above the open file limit, so don't loop
       all the way up to e.g. closerange(3, 2**31) */
    long max_fd = ::sysconf(_SC_OPEN_MAX);
    if (max_fd > 0 && fd_high > max_fd)
        fd_high = (__ss_int)max_fd;
    if (fd_low < 0)
        fd_low = 0;
    for (__ss_int fd = fd_low; fd < fd_high; fd++)
        ::close((int)fd); /* errors are ignored */
    return NULL;
}

__ss_int waitstatus_to_exitcode(__ss_int status) {
    int st = __ss_cint(status);
    if (WIFEXITED(st))
        return (__ss_int)WEXITSTATUS(st);
    if (WIFSIGNALED(st))
        return -(__ss_int)WTERMSIG(st);
    if (WIFSTOPPED(st))
        throw new ValueError(__add_strs(2, new str("process stopped by delivery of signal "), __str((__ss_int)WSTOPSIG(st))));
    throw new ValueError(__add_strs(2, new str("invalid wait status: "), __str(status)));
}

__ss_bool get_inheritable(__ss_int fd) {
    int flags = ::fcntl(__ss_cint(fd), F_GETFD);
    if (flags == -1)
        __throw_oserror();
    return __mbool(!(flags & FD_CLOEXEC));
}

void *set_inheritable(__ss_int fd, __ss_bool inheritable) {
    int fd_ = __ss_cint(fd);
    int flags = ::fcntl(fd_, F_GETFD);
    if (flags == -1)
        __throw_oserror();
    int new_flags = inheritable ? (flags & ~FD_CLOEXEC) : (flags | FD_CLOEXEC);
    if (new_flags != flags && ::fcntl(fd_, F_SETFD, new_flags) == -1)
        __throw_oserror();
    return NULL;
}

__ss_bool get_blocking(__ss_int fd) {
    int flags = ::fcntl(__ss_cint(fd), F_GETFL);
    if (flags == -1)
        __throw_oserror();
    return __mbool(!(flags & O_NONBLOCK));
}

void *set_blocking(__ss_int fd, __ss_bool blocking) {
    int fd_ = __ss_cint(fd);
    int flags = ::fcntl(fd_, F_GETFL);
    if (flags == -1)
        __throw_oserror();
    int new_flags = blocking ? (flags & ~O_NONBLOCK) : (flags | O_NONBLOCK);
    if (new_flags != flags && ::fcntl(fd_, F_SETFL, new_flags) == -1)
        __throw_oserror();
    return NULL;
}

/* shedskin behaves like cpython in utf-8 mode (the default from 3.15 on) */
str *device_encoding(__ss_int fd) {
    if (!::isatty(__ss_cint(fd)))
        return NULL;
    return new str("utf-8");
}

terminal_size *get_terminal_size(__ss_int fd) {
    struct winsize w;
    if (::ioctl(__ss_cint(fd), TIOCGWINSZ, &w) != 0)
        __throw_oserror();
    return new terminal_size((__ss_int)w.ws_col, (__ss_int)w.ws_row);
}

#else /* WIN32 */

void *truncate(str *path, __ss_int length) {
    if (length < 0) {
        errno = EINVAL;
        __throw_oserror(path);
    }
    std::error_code ec;
    std::filesystem::resize_file(__fspath(path, "truncate"), (std::uintmax_t)length, ec);
    if (ec) {
        std::error_condition c = ec.default_error_condition();
        errno = (c.category() == std::generic_category()) ? c.value() : EIO;
        __throw_oserror(path);
    }
    return NULL;
}

void *closerange(__ss_int fd_low, __ss_int fd_high) {
    __ss_cint(fd_low);
    __ss_cint(fd_high);
    /* the msvc crt supports at most 8192 low-level descriptors */
    if (fd_high > 8192)
        fd_high = 8192;
    if (fd_low < 0)
        fd_low = 0;
    __suppress_iph guard;
    for (__ss_int fd = fd_low; fd < fd_high; fd++)
        ::_close((int)fd); /* errors are ignored */
    return NULL;
}

/* like cpython: see the _cwait() based os.waitpid() */
__ss_int waitstatus_to_exitcode(__ss_int status) {
    if (status < 0)
        throw new OverflowError(new str("can't convert negative int to unsigned"));
    unsigned long long exitcode = ((unsigned long long)status) >> 8;
    if (exitcode > UINT_MAX)
        throw new ValueError(__add_strs(2, new str("invalid exit code: "), __str((__ss_int)exitcode)));
    return (__ss_int)exitcode;
}

static HANDLE __fd_handle(__ss_int fd) {
    HANDLE h;
    {
        __suppress_iph guard;
        h = (HANDLE)::_get_osfhandle(__ss_cint(fd));
    }
    if (h == INVALID_HANDLE_VALUE) {
        errno = EBADF;
        __throw_oserror();
    }
    return h;
}

__ss_bool get_inheritable(__ss_int fd) {
    DWORD flags;
    if (!GetHandleInformation(__fd_handle(fd), &flags))
        throw new OSError(new str("os.get_inheritable"));
    return __mbool((flags & HANDLE_FLAG_INHERIT) != 0);
}

void *set_inheritable(__ss_int fd, __ss_bool inheritable) {
    if (!SetHandleInformation(__fd_handle(fd), HANDLE_FLAG_INHERIT, inheritable ? HANDLE_FLAG_INHERIT : 0))
        throw new OSError(new str("os.set_inheritable"));
    return NULL;
}

/* like cpython (3.12+): only supported for pipes */
__ss_bool get_blocking(__ss_int fd) {
    DWORD mode;
    if (!GetNamedPipeHandleStateW(__fd_handle(fd), &mode, NULL, NULL, NULL, NULL, 0))
        throw new OSError(new str("os.get_blocking"));
    return __mbool(!(mode & PIPE_NOWAIT));
}

void *set_blocking(__ss_int fd, __ss_bool blocking) {
    DWORD mode = blocking ? PIPE_WAIT : PIPE_NOWAIT;
    if (!SetNamedPipeHandleState(__fd_handle(fd), &mode, NULL, NULL))
        throw new OSError(new str("os.set_blocking"));
    return NULL;
}

/* like cpython: the console code page for the standard streams */
str *device_encoding(__ss_int fd) {
    int tty;
    {
        __suppress_iph guard;
        tty = ::_isatty(__ss_cint(fd));
    }
    if (!tty)
        return NULL;
    UINT cp;
    if (fd == 0)
        cp = GetConsoleCP();
    else if (fd == 1 || fd == 2)
        cp = GetConsoleOutputCP();
    else
        cp = 0;
    if (cp == 0) /* no console */
        return NULL;
    return __add_strs(2, new str("cp"), __str((__ss_int)cp));
}

terminal_size *get_terminal_size(__ss_int fd) {
    DWORD nhandle;
    switch (__ss_cint(fd)) {
        case 0: nhandle = STD_INPUT_HANDLE; break;
        case 1: nhandle = STD_OUTPUT_HANDLE; break;
        case 2: nhandle = STD_ERROR_HANDLE; break;
        default:
            throw new ValueError(new str("bad file descriptor"));
    }
    HANDLE handle = GetStdHandle(nhandle);
    if (handle == NULL)
        throw new OSError(new str("handle cannot be retrieved"));
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    if (handle == INVALID_HANDLE_VALUE || !GetConsoleScreenBufferInfo(handle, &csbi))
        throw new OSError(new str("os.get_terminal_size"));
    return new terminal_size((__ss_int)(csbi.srWindow.Right - csbi.srWindow.Left + 1), (__ss_int)(csbi.srWindow.Bottom - csbi.srWindow.Top + 1));
}

#endif

/* lseek is declared unconditionally in __init__.hpp (it's cross-platform,
   unlike the UNIX-only functionality above and below), so it must be
   defined for both WIN32 and non-WIN32 builds. */
#ifdef WIN32
__ss_int lseek(__ss_int fd, __ss_int pos, __ss_int how) {
    __int64 r;
    {
        __suppress_iph guard;
        r = ::_lseeki64(__ss_cint(fd), (__int64)pos, __ss_cint(how));
    }
    if(r == -1)
        __throw_oserror();
    return (__ss_int)r;
}
#else
__ss_int lseek(__ss_int fd, __ss_int pos, __ss_int how) {
    off_t r = ::lseek(__ss_cint(fd), pos, __ss_cint(how));
    if(r == -1)
        __throw_oserror();
    return (__ss_int)r;
}
#endif

/* symlink is declared unconditionally in __init__.hpp */
#ifdef WIN32
void *symlink(str *src, str *dst, __ss_bool target_is_directory) {
    /* like cpython: pick the directory flag when asked to, or when the
       target exists and is a directory */
    std::error_code ec;
    std::filesystem::path target = __fspath(dst, "symlink", "dst").parent_path() / __fspath(src, "symlink", "src");
    DWORD flags = (target_is_directory || std::filesystem::is_directory(target, ec)) ? SYMBOLIC_LINK_FLAG_DIRECTORY : 0;
#ifdef SYMBOLIC_LINK_FLAG_ALLOW_UNPRIVILEGED_CREATE
    flags |= SYMBOLIC_LINK_FLAG_ALLOW_UNPRIVILEGED_CREATE;
#endif
    if(!CreateSymbolicLinkW(__to_wide(dst, "symlink", "dst").c_str(), __to_wide(src, "symlink", "src").c_str(), flags))
        __throw_winerror(GetLastError(), src, dst);
    return NULL;
}
#else
void *symlink(str *src, str *dst, __ss_bool) { /* target_is_directory: windows only */
    if(::symlink(__ss_cpath(src, "symlink", "src"), __ss_cpath(dst, "symlink", "dst")) == -1)
        __throw_oserror(src, dst);
    return NULL;
}
#endif

list<str *> *get_exec_path(dict<str *, str *> *env) {
    if(!env)
        env = __ss_environ;
    str *key = new str("PATH");
    str *envpath;
    if(env->__contains__(key))
        envpath = env->get(key);
    else
        envpath = defpath;
    return envpath->split(pathsep);
}

#ifndef WIN32

/* a dev_t argument as cpython converts it (-1 is NODEV) */
static dev_t __ss_dev(__ss_int v) {
    if(v == -1)
        return (dev_t)-1;
    if(v < 0)
        throw new OverflowError(new str("can't convert negative int to unsigned"));
    if constexpr (sizeof(__ss_int) > sizeof(unsigned long long)) {
        if(v > (__ss_int)ULLONG_MAX)
            throw new OverflowError(new str("int too big to convert"));
    }
    /* dev_t may be narrower, or signed (macOS: int32_t) */
    if((__ss_int)(dev_t)v != v)
        throw new OverflowError(new str("Python int too large to convert to C dev_t"));
    return (dev_t)v;
}

/* major and minor device numbers are unsigned ints, with NODEV as -1 */
static unsigned int __ss_devnum(__ss_int v) {
    dev_t d = __ss_dev(v);
    if(d != (dev_t)-1 && (dev_t)(unsigned int)d != d)
        throw new OverflowError(new str("Python int too large to convert to C unsigned int"));
    return (unsigned int)d;
}
static __ss_int __ss_from_devnum(unsigned int n) {
    return n == UINT_MAX ? -1 : (__ss_int)n;
}

__ss_int __ss_makedev(__ss_int major, __ss_int minor) {
    unsigned int major_ = __ss_devnum(major);
    unsigned int minor_ = __ss_devnum(minor);
    return (__ss_int)makedev(major_, minor_);
}
__ss_int __ss_major(__ss_int dev) {
    return __ss_from_devnum(major(__ss_dev(dev)));
}
__ss_int __ss_minor(__ss_int dev) {
    return __ss_from_devnum(minor(__ss_dev(dev)));
}

void *mknod(str *filename, __ss_int mode, __ss_int device) {
    if(::mknod(__ss_cpath(filename, "mknod"), (mode_t)__ss_cint(mode), __ss_dev(device)) == -1)
        __throw_oserror();
    return NULL;
}

#ifndef __APPLE__
void *__mknod_at(int dir_fd, str *path, __ss_int mode, __ss_int device) {
    if(::mknodat(__at_fd(dir_fd), __ss_cpath(path, "mknod"), (mode_t)__ss_cint(mode), __ss_dev(device)) == -1)
        __throw_oserror();
    return NULL;
}
#endif

/* the argv/envp arrays live in GC-scanned static vectors, so the strings they
 * point into stay alive until exec replaces the process (or fails) */
char **__exec_argvlist(list<str *> *args) {
    static __GC_VECTOR(char *) argvlist;
    argvlist.clear();
    for(__ss_int i = 0; i < args->__len__(); ++i) {
        argvlist.push_back(__ss_cpath(args->__getitem__(i)));
    }
    argvlist.push_back(NULL);
    return argvlist.data();
}

char **__exec_envplist(dict<str *, str *> *env) {
    static __GC_VECTOR(char *) envplist;
    envplist.clear();
    list<tuple<str *> *> *items = new list<tuple<str *> *>(env->items());
    for(__ss_int i=0; i < items->__len__(); i++) {
        str *key = items->__getitem__(i)->__getfirst__();
        if (key->unit.empty() || key->unit.find(U'=', 1) != std::string::npos) /* (as CPython: a leading '=' is ok) */
            throw new ValueError(new str("illegal environment variable name"));
        envplist.push_back(__ss_cpath(__add_strs(3, items->__getitem__(i)->__getfirst__(), new str("="), items->__getitem__(i)->__getsecond__())));
    }
    envplist.push_back(NULL);
    return envplist.data();
}

/* as CPython: 'execv() arg 2 ..', but 'execve: argv ..' */
static void __check_exec_args(list<str *> *args, const char *func) {
    bool ve = std::string(func) == "execve()";
    if (args->units.empty())
        throw new ValueError(new str(ve ? "execve: argv must not be empty" : (std::string(func) + " arg 2 must not be empty").c_str()));
    if (args->units[0]->unit.empty())
        throw new ValueError(new str(ve ? "execve: argv first element cannot be empty" : (std::string(func) + " arg 2 first element cannot be empty").c_str()));
}

void *execv(str* file, list<str*>* args) {
    __check_exec_args(args, "execv()");
    ::execv(__ss_cpath(file, "execv"), __exec_argvlist(args));
    __throw_oserror();
}

void *execve(str* file, list<str*>* args, dict<str *, str *> *env) {
    __check_exec_args(args, "execve()");
    ::execve(__ss_cpath(file, "execve"), __exec_argvlist(args), __exec_envplist(env));
    __throw_oserror(file);
}

/* as CPython's os._execvpe: try each PATH entry, and raise the first error
   other than ENOENT/ENOTDIR (e.g. EACCES), else the last one */
static void *__execvpe(str* file, list<str*>* args, dict<str *, str *> *env) {
    __ss_check_nul(file, "execve"); /* (else no PATH entry exists, giving an OSError) */
    tuple<str *> *h_t = __path__::split(file);
    if( ___bool(h_t->__getfirst__())) {
        if(env)
            execve(file, args, env);
        execv(file, args);
    }
    __check_exec_args(args, env ? "execve()" : "execv()");
    list<str *> *PATH = env ? get_exec_path(env) : get_exec_path();
    /* (kept as errno + filename: a rethrown OSError * would lose its
       subclass, e.g. FileNotFoundError, for 'except') */
    int saved = 0, last = 0;
    str *saved_name = 0, *last_name = file;
    for(__ss_int i = 0; i < PATH->__len__(); ++i) {
        str* fullname = __path__::join(2, PATH->__getfast__(i), file);
        try {
            if(env)
                execve(fullname, args, env);
            execv(fullname, args);
        } catch (OSError *e) {
            last = (int)e->__ss_errno;
            last_name = e->filename;
            if(!saved && last != ENOENT && last != ENOTDIR) {
                saved = last;
                saved_name = e->filename;
            }
        }
    }
    errno = saved ? saved : last ? last : ENOENT;
    __throw_oserror(saved ? saved_name : last_name);
}

void *execvp(str* file, list<str*>* args) {
    return __execvpe(file, args, 0);
}

void *execvpe(str* file, list<str*>* args, dict<str *, str *> *env) {
    return __execvpe(file, args, env);
}

/* as CPython's os._spawnvef: checked before forking */
static void __spawn_check_args(list<str *> *args) {
    if (args->units.empty() || args->units[0]->unit.empty())
        throw new ValueError(new str("argv first element cannot be empty"));
}

/* like CPython: P_WAIT gives the exit code, or -signal for a killed child */
static __ss_int __spawn_wait_result(__ss_int pid) {
    tuple<__ss_int> *t = waitpid(pid, 0);
    __ss_int status = t->__getsecond__();
    if (WIFSIGNALED(status))
        return -WTERMSIG(status);
    return WEXITSTATUS(status);
}

__ss_int spawnv(__ss_int mode, str *file, list<str *> *args) {
    __spawn_check_args(args);
    __ss_int pid;
    if(!(pid = fork())) {
        try { execv(file, args); } catch (...) {}
        ::_exit(127);
    }
    else if (mode != __ss_P_NOWAIT) /* (as CPython: only P_NOWAIT returns the pid) */
        return __spawn_wait_result(pid);
    return pid;
}

__ss_int spawnvp(__ss_int mode, str *file, list<str *> *args) {
    __spawn_check_args(args);
    __ss_int pid;
    if(!(pid = fork())) {
        try { execvp(file, args); } catch (...) {}
        ::_exit(127);
    }
    else if (mode != __ss_P_NOWAIT) /* (as CPython: only P_NOWAIT returns the pid) */
        return __spawn_wait_result(pid);
    return pid;
}

__ss_int spawnve(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env) {
    __spawn_check_args(args);
    __ss_int pid;
    if(!(pid = fork())) {
        try { execve(file, args, env); } catch (...) {}
        ::_exit(127);
    }
    else if (mode != __ss_P_NOWAIT) /* (as CPython: only P_NOWAIT returns the pid) */
        return __spawn_wait_result(pid);
    return pid;
}

__ss_int spawnvpe(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env) {
    __spawn_check_args(args);
    __ss_int pid;
    if(!(pid = fork())) {
        try { execvpe(file, args, env); } catch (...) {}
        ::_exit(127);
    }
    else if (mode != __ss_P_NOWAIT) /* (as CPython: only P_NOWAIT returns the pid) */
        return __spawn_wait_result(pid);
    return pid;
}

#endif

/* pipe is declared unconditionally in __init__.hpp */
tuple<__ss_int>* pipe() {
    int fds[2];
    __ss_int ret;

#ifdef WIN32
    ret = ::_pipe(fds, 4096, _O_BINARY | _O_NOINHERIT);
#elif defined(__APPLE__)
    ret = ::pipe(fds);
#else
    ret = ::pipe2(fds, O_CLOEXEC);
#endif

    if(ret != 0) {
        __throw_oserror(); /* (no filename, as CPython) */
    }

#ifdef __APPLE__
    set_inheritable(fds[0], False);
    set_inheritable(fds[1], False);
#endif

    return new tuple<__ss_int>(2,(__ss_int)fds[0],(__ss_int)fds[1]);
}

/* like cpython: update os.environ in place from the process environment,
   so references to it stay valid */
void *reload_environ() {
    __ss_environ->clear();
    str *eq = new str("=");
    for (__ss_int n = 0; environ[n]; n++) {
        str *line = new str(environ[n]);
        __ss_int pos = line->find(eq);
#ifdef WIN32
        /* skip the hidden per-drive '=C:=C:\\...' entries, like cpython */
        if (pos == 0)
            pos = line->find(eq, 1);
#endif
        if (pos <= 0)
            continue;
        __ss_environ->__setitem__(line->__slice__(2, 0, pos, 0), line->__slice__(1, (pos+1), 0, 0));
    }
    return NULL;
}

void __init() {
    cl_stat_result = new class_("stat_result");
    cl_DirEntry = new class_("DirEntry");
    cl_ScandirIterator = new class_("ScandirIterator");
    cl_terminal_size = new class_("terminal_size");
    cl_times_result = new class_("times_result");

#ifdef WIN32
    linesep = new str("\r\n");
    name = new str("nt");
#else
    linesep = new str("\n");
    name = new str("posix");
    cl_statvfs_result = new class_("statvfs_result");
    cl_uname_result = new class_("uname_result");
#endif

    __ss_environ = new dict<str *, str *>();
    reload_environ();

    __path__::__init(); /* ugh */

    curdir = __path__::curdir;
    pardir = __path__::pardir;
    extsep = __path__::extsep;
    sep = __path__::sep;
    pathsep = __path__::pathsep;
    defpath = __path__::defpath;
    altsep = __path__::altsep;
    devnull = __path__::devnull;

#ifdef WIN32
    __ss_F_OK = 0;
    __ss_R_OK = 4;
    __ss_W_OK = 2;
    __ss_X_OK = 1;
#else
#ifdef F_OK
    __ss_F_OK = F_OK;
#endif
#ifdef R_OK
    __ss_R_OK = R_OK;
#endif
#ifdef W_OK
    __ss_W_OK = W_OK;
#endif
#ifdef X_OK
    __ss_X_OK = X_OK;
#endif
#endif
#ifdef NGROUPS_MAX
    __ss_NGROUPS_MAX = NGROUPS_MAX;
#endif
#ifdef TMP_MAX
    __ss_TMP_MAX = TMP_MAX;
#endif
#ifdef WCONTINUED
    __ss_WCONTINUED = WCONTINUED;
#endif
#ifdef WNOHANG
    __ss_WNOHANG = WNOHANG;
#endif
#ifdef WUNTRACED
    __ss_WUNTRACED = WUNTRACED;
#endif
#ifdef O_RDONLY
    __ss_O_RDONLY = O_RDONLY;
#endif
#ifdef O_WRONLY
    __ss_O_WRONLY = O_WRONLY;
#endif
#ifdef O_RDWR
    __ss_O_RDWR = O_RDWR;
#endif
#ifdef O_NDELAY
    __ss_O_NDELAY = O_NDELAY;
#endif
#ifdef O_NONBLOCK
    __ss_O_NONBLOCK = O_NONBLOCK;
#endif
#ifdef O_APPEND
    __ss_O_APPEND = O_APPEND;
#endif
#ifdef O_DSYNC
    __ss_O_DSYNC = O_DSYNC;
#endif
#ifdef O_RSYNC
    __ss_O_RSYNC = O_RSYNC;
#endif
#ifdef O_SYNC
    __ss_O_SYNC = O_SYNC;
#endif
#ifdef O_NOCTTY
    __ss_O_NOCTTY = O_NOCTTY;
#endif
#ifdef O_CREAT
    __ss_O_CREAT = O_CREAT;
#endif
#ifdef O_EXCL
    __ss_O_EXCL = O_EXCL;
#endif
#ifdef O_TRUNC
    __ss_O_TRUNC = O_TRUNC;
#endif
#ifdef O_BINARY
    __ss_O_BINARY = O_BINARY;
#endif
#ifdef O_TEXT
    __ss_O_TEXT = O_TEXT;
#endif
#ifdef O_LARGEFILE
    __ss_O_LARGEFILE = O_LARGEFILE;
#endif
#ifdef O_SHLOCK
    __ss_O_SHLOCK = O_SHLOCK;
#endif
#ifdef O_EXLOCK
    __ss_O_EXLOCK = O_EXLOCK;
#endif
#ifdef O_NOINHERIT
    __ss_O_NOINHERIT = O_NOINHERIT;
#endif
#ifdef _O_SHORT_LIVED
    __ss__O_SHORT_LIVED = _O_SHORT_LIVED;
#endif
#ifdef O_TEMPORARY
    __ss_O_TEMPORARY = O_TEMPORARY;
#endif
#ifdef O_RANDOM
    __ss_O_RANDOM = O_RANDOM;
#endif
#ifdef O_SEQUENTIAL
    __ss_O_SEQUENTIAL = O_SEQUENTIAL;
#endif
#ifdef O_ASYNC
    __ss_O_ASYNC = O_ASYNC;
#endif
#ifdef O_DIRECT
    __ss_O_DIRECT = O_DIRECT;
#endif
#ifdef O_DIRECTORY
    __ss_O_DIRECTORY = O_DIRECTORY;
#endif
#ifdef O_NOFOLLOW
    __ss_O_NOFOLLOW = O_NOFOLLOW;
#endif
#ifdef O_NOATIME
    __ss_O_NOATIME = O_NOATIME;
#endif
#ifdef EX_OK
    __ss_EX_OK = EX_OK;
#endif
#ifdef EX_USAGE
    __ss_EX_USAGE = EX_USAGE;
#endif
#ifdef EX_DATAERR
    __ss_EX_DATAERR = EX_DATAERR;
#endif
#ifdef EX_NOINPUT
    __ss_EX_NOINPUT = EX_NOINPUT;
#endif
#ifdef EX_NOUSER
    __ss_EX_NOUSER = EX_NOUSER;
#endif
#ifdef EX_NOHOST
    __ss_EX_NOHOST = EX_NOHOST;
#endif
#ifdef EX_UNAVAILABLE
    __ss_EX_UNAVAILABLE = EX_UNAVAILABLE;
#endif
#ifdef EX_SOFTWARE
    __ss_EX_SOFTWARE = EX_SOFTWARE;
#endif
#ifdef EX_OSERR
    __ss_EX_OSERR = EX_OSERR;
#endif
#ifdef EX_OSFILE
    __ss_EX_OSFILE = EX_OSFILE;
#endif
#ifdef EX_CANTCREAT
    __ss_EX_CANTCREAT = EX_CANTCREAT;
#endif
#ifdef EX_IOERR
    __ss_EX_IOERR = EX_IOERR;
#endif
#ifdef EX_TEMPFAIL
    __ss_EX_TEMPFAIL = EX_TEMPFAIL;
#endif
#ifdef EX_PROTOCOL
    __ss_EX_PROTOCOL = EX_PROTOCOL;
#endif
#ifdef EX_NOPERM
    __ss_EX_NOPERM = EX_NOPERM;
#endif
#ifdef EX_CONFIG
    __ss_EX_CONFIG = EX_CONFIG;
#endif
#ifdef EX_NOTFOUND
    __ss_EX_NOTFOUND = EX_NOTFOUND;
#endif

#ifdef WIN32
    __ss_P_WAIT = _P_WAIT;
    __ss_P_NOWAIT = _P_NOWAIT;
    __ss_P_NOWAITO = _P_NOWAITO;
    __ss_P_OVERLAY = _P_OVERLAY;
    __ss_P_DETACH = _P_DETACH;
#else
    __ss_P_WAIT = 0;
    __ss_P_NOWAIT = 1;
    __ss_P_NOWAITO = 1;
    __ss_P_OVERLAY = 2; /* (windows only in cpython) */
    __ss_P_DETACH = 3; /* (windows only in cpython) */
#endif

#ifdef SEEK_CUR
    __ss_SEEK_CUR = SEEK_CUR;
#endif
#ifdef SEEK_DATA
    __ss_SEEK_DATA = SEEK_DATA;
#endif
#ifdef GRND_NONBLOCK
    __ss_GRND_NONBLOCK = GRND_NONBLOCK;
#endif
#ifdef GRND_RANDOM
    __ss_GRND_RANDOM = GRND_RANDOM;
#endif
#ifdef SEEK_HOLE
    __ss_SEEK_HOLE = SEEK_HOLE;
#endif
#ifdef SEEK_END
    __ss_SEEK_END = SEEK_END;
#endif
#ifdef SEEK_SET
    __ss_SEEK_SET = SEEK_SET;
#endif

    pathconf_names = new dict<str *, __ss_int>();
#ifdef _PC_ABI_AIO_XFER_MAX
    pathconf_names->__setitem__(new str("PC_ABI_AIO_XFER_MAX"), _PC_ABI_AIO_XFER_MAX);
#endif
#ifdef _PC_ABI_ASYNC_IO
    pathconf_names->__setitem__(new str("PC_ABI_ASYNC_IO"), _PC_ABI_ASYNC_IO);
#endif
#ifdef _PC_ASYNC_IO
    pathconf_names->__setitem__(new str("PC_ASYNC_IO"), _PC_ASYNC_IO);
#endif
#ifdef _PC_CHOWN_RESTRICTED
    pathconf_names->__setitem__(new str("PC_CHOWN_RESTRICTED"), _PC_CHOWN_RESTRICTED);
#endif
#ifdef _PC_FILESIZEBITS
    pathconf_names->__setitem__(new str("PC_FILESIZEBITS"), _PC_FILESIZEBITS);
#endif
#ifdef _PC_LAST
    pathconf_names->__setitem__(new str("PC_LAST"), _PC_LAST);
#endif
#ifdef _PC_LINK_MAX
    pathconf_names->__setitem__(new str("PC_LINK_MAX"), _PC_LINK_MAX);
#endif
#ifdef _PC_MAX_CANON
    pathconf_names->__setitem__(new str("PC_MAX_CANON"), _PC_MAX_CANON);
#endif
#ifdef _PC_MAX_INPUT
    pathconf_names->__setitem__(new str("PC_MAX_INPUT"), _PC_MAX_INPUT);
#endif
#ifdef _PC_NAME_MAX
    pathconf_names->__setitem__(new str("PC_NAME_MAX"), _PC_NAME_MAX);
#endif
#ifdef _PC_ALLOC_SIZE_MIN
    pathconf_names->__setitem__(new str("PC_ALLOC_SIZE_MIN"), _PC_ALLOC_SIZE_MIN);
#endif
#ifdef _PC_REC_INCR_XFER_SIZE
    pathconf_names->__setitem__(new str("PC_REC_INCR_XFER_SIZE"), _PC_REC_INCR_XFER_SIZE);
#endif
#ifdef _PC_REC_MAX_XFER_SIZE
    pathconf_names->__setitem__(new str("PC_REC_MAX_XFER_SIZE"), _PC_REC_MAX_XFER_SIZE);
#endif
#ifdef _PC_REC_MIN_XFER_SIZE
    pathconf_names->__setitem__(new str("PC_REC_MIN_XFER_SIZE"), _PC_REC_MIN_XFER_SIZE);
#endif
#ifdef _PC_REC_XFER_ALIGN
    pathconf_names->__setitem__(new str("PC_REC_XFER_ALIGN"), _PC_REC_XFER_ALIGN);
#endif
#ifdef _PC_SYMLINK_MAX
    pathconf_names->__setitem__(new str("PC_SYMLINK_MAX"), _PC_SYMLINK_MAX);
#endif
#ifdef _PC_NO_TRUNC
    pathconf_names->__setitem__(new str("PC_NO_TRUNC"), _PC_NO_TRUNC);
#endif
#ifdef _PC_PATH_MAX
    pathconf_names->__setitem__(new str("PC_PATH_MAX"), _PC_PATH_MAX);
#endif
#ifdef _PC_PIPE_BUF
    pathconf_names->__setitem__(new str("PC_PIPE_BUF"), _PC_PIPE_BUF);
#endif
#ifdef _PC_PRIO_IO
    pathconf_names->__setitem__(new str("PC_PRIO_IO"), _PC_PRIO_IO);
#endif
#ifdef _PC_SOCK_MAXBUF
    pathconf_names->__setitem__(new str("PC_SOCK_MAXBUF"), _PC_SOCK_MAXBUF);
#endif
#ifdef _PC_SYNC_IO
    pathconf_names->__setitem__(new str("PC_SYNC_IO"), _PC_SYNC_IO);
#endif
#ifdef _PC_VDISABLE
    pathconf_names->__setitem__(new str("PC_VDISABLE"), _PC_VDISABLE);
#endif

    confstr_names = new dict<str *, __ss_int>();
#ifdef _CS_ARCHITECTURE
    confstr_names->__setitem__(new str("CS_ARCHITECTURE"), _CS_ARCHITECTURE);
#endif
#ifdef _CS_HOSTNAME
    confstr_names->__setitem__(new str("CS_HOSTNAME"), _CS_HOSTNAME);
#endif
#ifdef _CS_HW_PROVIDER
    confstr_names->__setitem__(new str("CS_HW_PROVIDER"), _CS_HW_PROVIDER);
#endif
#ifdef _CS_HW_SERIAL
    confstr_names->__setitem__(new str("CS_HW_SERIAL"), _CS_HW_SERIAL);
#endif
#ifdef _CS_INITTAB_NAME
    confstr_names->__setitem__(new str("CS_INITTAB_NAME"), _CS_INITTAB_NAME);
#endif
#ifdef _CS_LFS64_CFLAGS
    confstr_names->__setitem__(new str("CS_LFS64_CFLAGS"), _CS_LFS64_CFLAGS);
#endif
#ifdef _CS_LFS64_LDFLAGS
    confstr_names->__setitem__(new str("CS_LFS64_LDFLAGS"), _CS_LFS64_LDFLAGS);
#endif
#ifdef _CS_LFS64_LIBS
    confstr_names->__setitem__(new str("CS_LFS64_LIBS"), _CS_LFS64_LIBS);
#endif
#ifdef _CS_LFS64_LINTFLAGS
    confstr_names->__setitem__(new str("CS_LFS64_LINTFLAGS"), _CS_LFS64_LINTFLAGS);
#endif
#ifdef _CS_LFS_CFLAGS
    confstr_names->__setitem__(new str("CS_LFS_CFLAGS"), _CS_LFS_CFLAGS);
#endif
#ifdef _CS_LFS_LDFLAGS
    confstr_names->__setitem__(new str("CS_LFS_LDFLAGS"), _CS_LFS_LDFLAGS);
#endif
#ifdef _CS_LFS_LIBS
    confstr_names->__setitem__(new str("CS_LFS_LIBS"), _CS_LFS_LIBS);
#endif
#ifdef _CS_LFS_LINTFLAGS
    confstr_names->__setitem__(new str("CS_LFS_LINTFLAGS"), _CS_LFS_LINTFLAGS);
#endif
#ifdef _CS_MACHINE
    confstr_names->__setitem__(new str("CS_MACHINE"), _CS_MACHINE);
#endif
#ifdef _CS_PATH
    confstr_names->__setitem__(new str("CS_PATH"), _CS_PATH);
#endif
#ifdef _CS_GNU_LIBC_VERSION
    confstr_names->__setitem__(new str("CS_GNU_LIBC_VERSION"), _CS_GNU_LIBC_VERSION);
#endif
#ifdef _CS_GNU_LIBPTHREAD_VERSION
    confstr_names->__setitem__(new str("CS_GNU_LIBPTHREAD_VERSION"), _CS_GNU_LIBPTHREAD_VERSION);
#endif
#ifdef _CS_RELEASE
    confstr_names->__setitem__(new str("CS_RELEASE"), _CS_RELEASE);
#endif
#ifdef _CS_SRPC_DOMAIN
    confstr_names->__setitem__(new str("CS_SRPC_DOMAIN"), _CS_SRPC_DOMAIN);
#endif
#ifdef _CS_SYSNAME
    confstr_names->__setitem__(new str("CS_SYSNAME"), _CS_SYSNAME);
#endif
#ifdef _CS_VERSION
    confstr_names->__setitem__(new str("CS_VERSION"), _CS_VERSION);
#endif
#ifdef _CS_XBS5_ILP32_OFF32_CFLAGS
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFF32_CFLAGS"), _CS_XBS5_ILP32_OFF32_CFLAGS);
#endif
#ifdef _CS_XBS5_ILP32_OFF32_LDFLAGS
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFF32_LDFLAGS"), _CS_XBS5_ILP32_OFF32_LDFLAGS);
#endif
#ifdef _CS_XBS5_ILP32_OFF32_LIBS
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFF32_LIBS"), _CS_XBS5_ILP32_OFF32_LIBS);
#endif
#ifdef _CS_XBS5_ILP32_OFF32_LINTFLAGS
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFF32_LINTFLAGS"), _CS_XBS5_ILP32_OFF32_LINTFLAGS);
#endif
#ifdef _CS_XBS5_ILP32_OFFBIG_CFLAGS
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFFBIG_CFLAGS"), _CS_XBS5_ILP32_OFFBIG_CFLAGS);
#endif
#ifdef _CS_XBS5_ILP32_OFFBIG_LDFLAGS
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFFBIG_LDFLAGS"), _CS_XBS5_ILP32_OFFBIG_LDFLAGS);
#endif
#ifdef _CS_XBS5_ILP32_OFFBIG_LIBS
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFFBIG_LIBS"), _CS_XBS5_ILP32_OFFBIG_LIBS);
#endif
#ifdef _CS_XBS5_ILP32_OFFBIG_LINTFLAGS
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFFBIG_LINTFLAGS"), _CS_XBS5_ILP32_OFFBIG_LINTFLAGS);
#endif
#ifdef _CS_XBS5_LP64_OFF64_CFLAGS
    confstr_names->__setitem__(new str("CS_XBS5_LP64_OFF64_CFLAGS"), _CS_XBS5_LP64_OFF64_CFLAGS);
#endif
#ifdef _CS_XBS5_LP64_OFF64_LDFLAGS
    confstr_names->__setitem__(new str("CS_XBS5_LP64_OFF64_LDFLAGS"), _CS_XBS5_LP64_OFF64_LDFLAGS);
#endif
#ifdef _CS_XBS5_LP64_OFF64_LIBS
    confstr_names->__setitem__(new str("CS_XBS5_LP64_OFF64_LIBS"), _CS_XBS5_LP64_OFF64_LIBS);
#endif
#ifdef _CS_XBS5_LP64_OFF64_LINTFLAGS
    confstr_names->__setitem__(new str("CS_XBS5_LP64_OFF64_LINTFLAGS"), _CS_XBS5_LP64_OFF64_LINTFLAGS);
#endif
#ifdef _CS_XBS5_LPBIG_OFFBIG_CFLAGS
    confstr_names->__setitem__(new str("CS_XBS5_LPBIG_OFFBIG_CFLAGS"), _CS_XBS5_LPBIG_OFFBIG_CFLAGS);
#endif
#ifdef _CS_XBS5_LPBIG_OFFBIG_LDFLAGS
    confstr_names->__setitem__(new str("CS_XBS5_LPBIG_OFFBIG_LDFLAGS"), _CS_XBS5_LPBIG_OFFBIG_LDFLAGS);
#endif
#ifdef _CS_XBS5_LPBIG_OFFBIG_LIBS
    confstr_names->__setitem__(new str("CS_XBS5_LPBIG_OFFBIG_LIBS"), _CS_XBS5_LPBIG_OFFBIG_LIBS);
#endif
#ifdef _CS_XBS5_LPBIG_OFFBIG_LINTFLAGS
    confstr_names->__setitem__(new str("CS_XBS5_LPBIG_OFFBIG_LINTFLAGS"), _CS_XBS5_LPBIG_OFFBIG_LINTFLAGS);
#endif
#ifdef _MIPS_CS_AVAIL_PROCESSORS
    confstr_names->__setitem__(new str("MIPS_CS_AVAIL_PROCESSORS"), _MIPS_CS_AVAIL_PROCESSORS);
#endif
#ifdef _MIPS_CS_BASE
    confstr_names->__setitem__(new str("MIPS_CS_BASE"), _MIPS_CS_BASE);
#endif
#ifdef _MIPS_CS_HOSTID
    confstr_names->__setitem__(new str("MIPS_CS_HOSTID"), _MIPS_CS_HOSTID);
#endif
#ifdef _MIPS_CS_HW_NAME
    confstr_names->__setitem__(new str("MIPS_CS_HW_NAME"), _MIPS_CS_HW_NAME);
#endif
#ifdef _MIPS_CS_NUM_PROCESSORS
    confstr_names->__setitem__(new str("MIPS_CS_NUM_PROCESSORS"), _MIPS_CS_NUM_PROCESSORS);
#endif
#ifdef _MIPS_CS_OSREL_MAJ
    confstr_names->__setitem__(new str("MIPS_CS_OSREL_MAJ"), _MIPS_CS_OSREL_MAJ);
#endif
#ifdef _MIPS_CS_OSREL_MIN
    confstr_names->__setitem__(new str("MIPS_CS_OSREL_MIN"), _MIPS_CS_OSREL_MIN);
#endif
#ifdef _MIPS_CS_OSREL_PATCH
    confstr_names->__setitem__(new str("MIPS_CS_OSREL_PATCH"), _MIPS_CS_OSREL_PATCH);
#endif
#ifdef _MIPS_CS_OS_NAME
    confstr_names->__setitem__(new str("MIPS_CS_OS_NAME"), _MIPS_CS_OS_NAME);
#endif
#ifdef _MIPS_CS_OS_PROVIDER
    confstr_names->__setitem__(new str("MIPS_CS_OS_PROVIDER"), _MIPS_CS_OS_PROVIDER);
#endif
#ifdef _MIPS_CS_PROCESSORS
    confstr_names->__setitem__(new str("MIPS_CS_PROCESSORS"), _MIPS_CS_PROCESSORS);
#endif
#ifdef _MIPS_CS_SERIAL
    confstr_names->__setitem__(new str("MIPS_CS_SERIAL"), _MIPS_CS_SERIAL);
#endif
#ifdef _MIPS_CS_VENDOR
    confstr_names->__setitem__(new str("MIPS_CS_VENDOR"), _MIPS_CS_VENDOR);
#endif

    sysconf_names = new dict<str *, __ss_int>();
#ifdef _SC_2_CHAR_TERM
    sysconf_names->__setitem__(new str("SC_2_CHAR_TERM"), _SC_2_CHAR_TERM);
#endif
#ifdef _SC_2_C_BIND
    sysconf_names->__setitem__(new str("SC_2_C_BIND"), _SC_2_C_BIND);
#endif
#ifdef _SC_2_C_DEV
    sysconf_names->__setitem__(new str("SC_2_C_DEV"), _SC_2_C_DEV);
#endif
#ifdef _SC_2_C_VERSION
    sysconf_names->__setitem__(new str("SC_2_C_VERSION"), _SC_2_C_VERSION);
#endif
#ifdef _SC_2_FORT_DEV
    sysconf_names->__setitem__(new str("SC_2_FORT_DEV"), _SC_2_FORT_DEV);
#endif
#ifdef _SC_2_FORT_RUN
    sysconf_names->__setitem__(new str("SC_2_FORT_RUN"), _SC_2_FORT_RUN);
#endif
#ifdef _SC_2_LOCALEDEF
    sysconf_names->__setitem__(new str("SC_2_LOCALEDEF"), _SC_2_LOCALEDEF);
#endif
#ifdef _SC_2_SW_DEV
    sysconf_names->__setitem__(new str("SC_2_SW_DEV"), _SC_2_SW_DEV);
#endif
#ifdef _SC_2_UPE
    sysconf_names->__setitem__(new str("SC_2_UPE"), _SC_2_UPE);
#endif
#ifdef _SC_2_VERSION
    sysconf_names->__setitem__(new str("SC_2_VERSION"), _SC_2_VERSION);
#endif
#ifdef _SC_ABI_ASYNCHRONOUS_IO
    sysconf_names->__setitem__(new str("SC_ABI_ASYNCHRONOUS_IO"), _SC_ABI_ASYNCHRONOUS_IO);
#endif
#ifdef _SC_ACL
    sysconf_names->__setitem__(new str("SC_ACL"), _SC_ACL);
#endif
#ifdef _SC_AIO_LISTIO_MAX
    sysconf_names->__setitem__(new str("SC_AIO_LISTIO_MAX"), _SC_AIO_LISTIO_MAX);
#endif
#ifdef _SC_AIO_MAX
    sysconf_names->__setitem__(new str("SC_AIO_MAX"), _SC_AIO_MAX);
#endif
#ifdef _SC_AIO_PRIO_DELTA_MAX
    sysconf_names->__setitem__(new str("SC_AIO_PRIO_DELTA_MAX"), _SC_AIO_PRIO_DELTA_MAX);
#endif
#ifdef _SC_ARG_MAX
    sysconf_names->__setitem__(new str("SC_ARG_MAX"), _SC_ARG_MAX);
#endif
#ifdef _SC_ASYNCHRONOUS_IO
    sysconf_names->__setitem__(new str("SC_ASYNCHRONOUS_IO"), _SC_ASYNCHRONOUS_IO);
#endif
#ifdef _SC_ATEXIT_MAX
    sysconf_names->__setitem__(new str("SC_ATEXIT_MAX"), _SC_ATEXIT_MAX);
#endif
#ifdef _SC_AUDIT
    sysconf_names->__setitem__(new str("SC_AUDIT"), _SC_AUDIT);
#endif
#ifdef _SC_AVPHYS_PAGES
    sysconf_names->__setitem__(new str("SC_AVPHYS_PAGES"), _SC_AVPHYS_PAGES);
#endif
#ifdef _SC_BC_BASE_MAX
    sysconf_names->__setitem__(new str("SC_BC_BASE_MAX"), _SC_BC_BASE_MAX);
#endif
#ifdef _SC_BC_DIM_MAX
    sysconf_names->__setitem__(new str("SC_BC_DIM_MAX"), _SC_BC_DIM_MAX);
#endif
#ifdef _SC_BC_SCALE_MAX
    sysconf_names->__setitem__(new str("SC_BC_SCALE_MAX"), _SC_BC_SCALE_MAX);
#endif
#ifdef _SC_BC_STRING_MAX
    sysconf_names->__setitem__(new str("SC_BC_STRING_MAX"), _SC_BC_STRING_MAX);
#endif
#ifdef _SC_CAP
    sysconf_names->__setitem__(new str("SC_CAP"), _SC_CAP);
#endif
#ifdef _SC_CHARCLASS_NAME_MAX
    sysconf_names->__setitem__(new str("SC_CHARCLASS_NAME_MAX"), _SC_CHARCLASS_NAME_MAX);
#endif
#ifdef _SC_CHAR_BIT
    sysconf_names->__setitem__(new str("SC_CHAR_BIT"), _SC_CHAR_BIT);
#endif
#ifdef _SC_CHAR_MAX
    sysconf_names->__setitem__(new str("SC_CHAR_MAX"), _SC_CHAR_MAX);
#endif
#ifdef _SC_CHAR_MIN
    sysconf_names->__setitem__(new str("SC_CHAR_MIN"), _SC_CHAR_MIN);
#endif
#ifdef _SC_CHILD_MAX
    sysconf_names->__setitem__(new str("SC_CHILD_MAX"), _SC_CHILD_MAX);
#endif
#ifdef _SC_CLK_TCK
    sysconf_names->__setitem__(new str("SC_CLK_TCK"), _SC_CLK_TCK);
#endif
#ifdef _SC_COHER_BLKSZ
    sysconf_names->__setitem__(new str("SC_COHER_BLKSZ"), _SC_COHER_BLKSZ);
#endif
#ifdef _SC_COLL_WEIGHTS_MAX
    sysconf_names->__setitem__(new str("SC_COLL_WEIGHTS_MAX"), _SC_COLL_WEIGHTS_MAX);
#endif
#ifdef _SC_DCACHE_ASSOC
    sysconf_names->__setitem__(new str("SC_DCACHE_ASSOC"), _SC_DCACHE_ASSOC);
#endif
#ifdef _SC_DCACHE_BLKSZ
    sysconf_names->__setitem__(new str("SC_DCACHE_BLKSZ"), _SC_DCACHE_BLKSZ);
#endif
#ifdef _SC_DCACHE_LINESZ
    sysconf_names->__setitem__(new str("SC_DCACHE_LINESZ"), _SC_DCACHE_LINESZ);
#endif
#ifdef _SC_DCACHE_SZ
    sysconf_names->__setitem__(new str("SC_DCACHE_SZ"), _SC_DCACHE_SZ);
#endif
#ifdef _SC_DCACHE_TBLKSZ
    sysconf_names->__setitem__(new str("SC_DCACHE_TBLKSZ"), _SC_DCACHE_TBLKSZ);
#endif
#ifdef _SC_DELAYTIMER_MAX
    sysconf_names->__setitem__(new str("SC_DELAYTIMER_MAX"), _SC_DELAYTIMER_MAX);
#endif
#ifdef _SC_EQUIV_CLASS_MAX
    sysconf_names->__setitem__(new str("SC_EQUIV_CLASS_MAX"), _SC_EQUIV_CLASS_MAX);
#endif
#ifdef _SC_EXPR_NEST_MAX
    sysconf_names->__setitem__(new str("SC_EXPR_NEST_MAX"), _SC_EXPR_NEST_MAX);
#endif
#ifdef _SC_FSYNC
    sysconf_names->__setitem__(new str("SC_FSYNC"), _SC_FSYNC);
#endif
#ifdef _SC_GETGR_R_SIZE_MAX
    sysconf_names->__setitem__(new str("SC_GETGR_R_SIZE_MAX"), _SC_GETGR_R_SIZE_MAX);
#endif
#ifdef _SC_GETPW_R_SIZE_MAX
    sysconf_names->__setitem__(new str("SC_GETPW_R_SIZE_MAX"), _SC_GETPW_R_SIZE_MAX);
#endif
#ifdef _SC_ICACHE_ASSOC
    sysconf_names->__setitem__(new str("SC_ICACHE_ASSOC"), _SC_ICACHE_ASSOC);
#endif
#ifdef _SC_ICACHE_BLKSZ
    sysconf_names->__setitem__(new str("SC_ICACHE_BLKSZ"), _SC_ICACHE_BLKSZ);
#endif
#ifdef _SC_ICACHE_LINESZ
    sysconf_names->__setitem__(new str("SC_ICACHE_LINESZ"), _SC_ICACHE_LINESZ);
#endif
#ifdef _SC_ICACHE_SZ
    sysconf_names->__setitem__(new str("SC_ICACHE_SZ"), _SC_ICACHE_SZ);
#endif
#ifdef _SC_INF
    sysconf_names->__setitem__(new str("SC_INF"), _SC_INF);
#endif
#ifdef _SC_INT_MAX
    sysconf_names->__setitem__(new str("SC_INT_MAX"), _SC_INT_MAX);
#endif
#ifdef _SC_INT_MIN
    sysconf_names->__setitem__(new str("SC_INT_MIN"), _SC_INT_MIN);
#endif
#ifdef _SC_IOV_MAX
    sysconf_names->__setitem__(new str("SC_IOV_MAX"), _SC_IOV_MAX);
#endif
#ifdef _SC_IP_SECOPTS
    sysconf_names->__setitem__(new str("SC_IP_SECOPTS"), _SC_IP_SECOPTS);
#endif
#ifdef _SC_JOB_CONTROL
    sysconf_names->__setitem__(new str("SC_JOB_CONTROL"), _SC_JOB_CONTROL);
#endif
#ifdef _SC_KERN_POINTERS
    sysconf_names->__setitem__(new str("SC_KERN_POINTERS"), _SC_KERN_POINTERS);
#endif
#ifdef _SC_KERN_SIM
    sysconf_names->__setitem__(new str("SC_KERN_SIM"), _SC_KERN_SIM);
#endif
#ifdef _SC_LINE_MAX
    sysconf_names->__setitem__(new str("SC_LINE_MAX"), _SC_LINE_MAX);
#endif
#ifdef _SC_LOGIN_NAME_MAX
    sysconf_names->__setitem__(new str("SC_LOGIN_NAME_MAX"), _SC_LOGIN_NAME_MAX);
#endif
#ifdef _SC_LOGNAME_MAX
    sysconf_names->__setitem__(new str("SC_LOGNAME_MAX"), _SC_LOGNAME_MAX);
#endif
#ifdef _SC_LONG_BIT
    sysconf_names->__setitem__(new str("SC_LONG_BIT"), _SC_LONG_BIT);
#endif
#ifdef _SC_MAC
    sysconf_names->__setitem__(new str("SC_MAC"), _SC_MAC);
#endif
#ifdef _SC_MAPPED_FILES
    sysconf_names->__setitem__(new str("SC_MAPPED_FILES"), _SC_MAPPED_FILES);
#endif
#ifdef _SC_MAXPID
    sysconf_names->__setitem__(new str("SC_MAXPID"), _SC_MAXPID);
#endif
#ifdef _SC_MB_LEN_MAX
    sysconf_names->__setitem__(new str("SC_MB_LEN_MAX"), _SC_MB_LEN_MAX);
#endif
#ifdef _SC_MEMLOCK
    sysconf_names->__setitem__(new str("SC_MEMLOCK"), _SC_MEMLOCK);
#endif
#ifdef _SC_MEMLOCK_RANGE
    sysconf_names->__setitem__(new str("SC_MEMLOCK_RANGE"), _SC_MEMLOCK_RANGE);
#endif
#ifdef _SC_MEMORY_PROTECTION
    sysconf_names->__setitem__(new str("SC_MEMORY_PROTECTION"), _SC_MEMORY_PROTECTION);
#endif
#ifdef _SC_MESSAGE_PASSING
    sysconf_names->__setitem__(new str("SC_MESSAGE_PASSING"), _SC_MESSAGE_PASSING);
#endif
#ifdef _SC_MMAP_FIXED_ALIGNMENT
    sysconf_names->__setitem__(new str("SC_MMAP_FIXED_ALIGNMENT"), _SC_MMAP_FIXED_ALIGNMENT);
#endif
#ifdef _SC_MQ_OPEN_MAX
    sysconf_names->__setitem__(new str("SC_MQ_OPEN_MAX"), _SC_MQ_OPEN_MAX);
#endif
#ifdef _SC_MQ_PRIO_MAX
    sysconf_names->__setitem__(new str("SC_MQ_PRIO_MAX"), _SC_MQ_PRIO_MAX);
#endif
#ifdef _SC_NACLS_MAX
    sysconf_names->__setitem__(new str("SC_NACLS_MAX"), _SC_NACLS_MAX);
#endif
#ifdef _SC_NGROUPS_MAX
    sysconf_names->__setitem__(new str("SC_NGROUPS_MAX"), _SC_NGROUPS_MAX);
#endif
#ifdef _SC_NL_ARGMAX
    sysconf_names->__setitem__(new str("SC_NL_ARGMAX"), _SC_NL_ARGMAX);
#endif
#ifdef _SC_NL_LANGMAX
    sysconf_names->__setitem__(new str("SC_NL_LANGMAX"), _SC_NL_LANGMAX);
#endif
#ifdef _SC_NL_MSGMAX
    sysconf_names->__setitem__(new str("SC_NL_MSGMAX"), _SC_NL_MSGMAX);
#endif
#ifdef _SC_NL_NMAX
    sysconf_names->__setitem__(new str("SC_NL_NMAX"), _SC_NL_NMAX);
#endif
#ifdef _SC_NL_SETMAX
    sysconf_names->__setitem__(new str("SC_NL_SETMAX"), _SC_NL_SETMAX);
#endif
#ifdef _SC_NL_TEXTMAX
    sysconf_names->__setitem__(new str("SC_NL_TEXTMAX"), _SC_NL_TEXTMAX);
#endif
#ifdef _SC_NPROCESSORS_CONF
    sysconf_names->__setitem__(new str("SC_NPROCESSORS_CONF"), _SC_NPROCESSORS_CONF);
#endif
#ifdef _SC_NPROCESSORS_ONLN
    sysconf_names->__setitem__(new str("SC_NPROCESSORS_ONLN"), _SC_NPROCESSORS_ONLN);
#endif
#ifdef _SC_NPROC_CONF
    sysconf_names->__setitem__(new str("SC_NPROC_CONF"), _SC_NPROC_CONF);
#endif
#ifdef _SC_NPROC_ONLN
    sysconf_names->__setitem__(new str("SC_NPROC_ONLN"), _SC_NPROC_ONLN);
#endif
#ifdef _SC_NZERO
    sysconf_names->__setitem__(new str("SC_NZERO"), _SC_NZERO);
#endif
#ifdef _SC_OPEN_MAX
    sysconf_names->__setitem__(new str("SC_OPEN_MAX"), _SC_OPEN_MAX);
#endif
#ifdef _SC_PAGESIZE
    sysconf_names->__setitem__(new str("SC_PAGESIZE"), _SC_PAGESIZE);
#endif
#ifdef _SC_PAGE_SIZE
    sysconf_names->__setitem__(new str("SC_PAGE_SIZE"), _SC_PAGE_SIZE);
#endif
#ifdef _SC_PASS_MAX
    sysconf_names->__setitem__(new str("SC_PASS_MAX"), _SC_PASS_MAX);
#endif
#ifdef _SC_PHYS_PAGES
    sysconf_names->__setitem__(new str("SC_PHYS_PAGES"), _SC_PHYS_PAGES);
#endif
#ifdef _SC_PII
    sysconf_names->__setitem__(new str("SC_PII"), _SC_PII);
#endif
#ifdef _SC_PII_INTERNET
    sysconf_names->__setitem__(new str("SC_PII_INTERNET"), _SC_PII_INTERNET);
#endif
#ifdef _SC_PII_INTERNET_DGRAM
    sysconf_names->__setitem__(new str("SC_PII_INTERNET_DGRAM"), _SC_PII_INTERNET_DGRAM);
#endif
#ifdef _SC_PII_INTERNET_STREAM
    sysconf_names->__setitem__(new str("SC_PII_INTERNET_STREAM"), _SC_PII_INTERNET_STREAM);
#endif
#ifdef _SC_PII_OSI
    sysconf_names->__setitem__(new str("SC_PII_OSI"), _SC_PII_OSI);
#endif
#ifdef _SC_PII_OSI_CLTS
    sysconf_names->__setitem__(new str("SC_PII_OSI_CLTS"), _SC_PII_OSI_CLTS);
#endif
#ifdef _SC_PII_OSI_COTS
    sysconf_names->__setitem__(new str("SC_PII_OSI_COTS"), _SC_PII_OSI_COTS);
#endif
#ifdef _SC_PII_OSI_M
    sysconf_names->__setitem__(new str("SC_PII_OSI_M"), _SC_PII_OSI_M);
#endif
#ifdef _SC_PII_SOCKET
    sysconf_names->__setitem__(new str("SC_PII_SOCKET"), _SC_PII_SOCKET);
#endif
#ifdef _SC_PII_XTI
    sysconf_names->__setitem__(new str("SC_PII_XTI"), _SC_PII_XTI);
#endif
#ifdef _SC_POLL
    sysconf_names->__setitem__(new str("SC_POLL"), _SC_POLL);
#endif
#ifdef _SC_PRIORITIZED_IO
    sysconf_names->__setitem__(new str("SC_PRIORITIZED_IO"), _SC_PRIORITIZED_IO);
#endif
#ifdef _SC_PRIORITY_SCHEDULING
    sysconf_names->__setitem__(new str("SC_PRIORITY_SCHEDULING"), _SC_PRIORITY_SCHEDULING);
#endif
#ifdef _SC_REALTIME_SIGNALS
    sysconf_names->__setitem__(new str("SC_REALTIME_SIGNALS"), _SC_REALTIME_SIGNALS);
#endif
#ifdef _SC_RE_DUP_MAX
    sysconf_names->__setitem__(new str("SC_RE_DUP_MAX"), _SC_RE_DUP_MAX);
#endif
#ifdef _SC_RTSIG_MAX
    sysconf_names->__setitem__(new str("SC_RTSIG_MAX"), _SC_RTSIG_MAX);
#endif
#ifdef _SC_SAVED_IDS
    sysconf_names->__setitem__(new str("SC_SAVED_IDS"), _SC_SAVED_IDS);
#endif
#ifdef _SC_SCHAR_MAX
    sysconf_names->__setitem__(new str("SC_SCHAR_MAX"), _SC_SCHAR_MAX);
#endif
#ifdef _SC_SCHAR_MIN
    sysconf_names->__setitem__(new str("SC_SCHAR_MIN"), _SC_SCHAR_MIN);
#endif
#ifdef _SC_SELECT
    sysconf_names->__setitem__(new str("SC_SELECT"), _SC_SELECT);
#endif
#ifdef _SC_SEMAPHORES
    sysconf_names->__setitem__(new str("SC_SEMAPHORES"), _SC_SEMAPHORES);
#endif
#ifdef _SC_SEM_NSEMS_MAX
    sysconf_names->__setitem__(new str("SC_SEM_NSEMS_MAX"), _SC_SEM_NSEMS_MAX);
#endif
#ifdef _SC_SEM_VALUE_MAX
    sysconf_names->__setitem__(new str("SC_SEM_VALUE_MAX"), _SC_SEM_VALUE_MAX);
#endif
#ifdef _SC_SHARED_MEMORY_OBJECTS
    sysconf_names->__setitem__(new str("SC_SHARED_MEMORY_OBJECTS"), _SC_SHARED_MEMORY_OBJECTS);
#endif
#ifdef _SC_SHRT_MAX
    sysconf_names->__setitem__(new str("SC_SHRT_MAX"), _SC_SHRT_MAX);
#endif
#ifdef _SC_SHRT_MIN
    sysconf_names->__setitem__(new str("SC_SHRT_MIN"), _SC_SHRT_MIN);
#endif
#ifdef _SC_SIGQUEUE_MAX
    sysconf_names->__setitem__(new str("SC_SIGQUEUE_MAX"), _SC_SIGQUEUE_MAX);
#endif
#ifdef _SC_SIGRT_MAX
    sysconf_names->__setitem__(new str("SC_SIGRT_MAX"), _SC_SIGRT_MAX);
#endif
#ifdef _SC_SIGRT_MIN
    sysconf_names->__setitem__(new str("SC_SIGRT_MIN"), _SC_SIGRT_MIN);
#endif
#ifdef _SC_SOFTPOWER
    sysconf_names->__setitem__(new str("SC_SOFTPOWER"), _SC_SOFTPOWER);
#endif
#ifdef _SC_SPLIT_CACHE
    sysconf_names->__setitem__(new str("SC_SPLIT_CACHE"), _SC_SPLIT_CACHE);
#endif
#ifdef _SC_SSIZE_MAX
    sysconf_names->__setitem__(new str("SC_SSIZE_MAX"), _SC_SSIZE_MAX);
#endif
#ifdef _SC_STACK_PROT
    sysconf_names->__setitem__(new str("SC_STACK_PROT"), _SC_STACK_PROT);
#endif
#ifdef _SC_STREAM_MAX
    sysconf_names->__setitem__(new str("SC_STREAM_MAX"), _SC_STREAM_MAX);
#endif
#ifdef _SC_SYNCHRONIZED_IO
    sysconf_names->__setitem__(new str("SC_SYNCHRONIZED_IO"), _SC_SYNCHRONIZED_IO);
#endif
#ifdef _SC_THREADS
    sysconf_names->__setitem__(new str("SC_THREADS"), _SC_THREADS);
#endif
#ifdef _SC_THREAD_ATTR_STACKADDR
    sysconf_names->__setitem__(new str("SC_THREAD_ATTR_STACKADDR"), _SC_THREAD_ATTR_STACKADDR);
#endif
#ifdef _SC_THREAD_ATTR_STACKSIZE
    sysconf_names->__setitem__(new str("SC_THREAD_ATTR_STACKSIZE"), _SC_THREAD_ATTR_STACKSIZE);
#endif
#ifdef _SC_THREAD_DESTRUCTOR_ITERATIONS
    sysconf_names->__setitem__(new str("SC_THREAD_DESTRUCTOR_ITERATIONS"), _SC_THREAD_DESTRUCTOR_ITERATIONS);
#endif
#ifdef _SC_THREAD_KEYS_MAX
    sysconf_names->__setitem__(new str("SC_THREAD_KEYS_MAX"), _SC_THREAD_KEYS_MAX);
#endif
#ifdef _SC_THREAD_PRIORITY_SCHEDULING
    sysconf_names->__setitem__(new str("SC_THREAD_PRIORITY_SCHEDULING"), _SC_THREAD_PRIORITY_SCHEDULING);
#endif
#ifdef _SC_THREAD_PRIO_INHERIT
    sysconf_names->__setitem__(new str("SC_THREAD_PRIO_INHERIT"), _SC_THREAD_PRIO_INHERIT);
#endif
#ifdef _SC_THREAD_PRIO_PROTECT
    sysconf_names->__setitem__(new str("SC_THREAD_PRIO_PROTECT"), _SC_THREAD_PRIO_PROTECT);
#endif
#ifdef _SC_THREAD_PROCESS_SHARED
    sysconf_names->__setitem__(new str("SC_THREAD_PROCESS_SHARED"), _SC_THREAD_PROCESS_SHARED);
#endif
#ifdef _SC_THREAD_SAFE_FUNCTIONS
    sysconf_names->__setitem__(new str("SC_THREAD_SAFE_FUNCTIONS"), _SC_THREAD_SAFE_FUNCTIONS);
#endif
#ifdef _SC_THREAD_STACK_MIN
    sysconf_names->__setitem__(new str("SC_THREAD_STACK_MIN"), _SC_THREAD_STACK_MIN);
#endif
#ifdef _SC_THREAD_THREADS_MAX
    sysconf_names->__setitem__(new str("SC_THREAD_THREADS_MAX"), _SC_THREAD_THREADS_MAX);
#endif
#ifdef _SC_TIMERS
    sysconf_names->__setitem__(new str("SC_TIMERS"), _SC_TIMERS);
#endif
#ifdef _SC_TIMER_MAX
    sysconf_names->__setitem__(new str("SC_TIMER_MAX"), _SC_TIMER_MAX);
#endif
#ifdef _SC_TTY_NAME_MAX
    sysconf_names->__setitem__(new str("SC_TTY_NAME_MAX"), _SC_TTY_NAME_MAX);
#endif
#ifdef _SC_TZNAME_MAX
    sysconf_names->__setitem__(new str("SC_TZNAME_MAX"), _SC_TZNAME_MAX);
#endif
#ifdef _SC_T_IOV_MAX
    sysconf_names->__setitem__(new str("SC_T_IOV_MAX"), _SC_T_IOV_MAX);
#endif
#ifdef _SC_UCHAR_MAX
    sysconf_names->__setitem__(new str("SC_UCHAR_MAX"), _SC_UCHAR_MAX);
#endif
#ifdef _SC_UINT_MAX
    sysconf_names->__setitem__(new str("SC_UINT_MAX"), _SC_UINT_MAX);
#endif
#ifdef _SC_UIO_MAXIOV
    sysconf_names->__setitem__(new str("SC_UIO_MAXIOV"), _SC_UIO_MAXIOV);
#endif
#ifdef _SC_ULONG_MAX
    sysconf_names->__setitem__(new str("SC_ULONG_MAX"), _SC_ULONG_MAX);
#endif
#ifdef _SC_USHRT_MAX
    sysconf_names->__setitem__(new str("SC_USHRT_MAX"), _SC_USHRT_MAX);
#endif
#ifdef _SC_VERSION
    sysconf_names->__setitem__(new str("SC_VERSION"), _SC_VERSION);
#endif
#ifdef _SC_WORD_BIT
    sysconf_names->__setitem__(new str("SC_WORD_BIT"), _SC_WORD_BIT);
#endif
#ifdef _SC_XBS5_ILP32_OFF32
    sysconf_names->__setitem__(new str("SC_XBS5_ILP32_OFF32"), _SC_XBS5_ILP32_OFF32);
#endif
#ifdef _SC_XBS5_ILP32_OFFBIG
    sysconf_names->__setitem__(new str("SC_XBS5_ILP32_OFFBIG"), _SC_XBS5_ILP32_OFFBIG);
#endif
#ifdef _SC_XBS5_LP64_OFF64
    sysconf_names->__setitem__(new str("SC_XBS5_LP64_OFF64"), _SC_XBS5_LP64_OFF64);
#endif
#ifdef _SC_XBS5_LPBIG_OFFBIG
    sysconf_names->__setitem__(new str("SC_XBS5_LPBIG_OFFBIG"), _SC_XBS5_LPBIG_OFFBIG);
#endif
#ifdef _SC_XOPEN_CRYPT
    sysconf_names->__setitem__(new str("SC_XOPEN_CRYPT"), _SC_XOPEN_CRYPT);
#endif
#ifdef _SC_XOPEN_ENH_I18N
    sysconf_names->__setitem__(new str("SC_XOPEN_ENH_I18N"), _SC_XOPEN_ENH_I18N);
#endif
#ifdef _SC_XOPEN_LEGACY
    sysconf_names->__setitem__(new str("SC_XOPEN_LEGACY"), _SC_XOPEN_LEGACY);
#endif
#ifdef _SC_XOPEN_REALTIME
    sysconf_names->__setitem__(new str("SC_XOPEN_REALTIME"), _SC_XOPEN_REALTIME);
#endif
#ifdef _SC_XOPEN_REALTIME_THREADS
    sysconf_names->__setitem__(new str("SC_XOPEN_REALTIME_THREADS"), _SC_XOPEN_REALTIME_THREADS);
#endif
#ifdef _SC_XOPEN_SHM
    sysconf_names->__setitem__(new str("SC_XOPEN_SHM"), _SC_XOPEN_SHM);
#endif
#ifdef _SC_XOPEN_UNIX
    sysconf_names->__setitem__(new str("SC_XOPEN_UNIX"), _SC_XOPEN_UNIX);
#endif
#ifdef _SC_XOPEN_VERSION
    sysconf_names->__setitem__(new str("SC_XOPEN_VERSION"), _SC_XOPEN_VERSION);
#endif
#ifdef _SC_XOPEN_XCU_VERSION
    sysconf_names->__setitem__(new str("SC_XOPEN_XCU_VERSION"), _SC_XOPEN_XCU_VERSION);
#endif
#ifdef _SC_XOPEN_XPG2
    sysconf_names->__setitem__(new str("SC_XOPEN_XPG2"), _SC_XOPEN_XPG2);
#endif
#ifdef _SC_XOPEN_XPG3
    sysconf_names->__setitem__(new str("SC_XOPEN_XPG3"), _SC_XOPEN_XPG3);
#endif
#ifdef _SC_XOPEN_XPG4
    sysconf_names->__setitem__(new str("SC_XOPEN_XPG4"), _SC_XOPEN_XPG4);
#endif

}

} // module namespace

