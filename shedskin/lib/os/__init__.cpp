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

#if !defined(__APPLE__) && !defined(__FreeBSD__)
#include <sys/sysmacros.h>
#endif

#include <grp.h>
#include <sysexits.h>
#include <sys/ioctl.h>
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
#include <roken.h>
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
[[noreturn]] static void __throw_winerror(DWORD err, str *fname=0) {
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
    __throw_oserror(fname);
}

/* str (code points) <-> native wide strings, via std::filesystem::path */
static std::wstring __to_wide(str *s) {
    return std::filesystem::path(s->unit).wstring();
}

static str *__from_wide(const wchar_t *w) {
    std::u32string u = std::filesystem::path(w).u32string();
    return new str((const __ss_char *)u.data(), u.size());
}
#endif


str *linesep, *name;
dict<str *, str *> *__ss_environ;
dict<str *, __ss_int> *pathconf_names, *confstr_names, *sysconf_names;

struct stat sbuf;
#ifndef WIN32
struct statvfs vbuf;
#endif

const __ss_int MAXENTRIES = 4096; /* XXX fix functions that use this */

str *altsep, *curdir, *defpath, *devnull, *extsep, *pardir, *pathsep, *sep;

__ss_int __ss_F_OK, __ss_R_OK, __ss_W_OK, __ss_X_OK, __ss_NGROUPS_MAX, __ss_TMP_MAX, __ss_WCONTINUED, __ss_WNOHANG, __ss_WUNTRACED, __ss_O_RDONLY, __ss_O_WRONLY, __ss_O_RDWR, __ss_O_NDELAY, __ss_O_NONBLOCK, __ss_O_APPEND, __ss_O_DSYNC, __ss_O_RSYNC, __ss_O_SYNC, __ss_O_NOCTTY, __ss_O_CREAT, __ss_O_EXCL, __ss_O_TRUNC, __ss_O_BINARY, __ss_O_TEXT, __ss_O_LARGEFILE, __ss_O_SHLOCK, __ss_O_EXLOCK, __ss_O_NOINHERIT, __ss__O_SHORT_LIVED, __ss_O_TEMPORARY, __ss_O_RANDOM, __ss_O_SEQUENTIAL, __ss_O_ASYNC, __ss_O_DIRECT, __ss_O_DIRECTORY, __ss_O_NOFOLLOW, __ss_O_NOATIME, __ss_EX_OK, __ss_EX_USAGE, __ss_EX_DATAERR, __ss_EX_NOINPUT, __ss_EX_NOUSER, __ss_EX_NOHOST, __ss_EX_UNAVAILABLE, __ss_EX_SOFTWARE, __ss_EX_OSERR, __ss_EX_OSFILE, __ss_EX_CANTCREAT, __ss_EX_IOERR, __ss_EX_TEMPFAIL, __ss_EX_PROTOCOL, __ss_EX_NOPERM, __ss_EX_CONFIG, __ss_EX_NOTFOUND, __ss_P_WAIT, __ss_P_NOWAIT, __ss_P_OVERLAY, __ss_P_NOWAITO, __ss_P_DETACH, __ss_SEEK_SET, __ss_SEEK_CUR, __ss_SEEK_END;

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
        for (const auto & entry : std::filesystem::directory_iterator(path->unit))
            r->append(new str(entry.path().filename().string().c_str()));
    } catch (std::filesystem::filesystem_error const& e) {
        __throw_fs_error(e, path);
    }

    return r;
}

str *getcwd() {
    str *r;
    char *d=::getcwd(0, 256);
    r = new str(d);
    free(d);
    return r;
}

bytes *getcwdb() {
    char *d=::getcwd(0, 256);
    if (!d)
        __throw_oserror();
    bytes *r = new bytes(d);
    free(d);
    return r;
}

bytes *fsencode(str *filename) {
    return new bytes(__to_utf8(filename->unit));
}

bytes *fsencode(bytes *filename) {
    return filename;
}

str *fsdecode(bytes *filename) {
    return new str(__from_utf8(filename->unit));
}

str *fsdecode(str *filename) {
    return filename;
}

void *chdir(str *dir) {
    if(::chdir(dir->c_str()) == -1)
        __throw_oserror(dir);
    return NULL;
}

str *strerror(__ss_int i) {
    return new str(::strerror((int)i));
}

__ss_int system(str *c) {
    return std::system(c->c_str());
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
    if(std::rename(a->c_str(), b->c_str()) == -1) {
        __throw_oserror(a);
    }
    return NULL;
}

void *replace(str *a, str *b) {
    /* std::rename() already atomically replaces an existing destination
     * on POSIX, but on Windows it fails with EEXIST in that case instead.
     * std::filesystem::rename() is specified to have POSIX-like overwrite
     * semantics on every platform, so use that here instead to match what
     * os.replace() promises. */
    std::error_code ec;
    std::filesystem::rename(a->c_str(), b->c_str(), ec);
    if (ec) {
        /* the error_code overload doesn't throw and isn't guaranteed to
         * leave errno set, so set it explicitly from ec before constructing
         * the exception, which reads the global errno */
        errno = ec.value();
        __throw_oserror(a);
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

void *remove(str *path) {
    if(std::remove(path->c_str()) == -1) {
        __throw_oserror(path);
    }
    return NULL;
}

void *unlink(str *path) {
    remove(path);
    return NULL;
}

void *rmdir(str *a) {
    if (::rmdir(a->c_str()) == -1)
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
    if (::mkdir(path->c_str()) == -1)
#else
    if (::mkdir(path->c_str(), (unsigned)mode) == -1)
#endif
        __throw_oserror(path);
    return NULL;
}

void _exit(__ss_int code) {
    ::exit((int)code);
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
                throw (e);
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
            throw (e);
        }
    }
    return NULL;
}

void *abort() {
    std::abort();
}

/* class __cstat */

class_ *cl___cstat;

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

