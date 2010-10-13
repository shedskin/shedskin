#include "__init__.hpp"
#include "path.hpp"

#include <cstdlib>
#include <sstream>
#include <sys/stat.h>
#include <stdio.h>
#include <dirent.h>
#include <errno.h>
#include <sys/time.h>
#include <sys/types.h>
#include <fcntl.h>
#include <utime.h>

#ifndef WIN32
#include <sys/times.h>
#include <sys/wait.h>
#include <sys/utsname.h>
#include <sys/statvfs.h>
#include <grp.h>
#include <sysexits.h>
#endif

namespace std {
#include <unistd.h>
}

#ifdef WIN32
//#include <windows.h>
#endif

#ifdef __FreeBSD__
#include <roken.h>
#include <libutil.h>
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

str *const_0;
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

list<str *> *listdir(str *path) {
    list<str *> *r = new list<str *>();
    DIR *dp;
    struct dirent *ep;

    dp = opendir(path->unit.c_str());

    while ((ep = readdir(dp)))
        if(strcmp(ep->d_name, ".") && strcmp(ep->d_name, ".."))
            r->append(new str(ep->d_name));

    closedir (dp);
    return r;
}

str *getcwd() {
    str *r;
    char *d=::getcwd(0, 256);
    r = new str(d);
    free(d);
    return r;
}

void *chdir(str *dir) {
    if(::chdir(dir->unit.c_str()) == -1)
        throw new OSError(dir);
    return NULL;
}

str *strerror(__ss_int i) {
    return new str(::strerror(i));
}

__ss_int system(str *c) {
    return std::system(c->unit.c_str());
}

str *getenv(str *name, str *alternative) {
    const char *waba = name->unit.c_str();
    if(std::getenv(waba))
        return new str(std::getenv(waba));
    return alternative;
}

void *rename(str *a, str *b) {
    if(std::rename(a->unit.c_str(), b->unit.c_str()) == -1)
        throw new OSError(a);
    return NULL;
}

void *remove(str *path) {
    if(std::remove(path->unit.c_str()) == -1)
        throw new OSError(path);
    return NULL;
}

void *unlink(str *path) {
    remove(path);
    return NULL;
}

void *rmdir(str *a) {
    if (::rmdir(a->unit.c_str()) == -1)
        throw new OSError(a);
    return NULL;
}

void *removedirs(str *name) {
    tuple2<str *, str *> *__0, *__1, *__5;
    str *__2, *head, *tail;

    rmdir(name);
    __0 = __path__::split(name);
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
    if (::mkdir(path->unit.c_str()) == -1)
#else
    if (::mkdir(path->unit.c_str(), mode) == -1)
#endif
        throw new OSError(path);
    return NULL;
}

void _exit(__ss_int code) {
    ::exit(code);
}

void *makedirs(str *name, __ss_int mode) {
    tuple2<str *, str *> *__0, *__1;
    str *head, *tail;

    __0 = __path__::split(name);
    head = __0->__getfirst__();
    tail = __0->__getsecond__();
    if ((!___bool(tail))) {
        __1 = __path__::split(head);
        head = __1->__getfirst__();
        tail = __1->__getsecond__();
    }
    if ((___bool(head) && ___bool(tail) && (!__path__::exists(head)))) {
        try {
            makedirs(head, mode);
        } catch (OSError *e) {
            if (e->__ss_errno != EEXIST) {
                throw (e);
            }
        }
        if (__eq(tail, __path__::curdir)) {
            return NULL;
        }
    }
    mkdir(name, mode);
    return NULL;
}

void *abort() {
    std::abort();
}

/* class __cstat */

class_ *cl___cstat;

__cstat::__cstat(str *path, __ss_int t) {
    this->__class__ = cl___cstat;

    if(t==1) {
        if(stat(path->unit.c_str(), &sbuf) == -1)
            throw new OSError(path);
    } else if (t==2) {
#ifndef WIN32
        if(lstat(path->unit.c_str(), &sbuf) == -1)
#endif
            throw new OSError(path);
    }

    fill_er_up();
}

__cstat::__cstat(__ss_int fd) {
    this->__class__ = cl___cstat;

    if(fstat(fd, &sbuf) == -1)
        throw new OSError();

    fill_er_up();
}

void __cstat::fill_er_up() {
    this->st_mode = sbuf.st_mode;
    this->st_ino = sbuf.st_ino;
    this->st_dev = sbuf.st_dev;
    this->st_rdev = sbuf.st_rdev;
    this->st_nlink = sbuf.st_nlink;
    this->__ss_st_atime = sbuf.st_atime;
    this->__ss_st_mtime = sbuf.st_mtime;
    this->__ss_st_ctime = sbuf.st_ctime;
    this->st_uid = sbuf.st_uid;
    this->st_gid = sbuf.st_gid;
    this->st_size = sbuf.st_size;
#ifndef WIN32
    this->st_blksize = sbuf.st_blksize;
    this->st_blocks = sbuf.st_blocks;
#endif
}