static void __stat_win32_info(__cstat *st, HANDLE h) {
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

__cstat::__cstat(str *path, __ss_int t) {
    this->__class__ = cl___cstat;

    int r = -1;
    if(t==1) {
        r = ::stat(path->c_str(), &sbuf);
    } else if (t==2) {
#ifndef WIN32
        r = ::lstat(path->c_str(), &sbuf);
#endif
    }
#ifdef WIN32
    bool device = false;
    if (r == -1) {
        /* The CRT stat() fails on device names such as 'nul' or 'con'.
           Like CPython (since 3.8), fall back to opening the path and
           reporting it as a character device/pipe. */
        HANDLE h = CreateFileA(path->c_str(), 0,
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
        HANDLE h = CreateFileA(path->c_str(), 0,
                               FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                               NULL, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, NULL);
        if (h != INVALID_HANDLE_VALUE) {
            __stat_win32_info(this, h);
            CloseHandle(h);
        }
    }
#endif
}

__cstat::__cstat(__ss_int fd) {
    this->__class__ = cl___cstat;

    int r;
    {
        __suppress_iph guard;
        r = ::fstat((int)fd, &sbuf);
    }
    if(r == -1)
        __throw_oserror();

    fill_er_up();

#ifdef WIN32
    __stat_win32_info(this, (HANDLE)_get_osfhandle((int)fd));
#endif
}

void __cstat::fill_er_up() {
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

__ss_int __cstat::__len__() {
    return 10;
}

__ss_int __cstat::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    switch(i) {
        case 0: return (__ss_int)st_mode;
        case 1: return (__ss_int)st_ino;
        case 2: return (__ss_int)st_dev;
        case 3: return (__ss_int)st_nlink;
        case 4: return (__ss_int)st_uid;
        case 5: return (__ss_int)st_gid;
        case 6: return (__ss_int)st_size;
        case 7: return __atime_s;
        case 8: return __mtime_s;
        case 9: return __ctime_s;

        default:
            throw new IndexError(new str("tuple index out of range"));
    }

    return 0;
}


/* class namedtuple */

str *namedtuple::__repr__() {
    tuple<__ss_int> *t = new tuple<__ss_int>();
    for(__ss_int i=0; i < __len__(); i++)
        t->units.push_back(__getitem__(i));
    return repr(t);
}

tuple<__ss_int> *namedtuple::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    tuple<__ss_int> *c = new tuple<__ss_int>();

    slicenr(x, l, u, s, __len__());

    if(s > 0)
        for(__ss_int i=l; i<u; i += s)
            c->units.push_back(__getitem__(i));
    else
        for(__ss_int i=l; i>u; i += s)
            c->units.push_back(__getitem__(i));

    return c;
}

__cstat *stat(str *path) {
    return new __cstat(path, 1);
}
__cstat *stat(__ss_bool follow_symlinks, str *path) {
    if(follow_symlinks)
        return stat(path);
    return lstat(path);
}
__cstat *lstat(str *path) {
#ifndef WIN32
    return new __cstat(path, 2);
#else
    return new __cstat(path, 1);
#endif
}
__cstat *fstat(__ss_int fd) {
    return new __cstat(fd);
}

/* class DirEntry */

class_ *cl_DirEntry;

DirEntry::DirEntry(const std::filesystem::directory_entry &entry) : __entry(entry) {
    this->__class__ = cl_DirEntry;
    this->name = new str(entry.path().filename().string().c_str());
    this->path = new str(entry.path().string().c_str());
}

__ss_bool DirEntry::is_dir(__ss_bool follow_symlinks) {
    std::error_code ec;
    if(follow_symlinks)
        return __mbool(__entry.is_directory(ec));
    return __mbool(std::filesystem::is_directory(__entry.symlink_status(ec)));
}

__ss_bool DirEntry::is_file(__ss_bool follow_symlinks) {
    std::error_code ec;
    if(follow_symlinks)
        return __mbool(__entry.is_regular_file(ec));
    return __mbool(std::filesystem::is_regular_file(__entry.symlink_status(ec)));
}

__ss_bool DirEntry::is_symlink() {
    std::error_code ec;
    return __mbool(__entry.is_symlink(ec));
}

__ss_bool DirEntry::is_junction() {
    return __path__::isjunction(this->path); /* always False except on Windows */
}

__ss_int DirEntry::inode() {
    return __os__::lstat(this->path)->st_ino;
}

__cstat *DirEntry::stat(__ss_bool follow_symlinks) {
    if(follow_symlinks)
        return __os__::stat(this->path);
    return __os__::lstat(this->path);
}

str *DirEntry::__repr__() {
    std::stringstream ss;
    ss << "<DirEntry " << repr(this->name)->c_str() << ">";
    return new str(ss.str().c_str());
}

list<DirEntry *> *scandir(str *path) {
    if(!path)
        path = new str(".");

    list<DirEntry *> *r = new list<DirEntry *>();

    try {
        for (const auto & entry : std::filesystem::directory_iterator(path->unit))
            r->append(new DirEntry(entry));
    } catch (std::filesystem::filesystem_error const& e) {
        __throw_fs_error(e, path);
    }

    return r;
}

/* os.walk */

static str *__walk_join(str *top, str *name) {
    if(top->unit.empty())
        return name;
    __ss_char last = top->unit.back();
    if(last == '/' || last == '\\')
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
    std::filesystem::directory_iterator it(top->unit, ec);
    if(ec) {
        __onerror(top, ec);
        return NULL;
    }
    try {
        for (const auto & entry : it) {
            std::error_code ec2;
            str *name = new str(entry.path().filename().string().c_str());
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
            if(followlinks || !std::filesystem::is_symlink(path->unit, ec))
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
    if(varname->unit.empty() || varname->find(new str("=")) != -1)
        throw new ValueError(new str("illegal environment variable name"));
#ifdef WIN32
    if(::_putenv_s(varname->c_str(), value->c_str()) != 0)
        __throw_oserror(new str("os.putenv"));
#else
    if(::setenv(varname->c_str(), value->c_str(), 1) == -1)
        __throw_oserror(new str("os.putenv"));
#endif
    return NULL;
}

void *unsetenv(str* var) {
#ifdef WIN32
    /* MSVC has no unsetenv(); passing "NAME=" to _putenv removes NAME
       from the environment. */
    std::stringstream ss;
    ss << var->c_str() << '=';
    _putenv(const_cast<char*>(ss.str().c_str()));
#else
    ::unsetenv(var->c_str());
#endif
    return NULL;
}

__ss_int umask(__ss_int newmask)  {
    return (__ss_int)::umask((unsigned)newmask);
}

__ss_int chmod(str* path, __ss_int val) {
#ifdef WIN32
    /* windows only honours the write permission bit (read-only attribute) */
    if(::_chmod(path->c_str(), (int)val) == -1)
#else
    if(::chmod(path->c_str(), (unsigned)val) == -1)
#endif
        throw new OSError(path);
    return 0;
}

void *fchmod(__ss_int fd, __ss_int mode) {
#ifdef WIN32
    /* like cpython (3.13+): only the write permission bit, as the read-only
       attribute of the open file */
    HANDLE h;
    {
        __suppress_iph guard;
        h = (HANDLE)::_get_osfhandle((int)fd);
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
    if (::fchmod((int)fd, (mode_t)mode) == -1)
        __throw_oserror();
#endif
    return NULL;
}

void *renames(str* old, str* _new) {
    tuple<str *> *__0, *__1, *__5;
    str *__2, *head, *tail;

    __0 = __path__::split(_new);
    head = __0->__getfirst__();
    tail = __0->__getsecond__();

    if ((!___bool(tail))) {
        __1 = __path__::split(head);
        head = __1->__getfirst__();
        tail = __1->__getsecond__();
    }

    while(___bool(__AND(head, tail, 2)) && !__path__::exists(head)) {
        try {
            makedirs(head);
        } catch (OSError *) {
            break;
        }
        __5 = __path__::split(head);
        head = __5->__getfirst__();
        tail = __5->__getsecond__();
    }
    rename(old, _new);

    __0 = __path__::split(old);
    head = __0->__getfirst__();
    tail = __0->__getsecond__();

    if ((!___bool(tail))) {
        __1 = __path__::split(head);
        head = __1->__getfirst__();
        tail = __1->__getsecond__();
    }

    if(___bool(__AND(head,tail,2))) {
        removedirs(head);
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
    f = __ss_popen(cmd->c_str(), flags->c_str());
    if(f == 0)
        __throw_oserror(cmd);
    name = cmd;
    mode = flags;
}

void *popen_pipe::close() {
    __ss_pclose(f);
    closed = True;
    return NULL;
}

popen_pipe* popen(str* cmd) {
    return popen(cmd, new str("r"), -1);
}

popen_pipe* popen(str* cmd, str* mode) {
    return popen(cmd, mode, -1);
}

popen_pipe* popen(str* cmd, str* mode, __ss_int) {
    if(!mode)
        mode = new str("r");
    FILE* fp = __ss_popen(cmd->c_str(), mode->c_str());

    if(!fp) __throw_oserror(cmd);
    return new popen_pipe(fp);
}

__ss_int dup(__ss_int f1) {
    __ss_int f2;
    {
        __suppress_iph guard;
        f2 = ::dup((int)f1);
    }
    if (f2 == -1)
        __throw_oserror(new str("os.dup failed"));
    return f2;
}

__ss_int dup2(__ss_int f1, __ss_int f2, __ss_bool inheritable) {
    int r;
    {
        __suppress_iph guard;
        r = ::dup2((int)f1,(int)f2);
    }
    if (r == -1)
        __throw_oserror(new str("os.dup2 failed"));
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
    if (::fdatasync((int)f1) == -1)
        __throw_oserror(new str("os.fdatasync failed"));
    return NULL;
}
#endif

__ss_int open(str *name_, __ss_int flags, __ss_int mode) {
    __ss_int fp = ::open(name_->c_str(), (int)flags, (int)mode);
    if(fp == -1)
        __throw_oserror(name_);
    return fp;
}

file* fdopen(__ss_int fd, str* mode, __ss_int) {
    if(!mode)
        mode = new str("r");
/* XXX ValueError: mode string must begin with one of 'r', 'w', 'a' or 'U' */
    FILE* fp = ::fdopen((int)fd, mode->c_str());
    if(fp == NULL)
        __throw_oserror(new str("os.fdopen failed"));

    file* ret = new file(fp);
    ret->name = new str("<fdopen>");
    return ret;
}

bytes *read(__ss_int fd, __ss_int n) {
    /* like CPython: a single read(2), so we return whatever is available
       (e.g. on a pipe) instead of blocking until n bytes have arrived */
    if(n < 0) {
        errno = EINVAL;
        __throw_oserror(new str("os.read"));
    }
    if(n > INT_MAX)
        n = INT_MAX;
    bytes *s = new bytes();
    s->unit.resize((size_t)n);
    decltype(::read(0, 0, 0)) nr;
    {
        __suppress_iph guard;
        nr = ::read((int)fd, &s->unit[0], (unsigned int)n);
    }
    if(nr < 0)
        __throw_oserror(new str("os.read"));
    s->unit.resize((size_t)nr);
    return s;
}

__ss_int write(__ss_int fd, bytes *s) {
    size_t r;
    {
        __suppress_iph guard;
        r = (size_t)::write((int)fd, s->c_str(), s->unit.size());
    }
    if(r == std::string::npos)
        __throw_oserror(new str("os.write"));
    return (__ss_int)r;
}


/* like cpython: a single read(2) into a writable buffer (a bytearray) */
__ss_int readinto(__ss_int fd, bytes *buffer) {
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
        nr = ::read((int)fd, &buffer->unit[0], (unsigned int)n);
    }
    if(nr < 0)
        __throw_oserror(new str("os.readinto"));
    return (__ss_int)nr;
}

void *close(__ss_int fd) {
   int r;
   {
       __suppress_iph guard;
       r = ::close((int)fd);
   }
   if(r < 0)
       __throw_oserror(new str("os.close failed"));
   return NULL;
}

/* utime */

/* split float seconds into seconds and nanoseconds like CPython does for
   os.utime() (_PyTime_DoubleToDenominator with ROUND_FLOOR) */
static void __utime_split(double t, long long &sec, long &nsec) {
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
    hFile = CreateFileW(__to_wide(path).c_str(), FILE_WRITE_ATTRIBUTES, 0, NULL, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, NULL);
    if (hFile == INVALID_HANDLE_VALUE)
       __throw_winerror(GetLastError(), path);
    if (!SetFileTime(hFile, NULL, atime, mtime)) {
       DWORD err = GetLastError();
       CloseHandle(hFile);
       __throw_winerror(err, path);
    }
    CloseHandle(hFile);
}

void *__utime_now(str *path) {
    FILETIME now;
    GetSystemTimeAsFileTime(&now);
    __utime_win32(path, &now, &now);
    return NULL;
}

static void __utime_set(str *path, long long asec, long ansec, long long msec, long mnsec) {
    FILETIME atime, mtime;
    time_t_to_FILE_TIME(asec, ansec, &atime);
    time_t_to_FILE_TIME(msec, mnsec, &mtime);
    __utime_win32(path, &atime, &mtime);
}

#else
static void __utime_set(str *path, long long asec, long ansec, long long msec, long mnsec) {
    struct timespec ts[2];
    ts[0].tv_sec = (time_t)asec;
    ts[0].tv_nsec = ansec;
    ts[1].tv_sec = (time_t)msec;
    ts[1].tv_nsec = mnsec;
    if(::utimensat(AT_FDCWD, path->c_str(), ts, 0) == -1)
        __throw_oserror(path);
}

void *__utime_now(str *path) {
    if(::utimensat(AT_FDCWD, path->c_str(), NULL, 0) == -1)
        __throw_oserror(path);
    return NULL;
}
#endif

void *__utime_float(str *path, __ss_float atime, __ss_float mtime) {
    long long asec, msec;
    long ansec, mnsec;
    __utime_split((double)atime, asec, ansec);
    __utime_split((double)mtime, msec, mnsec);
    __utime_set(path, asec, ansec, msec, mnsec);
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

void *__utime_ns(str *path, __ss_int atime_ns, __ss_int mtime_ns) {
    long long asec, msec;
    long ansec, mnsec;
    __utime_split_ns(atime_ns, asec, ansec);
    __utime_split_ns(mtime_ns, msec, mnsec);
    __utime_set(path, asec, ansec, msec, mnsec);
    return NULL;
}

void __utime_error(const char *msg) {
    if (strstr(msg, "not both"))
        throw new ValueError(new str(msg));
    throw new TypeError(new str(msg));
}

void *utime(void *, str *path, void *) {
    return __utime_now(path);
}

bytes *urandom(__ss_int n) {
#ifdef WIN32
    /* like cpython: BCryptGenRandom with the system-preferred rng; looked up
       at run-time, so no extra link library is needed */
    typedef LONG (WINAPI *genrandom_t)(void *, PUCHAR, ULONG, ULONG);
    static genrandom_t genrandom = NULL;
    if(n < 0)
        throw new ValueError(new str("negative argument not allowed"));
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
    __ss_int fd = open(new str("/dev/urandom"), __ss_O_RDONLY);
    bytes *s = read(fd, n);
    close(fd);
    return s;
#endif
}

/* os.getrandom() is a thin, Linux-specific wrapper around the getrandom(2)
 * syscall in CPython, with flags (GRND_NONBLOCK, GRND_RANDOM) that have no
 * portable meaning. Rather than special-case a raw syscall() on Linux only,
 * we implement it on top of the same cross-platform source urandom() already
 * uses (/dev/urandom on POSIX, BCryptGenRandom on Windows), so
 * behavior is consistent across platforms; flags is accepted but ignored. */
bytes *getrandom(__ss_int size, __ss_int flags) {
    return urandom(size);
}

#ifdef WIN32
__ss_bool isatty(__ss_int fd) {
    __suppress_iph guard;
    return __mbool(::_isatty((int)fd));
}
#endif

/* UNIX-only functionality */

#ifndef WIN32
__ss_int __ss_WCOREDUMP(__ss_int status) {
    return WCOREDUMP(status);
}

__ss_int __ss_WEXITSTATUS(__ss_int status) {
    return WEXITSTATUS(status);
}

__ss_int __ss_WIFCONTINUED(__ss_int status) {
    return WIFCONTINUED(status);
}

__ss_int __ss_WIFEXITED(__ss_int status) {
    return WIFEXITED(status);
}

__ss_int __ss_WIFSIGNALED(__ss_int status) {
    return WIFSIGNALED(status);
}

__ss_int __ss_WIFSTOPPED(__ss_int status) {
    return WIFSTOPPED(status);
}

__ss_int __ss_WSTOPSIG(__ss_int status) {
    return WSTOPSIG(status);
}

__ss_int __ss_WTERMSIG(__ss_int status) {
    return WTERMSIG(status);
}

void *fchdir(__ss_int f1) {
    if (::fchdir((int)f1) == -1)
        __throw_oserror(new str("os.fchdir failed"));
    return NULL;
}

str *readlink(str *path) {
    size_t size = 255;
    str *r;

    while (1)
      {
        char *buffer = (char *) GC_malloc (size);
        size_t nchars = (size_t)::readlink(path->c_str(), buffer, size);
        if (nchars == std::string::npos) {
            __throw_oserror(path);
        }
        if (nchars < size) {
            buffer[nchars] = '\0';
            r = new str(buffer);
            return r;
        }
        size *= 2;
      }
}

__ss_int getuid() { return (__ss_int)::getuid(); }
void *setuid(__ss_int uid) {
    if(::setuid((unsigned)uid) == -1)
        __throw_oserror(new str("os.setuid"));
    return NULL;
}

__ss_int getgid() { return (__ss_int)::getgid(); }
void *setgid(__ss_int gid) {
    if(::setgid((unsigned)gid) == -1)
        __throw_oserror(new str("os.setgid"));
    return NULL;
}

__ss_int geteuid() { return (__ss_int)::geteuid(); }
void *seteuid(__ss_int euid) {
    if(::seteuid((unsigned)euid) == -1)
        __throw_oserror(new str("os.seteuid"));
    return NULL;
}

__ss_int getegid() { return (__ss_int)::getegid(); }
void *setegid(__ss_int egid) {
    if(::setegid((unsigned)egid) == -1)
        __throw_oserror(new str("os.setegid"));
    return NULL;
}

void *setreuid(__ss_int ruid, __ss_int euid) {
    if(::setreuid((unsigned)ruid, (unsigned)euid) == -1)
        __throw_oserror(new str("os.setreuid"));
    return NULL;
}

void *setregid(__ss_int rgid, __ss_int egid) {
    if(::setregid((unsigned)rgid, (unsigned)egid) == -1)
        __throw_oserror(new str("os.setregid"));
    return NULL;
}

__ss_int tcgetpgrp(__ss_int fd) {
    __ss_int nr;
    nr = ::tcgetpgrp((int)fd);
    if(nr == -1)
        __throw_oserror(new str("os.tcgetpgrp"));
    return nr;
}

void *tcsetpgrp(__ss_int fd, __ss_int pg) {
    if(::tcsetpgrp((int)fd, (pid_t)pg) == -1)
        __throw_oserror(new str("os.tcsetpgrp"));
    return NULL;
}

__ss_int fork() {
    __ss_int ret;
    if ((ret = ::fork()) == -1)
        __throw_oserror(new str("os.fork"));
    return ret;
}

#if !defined(__sun)
tuple<__ss_int> *forkpty() {
    __ss_int ret;
    int amaster;
    if ((ret = ::forkpty(&amaster, NULL, NULL, NULL)) == -1)
        __throw_oserror(new str("os.forkpty"));
    return new tuple<__ss_int>(2, ret, (__ss_int)amaster);
}
tuple<__ss_int> *openpty() {
    int amaster, aslave;
    if (::openpty(&amaster, &aslave, NULL, NULL, NULL) == -1)
        __throw_oserror(new str("os.openpty"));
    return new tuple<__ss_int>(2, (__ss_int)amaster, (__ss_int)aslave);
}
#endif

tuple<__ss_int> *wait() {
    int pid, status;
    if((pid = ::wait(&status)) == -1)
        __throw_oserror(new str("os.wait"));
    return new tuple<__ss_int>(2, (__ss_int)pid, (__ss_int)status);
}

tuple<__ss_int> *waitpid(__ss_int pid, __ss_int options) {
    int status;
    if((pid = ::waitpid((pid_t)pid, &status, (int)options)) == -1)
        __throw_oserror(new str("os.waitpid"));
    return new tuple<__ss_int>(2, pid, (__ss_int)status);
}

__ss_int nice(__ss_int n) {
    __ss_int m;
    if((m = ::nice((int)n)) == -1)
        __throw_oserror(new str("os.nice"));
    return m;
}

void *kill(__ss_int pid, __ss_int sig) {
    if(::kill((pid_t)pid, (int)sig) == -1)
        __throw_oserror(new str("os.kill"));
    return NULL;
}
void *killpg(__ss_int pgid, __ss_int sig) {
    if(::killpg((pid_t)pgid, (int)sig) == -1)
        __throw_oserror(new str("os.killpg"));
    return NULL;
}

str *getlogin() {
    char *name_ = ::getlogin();
    if(!name_)
        __throw_oserror(new str("os.getlogin"));
    return new str(name_);
}

void *chown(str *path, __ss_int uid, __ss_int gid) {
    if (::chown(path->c_str(), (unsigned)uid, (unsigned)gid) == -1)
        __throw_oserror(path);
    return NULL;
}

void *lchown(str *path, __ss_int uid, __ss_int gid) {
    if (::lchown(path->c_str(), (unsigned)uid, (unsigned)gid) == -1)
        __throw_oserror(path);
    return NULL;
}

void *chroot(str *path) {
    if (::chroot(path->c_str()) == -1)
        __throw_oserror(path);
    return NULL;
}

str *ctermid() {
    char term[L_ctermid];
    char *ptr = ::ctermid(term);
    return new str(ptr);
}

__ss_bool isatty(__ss_int fd) {
    return __mbool(::isatty((int)fd));
}

str *ttyname(__ss_int fd) {
    char *name_ = ::ttyname((int)fd);
    if(!name_)
        __throw_oserror(new str("os.ttyname"));
    return new str(name_);
}

class_ *cl_uname_result;

uname_result::uname_result(str *sysname, str *nodename, str *release, str *version, str *machine) {
    this->__class__ = cl_uname_result;
    this->sysname = sysname;
    this->nodename = nodename;
    this->release = release;
    this->version = version;
    this->machine = machine;
}

uname_result::uname_result(tuple<str *> *t) {
    this->__class__ = cl_uname_result;
    if (len(t) != 5)
        throw new TypeError(__add_strs(3, new str("os.uname_result() takes a 5-sequence ("), __str(len(t)), new str("-sequence given)")));
    sysname = t->__getitem__(0);
    nodename = t->__getitem__(1);
    release = t->__getitem__(2);
    version = t->__getitem__(3);
    machine = t->__getitem__(4);
}

tuple<str *> *uname_result::__tuple() {
    return new tuple<str *>(5, sysname, nodename, release, version, machine);
}

__ss_int uname_result::__len__() {
    return 5;
}

str *uname_result::__getitem__(__ss_int i) {
    if (i < 0)
        i += 5;
    switch(i) {
        case 0: return sysname;
        case 1: return nodename;
        case 2: return release;
        case 3: return version;
        case 4: return machine;
        default:
            throw new IndexError(new str("tuple index out of range"));
    }
}

tuple<str *> *uname_result::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    return __tuple()->__slice__(x, l, u, s);
}

__ss_bool uname_result::__contains__(str *x) {
    return __tuple()->__contains__(x);
}

__ss_int uname_result::count(str *x) {
    return __tuple()->count(x);
}

__ss_int uname_result::index(str *x, __ss_int start, __ss_void_struct) {
    return __tuple()->index(x, start);
}

__ss_int uname_result::index(str *x, __ss_int start, __ss_int stop) {
    return __tuple()->index(x, start, stop);
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
        __throw_oserror(new str("os.getgroups"));
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
        l[i] = (gid_t)groups->__getitem__(i);
    if(::setgroups((size_t)len(groups), l) == -1)
        __throw_oserror(new str("os.setgroups"));
    return NULL;
}

__ss_int getsid(__ss_int pid) {
    __ss_int nr = ::getsid((pid_t)pid);
    if(nr == -1)
        __throw_oserror(new str("os.getsid"));
    return nr;
}
__ss_int setsid() {
    __ss_int nr = ::setsid();
    if(nr == -1)
        __throw_oserror(new str("os.setsid"));
    return nr;
}

__ss_int getpgid(__ss_int pid) {
    __ss_int nr = ::getpgid((pid_t)pid);
    if(nr == -1)
        __throw_oserror(new str("os.getpgid"));
    return nr;
}
void *setpgid(__ss_int pid, __ss_int pgrp) {
    if(::setpgid((pid_t)pid, (pid_t)pgrp) == -1)
        __throw_oserror(new str("os.setpgid"));
    return NULL;
}

__ss_int getpgrp() {
    return getpgid(0);
}
void *setpgrp() {
    if(::setpgid(0, 0) == -1)
        __throw_oserror(new str("os.setpgrp"));
    return NULL;
}

void *link(str *src, str *dst) {
    if(::link(src->c_str(), dst->c_str()) == -1)
        __throw_oserror(new str("os.link"));
    return NULL;
}


__ss_int pathconf(str *path, str *name_) {
    if(!pathconf_names->__contains__(name_))
        throw new ValueError(new str("unrecognized configuration name"));
    return pathconf(path, pathconf_names->__getitem__(name_)); /* XXX errors */
}
__ss_int pathconf(str *path, __ss_int name_) {
    return (__ss_int)::pathconf(path->c_str(), (int)name_); /* XXX errors */
}

__ss_int fpathconf(__ss_int fd, str *name_) {
    if(!pathconf_names->__contains__(name_))
        throw new ValueError(new str("unrecognized configuration name"));
    return fpathconf(fd, pathconf_names->__getitem__(name_)); /* XXX errors */
}
__ss_int fpathconf(__ss_int fd, __ss_int name_) {
    return (__ss_int)::fpathconf((int)fd, (int)name_); /* XXX errors */
}

str *confstr(str *name_) {
    if(!confstr_names->__contains__(name_))
        throw new ValueError(new str("unrecognized configuration name"));
    return confstr(confstr_names->__getitem__(name_));
}
str *confstr(__ss_int name_) {
    char buf[MAXENTRIES];
    size_t size = ::confstr((int)name_, buf, MAXENTRIES); /* XXX errors */
    if(size == std::string::npos)
        __throw_oserror(new str("os.confstr"));
    return new str(buf);
}

__ss_int sysconf(str *name_) {
    if(!sysconf_names->__contains__(name_))
        throw new ValueError(new str("unrecognized configuration name"));
    return sysconf(sysconf_names->__getitem__(name_)); /* XXX errors */
}
__ss_int sysconf(__ss_int name_) {
    return (__ss_int)::sysconf((int)name_); /* XXX errors */
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
    if(::mkfifo(path->c_str(), (unsigned)mode) == -1)
        __throw_oserror(new str("os.mkfifo"));
    return NULL;
}

/* class __vfsstat */

class_ *cl___vfsstat;

__vfsstat::__vfsstat(str *path) {
    this->__class__ = cl___vfsstat;
    if(statvfs(path->c_str(), &vbuf) == -1)
        __throw_oserror(path);
    fill_er_up();
}

__vfsstat::__vfsstat(__ss_int fd) {
    this->__class__ = cl___vfsstat;
    if(fstatvfs((int)fd, &vbuf) == -1)
        __throw_oserror(__str(fd));
    fill_er_up();
}

void __vfsstat::fill_er_up() {
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
}

__ss_int __vfsstat::__len__() {
    return 10;
}

__ss_int __vfsstat::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    switch(i) {
        case 0: return (__ss_int)vbuf.f_bsize;
        case 1: return (__ss_int)vbuf.f_frsize;
        case 2: return (__ss_int)vbuf.f_blocks;
        case 3: return (__ss_int)vbuf.f_bfree;
        case 4: return (__ss_int)vbuf.f_bavail;
        case 5: return (__ss_int)vbuf.f_files;
        case 6: return (__ss_int)vbuf.f_ffree;
        case 7: return (__ss_int)vbuf.f_favail;
        case 8: return (__ss_int)vbuf.f_flag;
        case 9: return (__ss_int)vbuf.f_namemax;

        default:
            throw new IndexError(new str("tuple index out of range"));
    }

    return 0;
}

__vfsstat *statvfs(str *path) {
    return new __vfsstat(path);
}
__vfsstat *fstatvfs(__ss_int fd) {
    return new __vfsstat(fd);
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
        res = ::_cwait(&status, (intptr_t)pid, (int)options);
    }
    if (res == -1)
        __throw_oserror(new str("os.waitpid"));
    return new tuple<__ss_int>(2, (__ss_int)res, (__ss_int)(((unsigned long long)(unsigned int)status) << 8));
}

void *link(str *src, str *dst) {
    if (!CreateHardLinkW(__to_wide(dst).c_str(), __to_wide(src).c_str(), NULL))
        __throw_winerror(GetLastError(), src);
    return NULL;
}

str *readlink(str *path) {
    std::error_code ec;
    std::filesystem::path target = std::filesystem::read_symlink(std::filesystem::path(path->unit), ec);
    if (ec) {
        std::error_condition c = ec.default_error_condition();
        errno = (c.category() == std::generic_category()) ? c.value() : EINVAL;
        __throw_oserror(path);
    }
    std::u32string u = target.u32string();
    return new str((const __ss_char *)u.data(), u.size());
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
        for (auto const& [k, v] : env->gcd)
            strings.push_back(__to_wide(__add_strs(3, k, new str("="), v)));
        finish();
    }
    void finish() {
        for (size_t i = 0; i < strings.size(); i++)
            pointers.push_back(strings[i].c_str());
        pointers.push_back(NULL);
    }
    const wchar_t *const *data() { return pointers.data(); }
};

static void __check_exec_args(list<str *> *args, const char *func) {
    if (args->units.empty())
        throw new ValueError(new str((std::string(func) + " arg 2 must not be empty").c_str()));
    if (args->units[0]->unit.empty())
        throw new ValueError(new str((std::string(func) + " arg 2 first element cannot be empty").c_str()));
}

void *execv(str *file, list<str *> *args) {
    __check_exec_args(args, "execv()");
    __wide_vector argv(args);
    {
        __suppress_iph guard;
        ::_wexecv(__to_wide(file).c_str(), argv.data());
    }
    __throw_oserror(new str("os.execv"));
}

void *execvp(str *file, list<str *> *args) {
    __check_exec_args(args, "execvp()");
    __wide_vector argv(args);
    {
        __suppress_iph guard;
        ::_wexecvp(__to_wide(file).c_str(), argv.data());
    }
    __throw_oserror(new str("os.execvp"));
}

void *execve(str *file, list<str *> *args, dict<str *, str *> *env) {
    __check_exec_args(args, "execve()");
    __wide_vector argv(args), envp(env);
    {
        __suppress_iph guard;
        ::_wexecve(__to_wide(file).c_str(), argv.data(), envp.data());
    }
    __throw_oserror(new str("os.execve"));
}

void *execvpe(str *file, list<str *> *args, dict<str *, str *> *env) {
    __check_exec_args(args, "execvpe()");
    __wide_vector argv(args), envp(env);
    {
        __suppress_iph guard;
        ::_wexecvpe(__to_wide(file).c_str(), argv.data(), envp.data());
    }
    __throw_oserror(new str("os.execvpe"));
}

/* like cpython: P_WAIT returns the exit code, P_NOWAIT a process handle */
static __ss_int __spawn_result(intptr_t r, const char *func) {
    if (r == -1)
        __throw_oserror(new str(func));
    return (__ss_int)r;
}

__ss_int spawnv(__ss_int mode, str *file, list<str *> *args) {
    __check_exec_args(args, "spawnv()");
    __wide_vector argv(args);
    __suppress_iph guard;
    return __spawn_result(::_wspawnv((int)mode, __to_wide(file).c_str(), argv.data()), "os.spawnv");
}

__ss_int spawnvp(__ss_int mode, str *file, list<str *> *args) {
    __check_exec_args(args, "spawnvp()");
    __wide_vector argv(args);
    __suppress_iph guard;
    return __spawn_result(::_wspawnvp((int)mode, __to_wide(file).c_str(), argv.data()), "os.spawnvp");
}

__ss_int spawnve(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env) {
    __check_exec_args(args, "spawnve()");
    __wide_vector argv(args), envp(env);
    __suppress_iph guard;
    return __spawn_result(::_wspawnve((int)mode, __to_wide(file).c_str(), argv.data(), envp.data()), "os.spawnve");
}

__ss_int spawnvpe(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env) {
    __check_exec_args(args, "spawnvpe()");
    __wide_vector argv(args), envp(env);
    __suppress_iph guard;
    return __spawn_result(::_wspawnvpe((int)mode, __to_wide(file).c_str(), argv.data(), envp.data()), "os.spawnvpe");
}

#endif /* WIN32 */

/* getpid/getppid/access/fsync/ftruncate/times are declared unconditionally
   in __init__.hpp: posix versions first, then the win32 equivalents. */
#ifndef WIN32

__ss_int getpid() { return (__ss_int)::getpid(); }
__ss_int getppid() { return (__ss_int)::getppid(); }

__ss_bool access(str *path, __ss_int mode) {
    return __mbool(::access(path->c_str(), (int)mode) == 0);
}

void *fsync(__ss_int fd) {
    if(::fsync((int)fd) == -1)
        __throw_oserror(new str("os.fsync"));
    return NULL;
}

void *ftruncate(__ss_int fd, __ss_int n) {
    if (::ftruncate((int)fd, n) == -1)
        __throw_oserror(new str("os.ftruncate"));
    return NULL;
}

times_result *times() {
    struct tms buf;
    clock_t c;
    double ticks_per_second = (double)::sysconf(_SC_CLK_TCK);
    if((c = ::times(&buf)) == -1)
        __throw_oserror(new str("os.times"));
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
    int m = (int)mode & (__ss_R_OK | __ss_W_OK);
    return __mbool(::_access(path->c_str(), m) == 0);
}

void *fsync(__ss_int fd) {
    int r;
    {
        __suppress_iph guard;
        r = ::_commit((int)fd);
    }
    if(r == -1)
        __throw_oserror(new str("os.fsync"));
    return NULL;
}

void *ftruncate(__ss_int fd, __ss_int n) {
    errno_t r;
    {
        __suppress_iph guard;
        r = ::_chsize_s((int)fd, (__int64)n);
    }
    if (r != 0)
        __throw_oserror(new str("os.ftruncate"));
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

terminal_size::terminal_size(__ss_int columns, __ss_int lines) {
    this->__class__ = cl_terminal_size;
    this->columns = columns;
    this->lines = lines;
}

terminal_size::terminal_size(tuple<__ss_int> *t) {
    this->__class__ = cl_terminal_size;
    if (len(t) != 2)
        throw new TypeError(__add_strs(3, new str("os.terminal_size() takes a 2-sequence ("), __str(len(t)), new str("-sequence given)")));
    this->columns = t->__getitem__(0);
    this->lines = t->__getitem__(1);
}

__ss_int terminal_size::__len__() {
    return 2;
}

__ss_int terminal_size::__getitem__(__ss_int i) {
    if (i < 0)
        i += 2;
    switch(i) {
        case 0: return columns;
        case 1: return lines;
        default:
            throw new IndexError(new str("tuple index out of range"));
    }
}

str *terminal_size::__repr__() {
    return __add_strs(5, new str("os.terminal_size(columns="), __str(columns), new str(", lines="), __str(lines), new str(")"));
}

class_ *cl_times_result;

times_result::times_result(__ss_float user, __ss_float system, __ss_float children_user, __ss_float children_system, __ss_float elapsed) {
    this->__class__ = cl_times_result;
    this->user = user;
    this->system = system;
    this->children_user = children_user;
    this->children_system = children_system;
    this->elapsed = elapsed;
}

times_result::times_result(tuple<__ss_float> *t) {
    this->__class__ = cl_times_result;
    if (len(t) != 5)
        throw new TypeError(__add_strs(3, new str("os.times_result() takes a 5-sequence ("), __str(len(t)), new str("-sequence given)")));
    user = t->__getitem__(0);
    system = t->__getitem__(1);
    children_user = t->__getitem__(2);
    children_system = t->__getitem__(3);
    elapsed = t->__getitem__(4);
}

times_result::times_result(tuple<__ss_int> *t) {
    this->__class__ = cl_times_result;
    if (len(t) != 5)
        throw new TypeError(__add_strs(3, new str("os.times_result() takes a 5-sequence ("), __str(len(t)), new str("-sequence given)")));
    user = (__ss_float)t->__getitem__(0);
    system = (__ss_float)t->__getitem__(1);
    children_user = (__ss_float)t->__getitem__(2);
    children_system = (__ss_float)t->__getitem__(3);
    elapsed = (__ss_float)t->__getitem__(4);
}

tuple<__ss_float> *times_result::__tuple() {
    return new tuple<__ss_float>(5, user, system, children_user, children_system, elapsed);
}

__ss_int times_result::__len__() {
    return 5;
}

__ss_float times_result::__getitem__(__ss_int i) {
    if (i < 0)
        i += 5;
    switch(i) {
        case 0: return user;
        case 1: return system;
        case 2: return children_user;
        case 3: return children_system;
        case 4: return elapsed;
        default:
            throw new IndexError(new str("tuple index out of range"));
    }
}

tuple<__ss_float> *times_result::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    return __tuple()->__slice__(x, l, u, s);
}

__ss_bool times_result::__contains__(__ss_float x) {
    return __tuple()->__contains__(x);
}

__ss_int times_result::count(__ss_float x) {
    return __tuple()->count(x);
}

__ss_int times_result::index(__ss_float x, __ss_int start, __ss_void_struct) {
    return __tuple()->index(x, start);
}

__ss_int times_result::index(__ss_float x, __ss_int start, __ss_int stop) {
    return __tuple()->index(x, start, stop);
}

str *times_result::__repr__() {
    return __add_strs(12, name, new str(".times_result(user="), repr(user), new str(", system="), repr(system), new str(", children_user="), repr(children_user), new str(", children_system="), repr(children_system), new str(", elapsed="), repr(elapsed), new str(")"));
}

#ifndef WIN32

void *truncate(str *path, __ss_int length) {
    if (::truncate(path->c_str(), (off_t)length) == -1)
        __throw_oserror(path);
    return NULL;
}

void *closerange(__ss_int fd_low, __ss_int fd_high) {
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
    if (status < INT_MIN || status > INT_MAX)
        throw new OverflowError(new str("signed integer is greater than maximum"));
    int st = (int)status;
    if (WIFEXITED(st))
        return (__ss_int)WEXITSTATUS(st);
    if (WIFSIGNALED(st))
        return -(__ss_int)WTERMSIG(st);
    if (WIFSTOPPED(st))
        throw new ValueError(__add_strs(2, new str("process stopped by delivery of signal "), __str((__ss_int)WSTOPSIG(st))));
    throw new ValueError(__add_strs(2, new str("invalid wait status: "), __str(status)));
}

__ss_bool get_inheritable(__ss_int fd) {
    int flags = ::fcntl((int)fd, F_GETFD);
    if (flags == -1)
        __throw_oserror();
    return __mbool(!(flags & FD_CLOEXEC));
}

void *set_inheritable(__ss_int fd, __ss_bool inheritable) {
    int flags = ::fcntl((int)fd, F_GETFD);
    if (flags == -1)
        __throw_oserror();
    int new_flags = inheritable ? (flags & ~FD_CLOEXEC) : (flags | FD_CLOEXEC);
    if (new_flags != flags && ::fcntl((int)fd, F_SETFD, new_flags) == -1)
        __throw_oserror();
    return NULL;
}

__ss_bool get_blocking(__ss_int fd) {
    int flags = ::fcntl((int)fd, F_GETFL);
    if (flags == -1)
        __throw_oserror();
    return __mbool(!(flags & O_NONBLOCK));
}

void *set_blocking(__ss_int fd, __ss_bool blocking) {
    int flags = ::fcntl((int)fd, F_GETFL);
    if (flags == -1)
        __throw_oserror();
    int new_flags = blocking ? (flags & ~O_NONBLOCK) : (flags | O_NONBLOCK);
    if (new_flags != flags && ::fcntl((int)fd, F_SETFL, new_flags) == -1)
        __throw_oserror();
    return NULL;
}

/* shedskin behaves like cpython in utf-8 mode (the default from 3.15 on) */
str *device_encoding(__ss_int fd) {
    if (!::isatty((int)fd))
        return NULL;
    return new str("utf-8");
}

terminal_size *get_terminal_size(__ss_int fd) {
    struct winsize w;
    if (::ioctl((int)fd, TIOCGWINSZ, &w) != 0)
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
    std::filesystem::resize_file(path->c_str(), (std::uintmax_t)length, ec);
    if (ec) {
        std::error_condition c = ec.default_error_condition();
        errno = (c.category() == std::generic_category()) ? c.value() : EIO;
        __throw_oserror(path);
    }
    return NULL;
}

void *closerange(__ss_int fd_low, __ss_int fd_high) {
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
        h = (HANDLE)::_get_osfhandle((int)fd);
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
        tty = ::_isatty((int)fd);
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
    switch (fd) {
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
        r = ::_lseeki64((int)fd, (__int64)pos, (int)how);
    }
    if(r == -1)
        __throw_oserror(new str("os.lseek"));
    return (__ss_int)r;
}
#else
__ss_int lseek(__ss_int fd, __ss_int pos, __ss_int how) {
    off_t r = ::lseek((int)fd, pos, (int)how);
    if(r == -1)
        __throw_oserror(new str("os.lseek"));
    return (__ss_int)r;
}
#endif

/* symlink is declared unconditionally in __init__.hpp */
#ifdef WIN32
void *symlink(str *src, str *dst, __ss_bool target_is_directory) {
    /* like cpython: pick the directory flag when asked to, or when the
       target exists and is a directory */
    std::error_code ec;
    std::filesystem::path target = std::filesystem::path(dst->unit).parent_path() / src->unit;
    DWORD flags = (target_is_directory || std::filesystem::is_directory(target, ec)) ? SYMBOLIC_LINK_FLAG_DIRECTORY : 0;
#ifdef SYMBOLIC_LINK_FLAG_ALLOW_UNPRIVILEGED_CREATE
    flags |= SYMBOLIC_LINK_FLAG_ALLOW_UNPRIVILEGED_CREATE;
#endif
    if(!CreateSymbolicLinkW(__to_wide(dst).c_str(), __to_wide(src).c_str(), flags))
        __throw_winerror(GetLastError(), dst);
    return NULL;
}
#else
void *symlink(str *src, str *dst, __ss_bool) { /* target_is_directory: windows only */
    if(::symlink(src->c_str(), dst->c_str()) == -1)
        __throw_oserror(new str("os.symlink"));
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

__ss_int __ss_makedev(__ss_int major, __ss_int minor) {
    return (__ss_int)makedev((unsigned)major, (unsigned)minor);
}
__ss_int __ss_major(__ss_int dev) {
    return (__ss_int)major((unsigned)dev);
}
__ss_int __ss_minor(__ss_int dev) {
    return (__ss_int)minor((unsigned)dev);
}

void *mknod(str *filename, __ss_int mode, __ss_int device) {
    if(::mknod(filename->c_str(), (unsigned)mode, (unsigned)device) == -1)
        __throw_oserror(new str("os.mknod"));
    return NULL;
}

char **__exec_argvlist(list<str *> *args) {
    char** argvlist = (char**)GC_malloc(sizeof(char*)*(args->units.size()+1));
    for(__ss_int i = 0; i < args->__len__(); ++i) {
        argvlist[i] = (char *)(args->__getitem__(i)->c_str());
    }
    argvlist[args->__len__()] = NULL;
    return argvlist;
}

char **__exec_envplist(dict<str *, str *> *env) {
    char** envplist = (char**)GC_malloc(sizeof(char*)*(env->gcd.size()+1));
    list<tuple<str *> *> *items = new list<tuple<str *> *>(env->items());
    for(__ss_int i=0; i < items->__len__(); i++) {
        envplist[i] = (char *)(__add_strs(3, items->__getitem__(i)->__getfirst__(), new str("="), items->__getitem__(i)->__getsecond__())->c_str());
    }
    envplist[items->__len__()] = NULL;
    return envplist;
}

void *execv(str* file, list<str*>* args) {
    ::execv(file->c_str(), __exec_argvlist(args));
    __throw_oserror(new str("os.execv"));
}

void *execvp(str* file, list<str*>* args) {
    tuple<str *> *h_t = __path__::split(file);

    if( ___bool(h_t->__getfirst__())) {
        execv(file,args);
        __throw_oserror(new str("os.execvp"));
    }

    list<str *> *PATH = get_exec_path();

    for(__ss_int i = 0; i < PATH->__len__(); ++i) {
        str* dir = PATH->__getfast__(i);
        str* fullname = __path__::join(2, dir, file);
        if(__path__::exists(fullname)) {
            execv(fullname, args);
        }
    }
    __throw_oserror(new str("os.execvp"));
}

void *execve(str* file, list<str*>* args, dict<str *, str *> *env) {
    ::execve(file->c_str(), __exec_argvlist(args), __exec_envplist(env));
    __throw_oserror(new str("os.execve"));
}

void *execvpe(str* file, list<str*>* args, dict<str *, str *> *env) {
    tuple<str *> *h_t = __path__::split(file);

    if( ___bool(h_t->__getfirst__())) {
        execve(file, args, env);
        __throw_oserror(new str("os.execvpe"));
    }

    list<str *> *PATH = get_exec_path(env);

    for(__ss_int i = 0; i < PATH->__len__(); ++i) {
        str* dir = PATH->__getfast__(i);
        str* fullname = __path__::join(2, dir, file);
        if(__path__::exists(fullname))
            execve(fullname, args, env);
    }
    __throw_oserror(new str("os.execvpe"));
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
    __ss_int pid;
    if(!(pid = fork())) /* XXX no spawn* for C++..? */
        execv(file, args);
    else if (mode == __ss_P_WAIT)
        return __spawn_wait_result(pid);
    return pid;
}

__ss_int spawnvp(__ss_int mode, str *file, list<str *> *args) {
    __ss_int pid;
    if(!(pid = fork())) /* XXX no spawn* for C++..? */
        execvp(file, args);
    else if (mode == __ss_P_WAIT)
        return __spawn_wait_result(pid);
    return pid;
}

__ss_int spawnve(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env) {
    __ss_int pid;
    if(!(pid = fork())) /* XXX no spawn* for C++..? */
        execve(file, args, env);
    else if (mode == __ss_P_WAIT)
        return __spawn_wait_result(pid);
    return pid;
}

__ss_int spawnvpe(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env) {
    __ss_int pid;
    if(!(pid = fork())) /* XXX no spawn* for C++..? */
        execvpe(file, args, env);
    else if (mode == __ss_P_WAIT)
        return __spawn_wait_result(pid);
    return pid;
}

#endif

/* pipe is declared unconditionally in __init__.hpp */
tuple<__ss_int>* pipe() {
    int fds[2];
    __ss_int ret;

#ifdef WIN32
    ret = ::_pipe(fds, 4096, _O_BINARY);
#else
    ret = ::pipe(fds);
#endif

    if(ret != 0) {
        str* s = new str("os.pipe failed");

        __throw_oserror(s);
    }

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
    cl___cstat = new class_("__cstat");
    cl_DirEntry = new class_("DirEntry");
    cl_terminal_size = new class_("terminal_size");
    cl_times_result = new class_("times_result");

    linesep = new str("\n");
#ifdef WIN32
    name = new str("nt");
#else
    name = new str("posix");
    cl___vfsstat = new class_("__vfsstat");
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