__ss_int __cstat::__len__() {
    return 10;
}

__ss_int __cstat::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    switch(i) {
        case 0: return st_mode;
        case 1: return st_ino;
        case 2: return st_dev;
        case 3: return st_nlink;
        case 4: return st_uid;
        case 5: return st_gid;
        case 6: return st_size;
        case 7: return __ss_st_atime;
        case 8: return __ss_st_mtime;
        case 9: return __ss_st_ctime;

        default:
            throw new IndexError(new str("tuple index out of range"));
    }

    return 0;
}


/* class namedtuple */

str *namedtuple::__repr__() {
    tuple2<__ss_int, __ss_int> *t = new tuple2<__ss_int, __ss_int>();
    for(__ss_int i=0; i < __len__(); i++)
        t->units.push_back(__getitem__(i));
    return repr(t);
}

tuple2<__ss_int, __ss_int> *namedtuple::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    tuple2<__ss_int, __ss_int> *c = new tuple2<__ss_int, __ss_int>();

    slicenr(x, l, u, s, __len__());

    if(s > 0)
        for(__ss_int i=l; i<u; i += s)
            c->append(__getitem__(i));
    else
        for(__ss_int i=l; i>u; i += s)
            c->append(__getitem__(i));

    return c;
}

__cstat *stat(str *path) {
    return new __cstat(path, 1);
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

__ss_bool stat_float_times(__ss_int newvalue) {
    if(newvalue==0)
        throw new TypeError(new str("os.stat_float_times: cannot change type"));
    return True;
}

void *putenv(str* varname, str* value) {
    std::stringstream ss;
    ss << varname->unit.c_str() << '=' << value->unit.c_str();
    ::putenv(const_cast<char*>(ss.str().c_str()));
    return NULL;
}

__ss_int umask(__ss_int newmask)  {
    return ::umask(newmask);
}

#ifndef WIN32
__ss_int chmod (str* path, __ss_int val) {
#ifdef WIN32
    DWORD attr;
    __ss_int res;
    attr = GetFileAttributesA(var->unit.c_str());

    if (attr != 0xFFFFFFFF) {
        if (i & S_IWRITE)
            attr &= ~FILE_ATTRIBUTE_READONLY;
        else
            attr |= FILE_ATTRIBUTE_READONLY;
        res = SetFileAttributesA(var->unit.c_str(), attr);
    }
    else {
        res = 0;
    }
    if(!res) {
        throw new OSError("Chmod");
    }
    return 0;
#else
    return ::chmod(path->unit.c_str(), val);
#endif
}
#endif

void *renames(str* old, str* _new) {
    tuple2<str *, str *> *__0, *__1, *__5;
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

popen_pipe::popen_pipe(str *cmd, str *mode) {
    FILE* fp;

    if(!mode)
        mode = new str("r");
    fp = ::popen(cmd->unit.c_str(), mode->unit.c_str());
    this->name = cmd;
    this->mode = mode;

    print_opt.endoffile=print_opt.space=0;
    print_opt.lastchar='\n';
}

popen_pipe::popen_pipe(FILE* pipe) {
    f = pipe;
    print_opt.endoffile=print_opt.space=0;
    print_opt.lastchar='\n';
}

void *popen_pipe::close() {
    pclose(f);
    closed = 1;
    return NULL;
}

popen_pipe* popen(str* cmd) {
    return popen(cmd, new str("r"), -1);
}

popen_pipe* popen(str* cmd, str* mode) {
    return popen(cmd, mode, -1);
}

popen_pipe* popen(str* cmd, str* mode, __ss_int) {
    FILE* fp = ::popen(cmd->unit.c_str(), mode->unit.c_str());

    if(!fp) throw new OSError(cmd);
    return new popen_pipe(fp);
}

__ss_int dup(__ss_int f1) {
    __ss_int f2 = ::dup(f1);
    if (f2 == -1)
        throw new OSError(new str("os.dup failed"));
    return f2;
}

void *dup2(__ss_int f1, __ss_int f2) {
    if (::dup2(f1,f2) == -1)
        throw new OSError(new str("os.dup2 failed"));
    return NULL;
}

#if !defined(__APPLE__) && !defined(__FreeBSD__) && !defined(WIN32)
void *fdatasync(__ss_int f1) {
    if (::fdatasync(f1) == -1)
        throw new OSError(new str("os.fdatasync failed"));
    return NULL;
}
#endif

__ss_int open(str *name, __ss_int flags) { /* XXX mode argument */
    __ss_int fp = ::open(name->unit.c_str(), flags);
    if(fp == -1)
        throw new OSError(new str("os.open failed"));
    return fp;
}

file* fdopen(__ss_int fd, str* mode, __ss_int) {
    if(!mode)
        mode = new str("r");
/* XXX ValueError: mode string must begin with one of 'r', 'w', 'a' or 'U' */
    FILE* fp = ::fdopen(fd, mode->unit.c_str());
    if(fp == NULL)
        throw new OSError(new str("os.fdopen failed"));

    file* ret = new file(fp);
    ret->name = new str("<fdopen>");
    return ret;
}

str *read(__ss_int fd, __ss_int n) {  /* XXX slowness */
    char c;
    str *s = new str();
    __ss_int nr;
    for(__ss_int i=0; i<n; i++) {
        nr = ::read(fd, &c, 1);
        if(nr == -1)
            throw new OSError(new str("os.read"));
        if(nr == 0)
            break;
        s->unit += c;
    }
    return s;
}

__ss_int write(__ss_int fd, str *s) {
    __ss_int r;
    if((r=::write(fd, s->unit.c_str(), len(s))) == -1)
        throw new OSError(new str("os.write"));
    return r;
}


void *close(__ss_int fd) {
   if(::close(fd) < 0)
       throw new OSError(new str("os.close failed"));
   return NULL;
}

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
    if (::fchdir(f1) == -1)
        throw new OSError(new str("os.fchdir failed"));
    return NULL;
}

str *readlink(str *path) {
    __ss_int size = 255;
    str *r;

    while (1)
      {
        char *buffer = (char *) GC_malloc (size);
	    __ss_int nchars = ::readlink(path->unit.c_str(), buffer, size);
    	if (nchars == -1) {
            throw new OSError(path);
  	    }
        if (nchars < size) {
            buffer[nchars] = '\0';
            r = new str(buffer);
            return r;
        }
        size *= 2;
      }
}

__ss_int getuid() { return ::getuid(); }
void *setuid(__ss_int uid) {
    if(::setuid(uid) == -1)
        throw new OSError(new str("os.setuid"));
    return NULL;
}

__ss_int getgid() { return ::getgid(); }
void *setgid(__ss_int gid) {
    if(::setgid(gid) == -1)
        throw new OSError(new str("os.setgid"));
    return NULL;
}

__ss_int geteuid() { return ::geteuid(); }
void *seteuid(__ss_int euid) {
    if(::seteuid(euid) == -1)
        throw new OSError(new str("os.seteuid"));
    return NULL;
}

__ss_int getegid() { return ::getegid(); }
void *setegid(__ss_int egid) {
    if(::setegid(egid) == -1)
        throw new OSError(new str("os.setegid"));
    return NULL;
}

__ss_int getppid() { return ::getppid(); }

void *setreuid(__ss_int ruid, __ss_int euid) {
    if(::setreuid(ruid, euid) == -1)
        throw new OSError(new str("os.setreuid"));
    return NULL;
}

void *setregid(__ss_int rgid, __ss_int egid) {
    if(::setregid(rgid, egid) == -1)
        throw new OSError(new str("os.setregid"));
    return NULL;
}

__ss_int tcgetpgrp(__ss_int fd) {
    __ss_int nr;
    nr = ::tcgetpgrp(fd);
    if(nr == -1)
        throw new OSError(new str("os.tcgetpgrp"));
    return nr;
}

void *tcsetpgrp(__ss_int fd, __ss_int pg) {
    if(::tcsetpgrp(fd, pg) == -1)
        throw new OSError(new str("os.tcsetpgrp"));
    return NULL;
}

__ss_int fork() {
    __ss_int ret;
    if ((ret = ::fork()) == -1)
        throw new OSError(new str("os.fork"));
    return ret;
}

void *ftruncate(__ss_int fd, __ss_int n) {
    if (::ftruncate(fd, n) == -1)
        throw new OSError(new str("os.ftruncate"));
    return NULL;
}

#if !defined(__sun)
tuple2<__ss_int, __ss_int> *forkpty() {
    __ss_int ret;
    int amaster;
    if ((ret = ::forkpty(&amaster, NULL, NULL, NULL)) == -1)
        throw new OSError(new str("os.forkpty"));
    return new tuple2<__ss_int, __ss_int>(2, ret, (__ss_int)amaster);
}
tuple2<__ss_int, __ss_int> *openpty() {
    int amaster, aslave;
    if (::openpty(&amaster, &aslave, NULL, NULL, NULL) == -1)
        throw new OSError(new str("os.openpty"));
    return new tuple2<__ss_int, __ss_int>(2, (__ss_int)amaster, (__ss_int)aslave);
}
#endif

tuple2<__ss_int, __ss_int> *wait() {
    int pid, status;
    if((pid = ::wait(&status)) == -1)
        throw new OSError(new str("os.wait"));
    return new tuple2<__ss_int, __ss_int>(2, (__ss_int)pid, (__ss_int)status);
}

tuple2<__ss_int, __ss_int> *waitpid(__ss_int pid, __ss_int options) {
    int status;
    if((pid = ::waitpid(pid, &status, options)) == -1)
        throw new OSError(new str("os.waitpid"));
    return new tuple2<__ss_int, __ss_int>(2, pid, (__ss_int)status);
}

__ss_int nice(__ss_int n) {
    __ss_int m;
    if((m = ::nice(n)) == -1)
        throw new OSError(new str("os.nice"));
    return m;
}

void *kill(__ss_int pid, __ss_int sig) {
    if(::kill(pid, sig) == -1)
        throw new OSError(new str("os.kill"));
    return NULL;
}
void *killpg(__ss_int pgid, __ss_int sig) {
    if(::killpg(pgid, sig) == -1)
        throw new OSError(new str("os.killpg"));
    return NULL;
}

str *getlogin() {
    char *name = ::getlogin();
    if(!name)
        throw new OSError(new str("os.getlogin"));
    return new str(name);
}

void *chown(str *path, __ss_int uid, __ss_int gid) {
    if (::chown(path->unit.c_str(), uid, gid) == -1)
        throw new OSError(path);
    return NULL;
}

void *lchown(str *path, __ss_int uid, __ss_int gid) {
    if (::lchown(path->unit.c_str(), uid, gid) == -1)
        throw new OSError(path);
    return NULL;
}

void *chroot(str *path) {
    if (::chroot(path->unit.c_str()) == -1)
        throw new OSError(path);
    return NULL;
}

str *ctermid() {
    char term[L_ctermid];
    char *ptr = ::ctermid(term);
    return new str(ptr);
}

__ss_bool isatty(__ss_int fd) {
    return __mbool(::isatty(fd));
}

str *ttyname(__ss_int fd) {
    char *name = ::ttyname(fd);
    if(!name)
        throw new OSError(new str("os.ttyname"));
    return new str(name);
}

tuple2<str *, str *> *uname() {
    struct utsname name;
    ::uname(&name);
    return new tuple2<str *, str *>(5, new str(name.sysname), new str(name.nodename), new str(name.release), new str(name.version), new str(name.machine));
}

list<__ss_int> *getgroups() {
    gid_t l[MAXENTRIES];
    __ss_int nr = ::getgroups(MAXENTRIES, l);
    if(nr == -1)
        throw new OSError(new str("os.getgroups"));
    list<__ss_int> *r = new list<__ss_int>();
    for(__ss_int i=0;i<nr;i++)
        r->append(l[i]);
    return r;
}
void *setgroups(pyseq<__ss_int> *groups) {
    gid_t l[MAXENTRIES];
    for(__ss_int i=0; i<len(groups); i++)
        l[i] = groups->__getitem__(i);
    if(::setgroups(len(groups), l) == -1)
        throw new OSError(new str("os.setgroups"));
    return NULL;
}

__ss_int getsid(__ss_int pid) {
    __ss_int nr = ::getsid(pid);
    if(nr == -1)
        throw new OSError(new str("os.getsid"));
    return nr;
}
__ss_int setsid() {
    __ss_int nr = ::setsid();
    if(nr == -1)
        throw new OSError(new str("os.setsid"));
    return nr;
}

__ss_int getpgid(__ss_int pid) {
    __ss_int nr = ::getpgid(pid);
    if(nr == -1)
        throw new OSError(new str("os.getpgid"));
    return nr;
}
void *setpgid(__ss_int pid, __ss_int pgrp) {
    if(::setpgid(pid, pgrp) == -1)
        throw new OSError(new str("os.setpgid"));
    return NULL;
}

__ss_int getpgrp() {
    return getpgid(0);
}
void *setpgrp() {
    if(::setpgid(0, 0) == -1)
        throw new OSError(new str("os.setpgrp"));
    return NULL;
}

void *link(str *src, str *dst) {
    if(::link(src->unit.c_str(), dst->unit.c_str()) == -1)
        throw new OSError(new str("os.link"));
    return NULL;
}

void *symlink(str *src, str *dst) {
    if(::symlink(src->unit.c_str(), dst->unit.c_str()) == -1)
        throw new OSError(new str("os.symlink"));
    return NULL;
}

__ss_int pathconf(str *path, str *name) {
    if(!pathconf_names->__contains__(name))
        throw new ValueError(new str("unrecognized configuration name"));
    return pathconf(path, pathconf_names->__getitem__(name)); /* XXX errors */
}
__ss_int pathconf(str *path, __ss_int name) {
    __ss_int limit = ::pathconf(path->unit.c_str(), name); /* XXX errors */
    return limit;
}

__ss_int fpathconf(__ss_int fd, str *name) {
    if(!pathconf_names->__contains__(name))
        throw new ValueError(new str("unrecognized configuration name"));
    return fpathconf(fd, pathconf_names->__getitem__(name)); /* XXX errors */
}
__ss_int fpathconf(__ss_int fd, __ss_int name) {
    __ss_int limit = ::fpathconf(fd, name); /* XXX errors */
    return limit;
}

str *confstr(str *name) {
    if(!confstr_names->__contains__(name))
        throw new ValueError(new str("unrecognized configuration name"));
    return confstr(confstr_names->__getitem__(name));
}
str *confstr(__ss_int name) {
    char buf[MAXENTRIES];
    __ss_int size = ::confstr(name, buf, MAXENTRIES); /* XXX errors */
    if(size == -1)
        throw new OSError(new str("os.confstr"));
    return new str(buf);
}

__ss_int sysconf(str *name) {
    if(!sysconf_names->__contains__(name))
        throw new ValueError(new str("unrecognized configuration name"));
    return sysconf(sysconf_names->__getitem__(name)); /* XXX errors */
}
__ss_int sysconf(__ss_int name) {
    __ss_int limit = ::sysconf(name); /* XXX errors */
    return limit;
}

tuple2<double, double> *getloadavg() {
    double load[3];
    if(::getloadavg(load, 3) != 3)
        throw new OSError(new str("os.getloadavg"));
    return new tuple2<double, double>(3, load[0], load[1], load[2]);
}

void *mkfifo(str *path, __ss_int mode) {
    if(::mkfifo(path->unit.c_str(), mode) == -1)
        throw new OSError(new str("os.mkfifo"));
    return NULL;
}

/* class __vfsstat */

class_ *cl___vfsstat;

__vfsstat::__vfsstat(str *path) {
    this->__class__ = cl___vfsstat;
    if(statvfs(path->unit.c_str(), &vbuf) == -1)
        throw new OSError(path);
    fill_er_up();
}

__vfsstat::__vfsstat(__ss_int fd) {
    this->__class__ = cl___vfsstat;
    if(fstatvfs(fd, &vbuf) == -1)
        throw new OSError(__str(fd));
    fill_er_up();
}

void __vfsstat::fill_er_up() {
    this->f_bsize = vbuf.f_bsize;
    this->f_frsize = vbuf.f_frsize;
    this->f_blocks = vbuf.f_blocks;
    this->f_bfree = vbuf.f_bfree;
    this->f_bavail = vbuf.f_bavail;
    this->f_files = vbuf.f_files;
    this->f_ffree = vbuf.f_ffree;
    this->f_favail = vbuf.f_favail;
    this->f_flag = vbuf.f_flag;
    this->f_namemax = vbuf.f_namemax;
}

__ss_int __vfsstat::__len__() {
    return 10;
}

__ss_int __vfsstat::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    switch(i) {
        case 0: return vbuf.f_bsize;
        case 1: return vbuf.f_frsize;
        case 2: return vbuf.f_blocks;
        case 3: return vbuf.f_bfree;
        case 4: return vbuf.f_bavail;
        case 5: return vbuf.f_files;
        case 6: return vbuf.f_ffree;
        case 7: return vbuf.f_favail;
        case 8: return vbuf.f_flag;
        case 9: return vbuf.f_namemax;

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

void *fsync(__ss_int fd) {
    if(::fsync(fd) == -1)
        throw new OSError(new str("os.fsync"));
    return NULL;
}

void *lseek(__ss_int fd, __ss_int pos, __ss_int how) {
    if(::lseek(fd, pos, how) == -1)
        throw new OSError(new str("os.lseek"));
    return NULL;
}

str *urandom(__ss_int n) {
    __ss_int fd = open(new str("/dev/urandom"), __ss_O_RDONLY);
    str *s = read(fd, n);
    close(fd);
    return s;
}

void __utime(str *path) {
    if(::utime(path->unit.c_str(), NULL) == -1)
        throw new OSError(new str("os.utime"));
}
void __utime(str *path, double actime, double modtime) {
    struct utimbuf buf;
    buf.actime = (time_t)actime;
    buf.modtime = (time_t)modtime;
    if(::utime(path->unit.c_str(), &buf) == -1)
        throw new OSError(new str("os.utime"));
}

#define HOPPA if (times) __utime(path, times->__getfirst__(), times->__getsecond__()); else __utime(path); return NULL;

void *utime(str *path, tuple2<__ss_int, __ss_int> *times) { HOPPA }
void *utime(str *path, tuple2<__ss_int, double> *times) { HOPPA }
void *utime(str *path, tuple2<double, __ss_int> *times) { HOPPA }
void *utime(str *path, tuple2<double, double> *times) { HOPPA }

#undef HOPPA

__ss_bool access(str *path, __ss_int mode) {
    return __mbool(::access(path->unit.c_str(), mode) == 0);
}

tuple2<double, double> *times() {
    struct tms buf;
    clock_t c;
    __ss_int ticks_per_second = ::sysconf(_SC_CLK_TCK);
    if((c = ::times(&buf)) == -1)
        throw new OSError(new str("os.utime"));
    return new tuple2<double, double>(5, ((double)buf.tms_utime / ticks_per_second), ((double)buf.tms_stime / ticks_per_second), ((double)buf.tms_cutime / ticks_per_second), ((double)buf.tms_cstime / ticks_per_second), ((double)c / ticks_per_second));
}

/* str *tmpnam() { XXX raises compiler warning
    char *buf;
    if((buf = ::tmpnam(NULL)) == NULL)
        throw new OSError(new str("os.tmpnam"));
    return new str(buf);
} */
file *tmpfile() {
    FILE *f;
    if((f = ::tmpfile()) == NULL)
        throw new OSError(new str("os.tmpfile"));
    file *_file = new file(f);
    _file->name = new str("<tmpfile>");
    return _file;
}
/* str *tempnam(str *dir, str *prefix) { XXX raises compiler warning
    char *name;
    str *result;
    char *pfx = NULL;
    if(prefix) pfx = (char *)(prefix->unit.c_str());
    if((name = ::tempnam(dir->unit.c_str(), pfx)) == NULL)
        throw new OSError(new str("os.tempnam"));
    result = new str(name);
    free(name);
    return result;
} */

__ss_int __ss_makedev(__ss_int major, __ss_int minor) {
    return makedev(major, minor);
}
__ss_int __ss_major(__ss_int dev) {
    return major(dev);
}
__ss_int __ss_minor(__ss_int dev) {
    return minor(dev);
}

void *mknod(str *filename, __ss_int mode, __ss_int device) {
    if(::mknod(filename->unit.c_str(), mode, device) == -1)
        throw new OSError(new str("os.mknod"));
    return NULL;
}

char **__exec_argvlist(list<str *> *args) {
    char** argvlist = (char**)GC_malloc(sizeof(char*)*(args->__len__()+1));
    for(__ss_int i = 0; i < args->__len__(); ++i) {
        argvlist[i] = (char *)(args->__getitem__(i)->unit.c_str());
    }
    argvlist[args->__len__()] = NULL;
    return argvlist;
}

char **__exec_envplist(dict<str *, str *> *env) {
    char** envplist = (char**)GC_malloc(sizeof(char*)*(env->__len__()+1));
    list<tuple2<str *, str *> *> *items = env->items();
    for(__ss_int i=0; i < items->__len__(); i++) {
        envplist[i] = (char *)(__add_strs(3, items->__getitem__(i)->__getfirst__(), new str("="), items->__getitem__(i)->__getsecond__())->unit.c_str());
    }
    envplist[items->__len__()] = NULL;
    return envplist;
}

list<str *> *__exec_path() {
    str* envpath;
    if(__ss_environ->__contains__(new str("PATH")))
        envpath = __ss_environ->get(new str("PATH"));
    else
        envpath = defpath;
    return envpath->split(pathsep);
}

void *execl(__ss_int n, str *file, ...) {
     list<str *> *vals = new list<str *>();
     va_list args;
     va_start(args, file);
     for(__ss_int i=0; i<n-1; i++)
         vals->append(va_arg(args, str *)); /* XXX check str */
     va_end(args);
     execv(file, vals);
     return NULL;
}

void *execlp(__ss_int n, str *file, ...) {
     list<str *> *vals = new list<str *>();
     va_list args;
     va_start(args, file);
     for(__ss_int i=0; i<n-1; i++)
         vals->append(va_arg(args, str *)); /* XXX check str */
     va_end(args);
     execvp(file, vals);
     return NULL;
}

void *execle(__ss_int n, str *file, ...) {
     list<str *> *vals = new list<str *>();
     va_list args;
     va_start(args, file);
     for(__ss_int i=0; i<n-2; i++)
         vals->append(va_arg(args, str *)); /* XXX check str */
     va_end(args);
     dict<str *, str *> *env = (dict<str *, str *> *)(va_arg(args, pyobj *)); /* XXX check */
     execve(file, vals, env);
     return NULL;
}

void *execlpe(__ss_int n, str *file, ...) {
     list<str *> *vals = new list<str *>();
     va_list args;
     va_start(args, file);
     for(__ss_int i=0; i<n-2; i++)
         vals->append(va_arg(args, str *)); /* XXX check str */
     va_end(args);
     dict<str *, str *> *env = (dict<str *, str *> *)(va_arg(args, pyobj *)); /* XXX check */
     execvpe(file, vals, env);
     return NULL;
}

void *execv(str* file, list<str*>* args) {
    ::execv(file->unit.c_str(), __exec_argvlist(args));
    throw new OSError(new str("os.execv"));
}

void *execvp(str* file, list<str*>* args) {
    tuple2<str*,str*>* h_t = __path__::split(file);

    if( ___bool(h_t->__getfirst__())) {
        execv(file,args);
        throw new OSError(new str("os.execvp"));
    }

    list<str *> *PATH = __exec_path();

    for(__ss_int i = 0; i < PATH->__len__(); ++i) {
        str* dir = PATH->__getfast__(i);
        str* fullname = __path__::join(2, dir, file);
        if(__path__::exists(fullname)) {
            execv(fullname, args);
        }
    }
    throw new OSError(new str("os.execvp"));
}

void *execve(str* file, list<str*>* args, dict<str *, str *> *env) {
    ::execve(file->unit.c_str(), __exec_argvlist(args), __exec_envplist(env));
    throw new OSError(new str("os.execve"));
}

void *execvpe(str* file, list<str*>* args, dict<str *, str *> *env) {

    tuple2<str*,str*>* h_t = __path__::split(file);

    if( ___bool(h_t->__getfirst__())) {
        execve(file, args, env);
        throw new OSError(new str("os.execvpe"));
    }

    list<str *> *PATH = __exec_path();

    for(__ss_int i = 0; i < PATH->__len__(); ++i) {
        str* dir = PATH->__getfast__(i);
        str* fullname = __path__::join(2, dir, file);
        if(__path__::exists(fullname))
            execve(fullname, args, env);
    }
    throw new OSError(new str("os.execvpe"));
}

__ss_int spawnl(__ss_int n, __ss_int mode, str *file, ...) {
     list<str *> *vals = new list<str *>();
     va_list args;
     va_start(args, file);
     for(__ss_int i=0; i<n-2; i++)
         vals->append(va_arg(args, str *)); /* XXX check str */
     va_end(args);
     return spawnv(mode, file, vals);
}

__ss_int spawnlp(__ss_int n, __ss_int mode, str *file, ...) {
     list<str *> *vals = new list<str *>();
     va_list args;
     va_start(args, file);
     for(__ss_int i=0; i<n-2; i++)
         vals->append(va_arg(args, str *)); /* XXX check str */
     va_end(args);
     return spawnvp(mode, file, vals);
}

__ss_int spawnle(__ss_int n, __ss_int mode, str *file, ...) {
     list<str *> *vals = new list<str *>();
     va_list args;
     va_start(args, file);
     for(__ss_int i=0; i<n-3; i++)
         vals->append(va_arg(args, str *)); /* XXX check str */
     va_end(args);
     dict<str *, str *> *env = (dict<str *, str *> *)(va_arg(args, pyobj *)); /* XXX check */
     return spawnve(mode, file, vals, env);
}

__ss_int spawnlpe(__ss_int n, __ss_int mode, str *file, ...) {
     list<str *> *vals = new list<str *>();
     va_list args;
     va_start(args, file);
     for(__ss_int i=0; i<n-3; i++)
         vals->append(va_arg(args, str *)); /* XXX check str */
     va_end(args);
     dict<str *, str *> *env = (dict<str *, str *> *)(va_arg(args, pyobj *)); /* XXX check */
     return spawnvpe(mode, file, vals, env);
}

__ss_int spawnv(__ss_int mode, str *file, list<str *> *args) {
    __ss_int pid;
    tuple2<__ss_int, __ss_int> *t;
    if(!(pid = fork())) /* XXX no spawn* for C++..? */
        execv(file, args);
    else if (mode == __ss_P_WAIT) {
        t = waitpid(pid, 0);
        return t->__getsecond__();
    }
    return pid;
}

__ss_int spawnvp(__ss_int mode, str *file, list<str *> *args) {
    __ss_int pid;
    tuple2<__ss_int, __ss_int> *t;
    if(!(pid = fork())) /* XXX no spawn* for C++..? */
        execvp(file, args);
    else if (mode == __ss_P_WAIT) {
        t = waitpid(pid, 0);
        return t->__getsecond__();
    }
    return pid;
}

__ss_int spawnve(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env) {
    __ss_int pid;
    tuple2<__ss_int, __ss_int> *t;
    if(!(pid = fork())) /* XXX no spawn* for C++..? */
        execve(file, args, env);
    else if (mode == __ss_P_WAIT) {
        t = waitpid(pid, 0);
        return t->__getsecond__();
    }
    return pid;
}

__ss_int spawnvpe(__ss_int mode, str *file, list<str *> *args, dict<str *, str *> *env) {
    __ss_int pid;
    tuple2<__ss_int, __ss_int> *t;
    if(!(pid = fork())) /* XXX no spawn* for C++..? */
        execvpe(file, args, env);
    else if (mode == __ss_P_WAIT) {
        t = waitpid(pid, 0);
        return t->__getsecond__();
    }
    return pid;
}

__ss_int getpid() {
    //return GetCurrentProcessId();
    return ::getpid();
}

void *unsetenv (str* var) {
    ::unsetenv(var->unit.c_str());
    return NULL;
}

tuple2<file*,file*>* popen2(str* cmd) {
    return popen2(cmd, new str("t"), -1);
}

tuple2<file*,file*>* popen2(str* cmd, str*, __ss_int) {
    tuple2<__ss_int,__ss_int>* p2c = pipe();
    tuple2<__ss_int,__ss_int>* c2p = pipe();

    __ss_int pid = fork();

    if(pid == 0) {
        dup2( p2c->__getfirst__(), 0);
        dup2( c2p->__getsecond__(), 1);

        for(__ss_int i = 3; i < MAXENTRIES; ++i) {
            try {
                close(i);
            }
            catch(OSError*) {}
        }

        list<str*>* cmd_l = new list<str*>(3, new str("/bin/sh"),
                new str("-c"), cmd);
        execvp(new str("/bin/sh"), cmd_l);
        ::exit(1);
    }

    close(p2c->__getfirst__());
    close(c2p->__getsecond__());

    tuple2<file*, file*>* ret = new tuple2<file*,file*>();
    ret->__init2__(fdopen(p2c->__getsecond__(),new str("w")), fdopen(c2p->__getfirst__(), new str("r")));

    return ret;
}

tuple2<file*,file*>* popen3(str* cmd) {
    return popen3(cmd, new str("t"), -1);
}


tuple2<file*,file*>* popen3(str* cmd, str*, __ss_int) {
    tuple2<__ss_int,__ss_int>* p2c = pipe();
    tuple2<__ss_int,__ss_int>* c2p = pipe();
    tuple2<__ss_int,__ss_int>* erp = pipe();

    __ss_int pid = fork();

    if(pid == 0) {
        dup2( p2c->__getfirst__(), 0);
        dup2( c2p->__getsecond__(), 1);
        dup2( erp->__getsecond__(), 2);

        for(__ss_int i = 3; i < MAXENTRIES; ++i) {
            try {
                close(i);
            }
            catch(OSError*) {}
        }

        list<str*>* cmd_l = new list<str*>(3, new str("/bin/sh"),
                new str("-c"), cmd);
        execvp(new str("/bin/sh"), cmd_l);
        ::exit(1);
    }

    close(p2c->__getfirst__());
    close(c2p->__getsecond__());
    close(erp->__getsecond__());

    return new tuple2<file*,file*>(3,fdopen(p2c->__getsecond__(),new str("w")), fdopen(c2p->__getfirst__(), new str("r")), fdopen(erp->__getfirst__(), new str("r")) );
}

tuple2<file*,file*>* popen4(str* cmd) {
    return popen4(cmd, new str("t"), -1);
}

tuple2<file*,file*>* popen4(str* cmd, str*, __ss_int) {
    tuple2<__ss_int,__ss_int>* p2c = pipe();
    tuple2<__ss_int,__ss_int>* c2p = pipe();

    __ss_int pid = fork();

    if(pid == 0) {
        dup2( p2c->__getfirst__(), 0);
        dup2( c2p->__getsecond__(), 1);
        dup2( c2p->__getsecond__(), 2);

        for(__ss_int i = 3; i < MAXENTRIES; ++i) {
            try {
                close(i);
            }
            catch(OSError*) {}
        }

        list<str*>* cmd_l = new list<str*>(3, new str("/bin/sh"),
                new str("-c"), cmd);
        execvp(new str("/bin/sh"), cmd_l);
        ::exit(1);
    }

    close(p2c->__getfirst__());
    close(c2p->__getsecond__());

    tuple2<file*, file*>* ret = new tuple2<file*,file*>();
    ret->__init2__(fdopen(p2c->__getsecond__(),new str("w")), fdopen(c2p->__getfirst__(), new str("r")));

    return ret;

}

tuple2<__ss_int,__ss_int>* pipe() {
    int fds[2];
    __ss_int ret;

    ret = ::pipe(fds);

    if(ret != 0) {
        str* s = new str("os.pipe failed");

        throw new OSError(s);
    }

    return new tuple2<__ss_int,__ss_int>(2,(__ss_int)fds[0],(__ss_int)fds[1]);
}
#endif

void __init() {
    const_0 = new str("(%d, %d, %d, %d, %d, %d, %d, %d, %d, %d)");

    cl___cstat = new class_("__cstat", 4, 4);

    linesep = new str("\n");
#ifdef WIN32
    name = new str("nt");
#else
    name = new str("posix");
    cl___vfsstat = new class_("__vfsstat", 4, 4);
#endif

    __ss_environ = new dict<str *, str *>();

    for (__ss_int n = 0; environ[n]; n++) {
        str *line = new str(environ[n]);
        __ss_int pos = line->find(new str("="));
        __ss_environ->__setitem__(line->__slice__(2, 0, pos, 0), line->__slice__(1, (pos+1), 0, 0));
    }

    __path__::__init(); /* ugh */

    curdir = __path__::curdir;
    pardir = __path__::pardir;
    extsep = __path__::extsep;
    sep = __path__::sep;
    pathsep = __path__::pathsep;
    defpath = __path__::defpath;
    altsep = __path__::altsep;
    devnull = __path__::devnull;

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

    __ss_P_WAIT = 0; /* XXX */
    __ss_P_NOWAIT = 1;
    __ss_P_NOWAITO = 1;
    __ss_P_OVERLAY = 2;
    __ss_P_DETACH = 3;

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

