#include "__init__.hpp"
#include "path.hpp"

#include <cstdlib>
#include <sstream>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/utsname.h>
#include <stdio.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <pty.h>

namespace std {
#include <unistd.h>
}

#ifdef WIN32
//#include <windows.h>
#endif

/* environ */
#ifdef __FreeBSD__
#include <roken.h>
#endif

#ifdef __APPLE__
#include <crt_externs.h>
#define environ (*_NSGetEnviron())
#endif

#ifdef __sun
extern char **environ;
#endif

namespace __os__ {

str *const_0;
str *linesep, *name;
dict<str *, str *> *__ss_environ;
dict<str *, int> *pathconf_names, *confstr_names, *sysconf_names;
struct stat sbuf;

const int MAXENTRIES = 4096; /* XXX fix functions that use this */

str *altsep, *curdir, *defpath, *devnull, *extsep, *pardir, *pathsep, *sep;

int __ss_O_APPEND, __ss_O_CREAT, __ss_O_EXCL, __ss_O_RDONLY, __ss_O_RDWR, __ss_O_TRUNC, __ss_O_WRONLY;

list<str *> *listdir(str *path) {
    list<str *> *r = new list<str *>();
    DIR *dp;
    struct dirent *ep;
    int count = 0;

    dp = opendir(path->unit.c_str());

    while (ep = readdir(dp))
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

str *strerror(int i) {
    return new str(::strerror(i));
}

int system(str *c) {
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

void *rmdir(str *a) {
    if (::rmdir(a->unit.c_str()) == -1)
        throw new OSError(a);
    return NULL;
}

void *removedirs(str *name) {
    tuple2<str *, str *> *__0, *__1, *__5;
    str *__2, *__3, *head, *tail;

    rmdir(name);
    __0 = __path__::split(name);
    head = __0->__getfirst__();
    tail = __0->__getsecond__();
    if ((!__bool(tail))) {
        __1 = __path__::split(head);
        head = __1->__getfirst__();
        tail = __1->__getsecond__();
    }

    while(__bool(__AND(head, tail, 2))) {
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


void *mkdir(str *path, int mode) {
#ifdef WIN32
    if (::mkdir(path->unit.c_str()) == -1)
#else
    if (::mkdir(path->unit.c_str(), mode) == -1)
#endif
        throw new OSError(path);
    return NULL;
}

void *makedirs(str *name, int mode) {
    tuple2<str *, str *> *__0, *__1;
    str *head, *tail;
    int __2, __3, __4;

    __0 = __path__::split(name);
    head = __0->__getfirst__();
    tail = __0->__getsecond__();
    if ((!__bool(tail))) {
        __1 = __path__::split(head);
        head = __1->__getfirst__();
        tail = __1->__getsecond__();
    }
    if ((__bool(head) && __bool(tail) && (!__path__::exists(head)))) {
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

__cstat::__cstat(str *path, int t) {
    int hop;
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
    
__cstat::__cstat(int fd) {
    int hop;
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

str *__cstat::__repr__() {
    return __modct(const_0, 10, __box(this->st_mode), __box(this->st_ino), __box(this->st_dev), __box(this->st_nlink), __box(this->st_uid), __box(this->st_gid), __box(this->st_size), __box(this->__ss_st_mtime), __box(this->__ss_st_atime), __box(this->__ss_st_ctime));
}

int __cstat::__len__() {
    return 10;
}

int __cstat::__getitem__(int i) {
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

tuple2<int, int> *__cstat::__slice__(int x, int l, int u, int s) {
    tuple2<int, int> *c = new tuple2<int, int>();

    slicenr(x, l, u, s, 10);
 
    if(s > 0)
        for(int i=l; i<u; i += s)
            c->append(__getitem__(i));
    else
        for(int i=l; i>u; i += s)
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
__cstat *fstat(int fd) {
    return new __cstat(fd);
}

int stat_float_times(int newvalue) {
    if(newvalue==0)
        throw new TypeError(new str("os.stat_float_times: cannot change type"));
    return 1;
}

#ifndef WIN32
int getpid() {
    //return GetCurrentProcessId();
    return ::getpid();
}
#endif

void *putenv(str* varname, str* value) {
    std::stringstream ss;
    ss << varname->unit.c_str() << '=' << value->unit.c_str();
    ::putenv(const_cast<char*>(ss.str().c_str()));
    return NULL;
}

int umask(int newmask)  {
    return ::umask(newmask);
}

#ifndef WIN32
void *unsetenv (str* var) {
    ::unsetenv(var->unit.c_str());
    return NULL;
}

int chmod (str* path, int val) {
#ifdef WIN32
    DWORD attr;
    int res;
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
    str *__2, *__3, *head, *tail;


    __0 = __path__::split(_new);
    head = __0->__getfirst__();
    tail = __0->__getsecond__();

    if ((!__bool(tail))) {
        __1 = __path__::split(head);
        head = __1->__getfirst__();
        tail = __1->__getsecond__();
    }
    
    while(__bool(__AND(head, tail, 2)) && !__path__::exists(head)) {
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

    if ((!__bool(tail))) {
        __1 = __path__::split(head);
        head = __1->__getfirst__();
        tail = __1->__getsecond__();
    }

    if(__bool(__AND(head,tail,2))) {
        removedirs(head);
    }
    return NULL;
}

popen_pipe* popen(str* cmd) {
    return popen(cmd, new str("r"), -1);
}

popen_pipe* popen(str* cmd, str* mode) {
    return popen(cmd, mode, -1);
}

popen_pipe* popen(str* cmd, str* mode, int bufsize) {
    FILE* fp = ::popen(cmd->unit.c_str(), mode->unit.c_str());

    if(!fp) throw new OSError(cmd);
    return new popen_pipe(fp);
}

int dup(int f1) {
    int f2 = ::dup(f1);
    if (f2 == -1) 
        throw new OSError(new str("os.dup failed"));
    return f2;
}

void *dup2(int f1, int f2) {
    if (::dup2(f1,f2) == -1) 
        throw new OSError(new str("os.dup2 failed"));
    return NULL;
}

void *fchdir(int f1) {
    if (::fchdir(f1) == -1) 
        throw new OSError(new str("os.fchdir failed"));
    return NULL;
}

void *fdatasync(int f1) {
    if (::fdatasync(f1) == -1) 
        throw new OSError(new str("os.fdatasync failed"));
    return NULL;
}

#ifndef WIN32
void *execv(str* file, list<str*>* args) {
    //char** argvlist = new char*[ args->__len__()+1];
    char** argvlist = (char**) GC_malloc( sizeof(char*) * (args->__len__()+1));

    for(int i = 0; i < args->__len__(); ++i) {
        argvlist[i] = const_cast<char*>(args->__getfast__(i)->unit.c_str());
    }
    argvlist[args->__len__()] = NULL;

    ::execv(file->unit.c_str(), argvlist);

    //delete[] argvlist;

    throw new OSError(new str("execv error"));
}

void *execvp(str* file, list<str*>* args) {
    tuple2<str*,str*>* h_t = __path__::split(file);

    if( __bool(h_t->__getfirst__())) {
        execv(file,args);
        return NULL;
    }

    str* envpath;
    
    if(__ss_environ->__contains__(new str("PATH"))) {
        envpath = __ss_environ->get(new str("PATH"));
    }
    else {
        envpath = defpath;
    }

    list<str*>* PATH = envpath->split(pathsep);

    for(int i = 0; i < PATH->__len__(); ++i) {
        str* dir = PATH->__getfast__(i);
        str* fullname = __path__::join(2, dir, file);
        if(__path__::exists(fullname)) {
            execv(fullname, args);
        }
    }
    throw new OSError(new str("os.execvp failed"));
}
#endif

int open(str *name, int flags) { /* XXX mode argument */
    int fp = ::open(name->unit.c_str(), flags);
    if(fp == -1)
        throw new OSError(new str("os.open failed"));
    return fp;
}

file* fdopen(int fd, str* mode, int bufsize) {
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

str *read(int fd, int n) {  /* XXX slowness */
    char c;
    str *s = new str();
    int nr;
    for(int i=0; i<n; i++) {
        nr = ::read(fd, &c, 1);
        if(nr == -1)
            throw new OSError(new str("os.read"));
        if(nr == 0)
            break;
        s->unit += c;
    }
    return s;
}

int write(int fd, str *s) {
    int r;
    if((r=::write(fd, s->unit.c_str(), len(s))) == -1)
        throw new OSError(new str("os.write"));
    return r;
}

#ifndef WIN32
tuple2<file*,file*>* popen2(str* cmd) {
    return popen2(cmd, new str("t"), -1);
}

tuple2<file*,file*>* popen2(str* cmd, str* mode, int bufsize) {
    tuple2<int,int>* p2c = pipe();
    tuple2<int,int>* c2p = pipe();

    int pid = fork();

    if(pid == 0) {
        dup2( p2c->__getfirst__(), 0);
        dup2( c2p->__getsecond__(), 1);

        for(int i = 3; i < MAXENTRIES; ++i) {
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


tuple2<file*,file*>* popen3(str* cmd, str* mode, int bufsize) {
    tuple2<int,int>* p2c = pipe();
    tuple2<int,int>* c2p = pipe();
    tuple2<int,int>* erp = pipe();

    int pid = fork();

    if(pid == 0) {
        dup2( p2c->__getfirst__(), 0);
        dup2( c2p->__getsecond__(), 1);
        dup2( erp->__getsecond__(), 2);

        for(int i = 3; i < MAXENTRIES; ++i) {
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

tuple2<file*,file*>* popen4(str* cmd, str* mode, int bufsize) {
    tuple2<int,int>* p2c = pipe();
    tuple2<int,int>* c2p = pipe();

    int pid = fork();

    if(pid == 0) {
        dup2( p2c->__getfirst__(), 0);
        dup2( c2p->__getsecond__(), 1);
        dup2( c2p->__getsecond__(), 2);

        for(int i = 3; i < MAXENTRIES; ++i) {
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

#endif

void *close(int fd) {
   if(::close(fd) < 0) 
       throw new OSError(new str("os.close failed"));
   return NULL;
}

popen_pipe::popen_pipe(str *cmd, str *mode) {
    FILE* fp;

    if(!mode)
        mode = new str("r");
    fp = ::popen(cmd->unit.c_str(), mode->unit.c_str());
    this->name = cmd;
    this->mode = mode;

    endoffile=print_space=0;
    print_lastchar='\n';
}

popen_pipe::popen_pipe(FILE* pipe) {
    f = pipe;
    endoffile=print_space=0;
    print_lastchar='\n';
}

void *popen_pipe::close() {
    pclose(f);
    closed = 1;
    return NULL;
}

#ifndef WIN32
tuple2<int,int>* pipe() {
    int fds[2];
    int ret;

    ret = ::pipe(fds);

    if(ret != 0) {
        str* s = new str("os.pipe failed");

        throw new OSError(s);
    }

    return new tuple2<int,int>(2,fds[0],fds[1]);
}
#endif

/* UNIX-only functionality */

#ifndef WIN32
str *readlink(str *path) {
    int size = 255;
    str *r;

    while (1)
      {
        char *buffer = (char *) GC_malloc (size);
	    int nchars = ::readlink(path->unit.c_str(), buffer, size);
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

int getuid() { return ::getuid(); }
void *setuid(int uid) { 
    if(::setuid(uid) == -1)
        throw new OSError(new str("os.setuid"));
    return NULL; 
}

int getgid() { return ::getgid(); }
void *setgid(int gid) { 
    if(::setgid(gid) == -1)
        throw new OSError(new str("os.setgid"));
    return NULL; 
}

int geteuid() { return ::geteuid(); }
void *seteuid(int euid) { 
    if(::seteuid(euid) == -1)
        throw new OSError(new str("os.seteuid"));
    return NULL; 
}

int getegid() { return ::getegid(); }
void *setegid(int egid) {
    if(::setegid(egid) == -1)
        throw new OSError(new str("os.setegid"));
    return NULL; 
}

int getppid() { return ::getppid(); }

void *setreuid(int ruid, int euid) {
    if(::setreuid(ruid, euid) == -1)
        throw new OSError(new str("os.setreuid"));
    return NULL; 
}

void *setregid(int rgid, int egid) {
    if(::setregid(rgid, egid) == -1)
        throw new OSError(new str("os.setregid"));
    return NULL; 
}

int tcgetpgrp(int fd) {
    int nr;
    nr = ::tcgetpgrp(fd);
    if(nr == -1)
        throw new OSError(new str("os.tcgetpgrp"));
    return NULL; 
}

void *tcsetpgrp(int fd, int pg) {
    if(::tcsetpgrp(fd, pg) == -1)
        throw new OSError(new str("os.tcsetpgrp"));
    return NULL; 
}

int fork() {
    int ret;
    if ((ret = ::fork()) == -1)
        throw new OSError(new str("os.fork"));
    return ret;
}

void *ftruncate(int fd, int n) {
    if (::ftruncate(fd, n) == -1)
        throw new OSError(new str("os.ftruncate"));
    return NULL;
}

tuple2<int, int> *forkpty() {
    int ret, amaster;
    if ((ret = ::forkpty(&amaster, NULL, NULL, NULL)) == -1)
        throw new OSError(new str("os.forkpty"));
    return new tuple2<int, int>(2, ret, amaster);
}
tuple2<int, int> *openpty() {
    int amaster, aslave;
    if (::openpty(&amaster, &aslave, NULL, NULL, NULL) == -1)
        throw new OSError(new str("os.openpty"));
    return new tuple2<int, int>(2, amaster, aslave);
}

tuple2<int, int> *wait() {
    int pid, status;
    if((pid = ::wait(&status)) == -1)
        throw new OSError(new str("os.wait"));
    return new tuple2<int, int>(2, pid, status);
}

tuple2<int, int> *waitpid(int pid, int options) {
    int status;
    if((pid = ::waitpid(pid, &status, options)) == -1)
        throw new OSError(new str("os.waitpid"));
    return new tuple2<int, int>(2, pid, status);
}

int nice(int n) {
    int m;
    if((m = ::nice(n)) == -1)
        throw new OSError(new str("os.nice"));
    return m;
}

void *kill(int pid, int sig) {
    if(::kill(pid, sig) == -1)
        throw new OSError(new str("os.kill"));
    return NULL;
}
void *killpg(int pgid, int sig) {
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

void *chown(str *path, int uid, int gid) {
    if (::chown(path->unit.c_str(), uid, gid) == -1) 
        throw new OSError(path);
    return NULL;
}

void *lchown(str *path, int uid, int gid) {
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

int isatty(int fd) {
    return ::isatty(fd);
}

str *ttyname(int fd) {
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

list<int> *getgroups() {
    gid_t l[MAXENTRIES];
    int nr = ::getgroups(MAXENTRIES, l);
    if(nr == -1)
        throw new OSError(new str("os.getgroups"));
    list<int> *r = new list<int>();
    for(int i=0;i<nr;i++)
        r->append(l[i]);
    return r;
}
void *setgroups(pyseq<int> *groups) {
    gid_t l[MAXENTRIES];
    for(int i=0; i<len(groups); i++)
        l[i] = groups->__getitem__(i);
    if(::setgroups(len(groups), l) == -1)
        throw new OSError(new str("os.setgroups"));
    return NULL;
}

int getsid(int pid) {
    int nr = ::getsid(pid);
    if(nr == -1)
        throw new OSError(new str("os.getsid"));
    return nr;
}
int setsid() {
    int nr = ::setsid();
    if(nr == -1)
        throw new OSError(new str("os.setsid"));
    return nr;
}

int getpgid(int pid) {
    int nr = ::getpgid(pid);
    if(nr == -1)
        throw new OSError(new str("os.getpgid"));
    return nr;
}
void *setpgid(int pid, int pgrp) {
    if(::setpgid(pid, pgrp) == -1)
        throw new OSError(new str("os.setpgid"));
    return NULL;
}

int getpgrp() {
    return getpgid(0);
}
void *setpgrp() {
    if(::setpgrp() == -1)
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

int pathconf(str *path, str *name) {
    if(!pathconf_names->__contains__(name))
        throw new ValueError(new str("unrecognized configuration name"));
    return pathconf(path, pathconf_names->__getitem__(name)); /* XXX errors */
}
int pathconf(str *path, int name) {
    int limit = ::pathconf(path->unit.c_str(), name); /* XXX errors */
    return limit;
}

int fpathconf(int fd, str *name) {
    if(!pathconf_names->__contains__(name))
        throw new ValueError(new str("unrecognized configuration name"));
    return fpathconf(fd, pathconf_names->__getitem__(name)); /* XXX errors */
}
int fpathconf(int fd, int name) {
    int limit = ::fpathconf(fd, name); /* XXX errors */
    return limit;
}

str *confstr(str *name) {
    if(!confstr_names->__contains__(name))
        throw new ValueError(new str("unrecognized configuration name"));
    return confstr(confstr_names->__getitem__(name));
}
str *confstr(int name) {
    char buf[MAXENTRIES];
    int size = ::confstr(name, buf, MAXENTRIES); /* XXX errors */
    if(size == -1)
        throw new OSError(new str("os.confstr"));
    return new str(buf);
}

int sysconf(str *name) {
    if(!sysconf_names->__contains__(name))
        throw new ValueError(new str("unrecognized configuration name"));
    return sysconf(sysconf_names->__getitem__(name)); /* XXX errors */
}
int sysconf(int name) {
    int limit = ::sysconf(name); /* XXX errors */
    return limit;
}

tuple2<double, double> *getloadavg() {
    double load[3];
    if(::getloadavg(load, 3) != 3)
        throw new OSError(new str("os.getloadavg"));
    return new tuple2<double, double>(3, load[0], load[1], load[2]);
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
#endif
    
    __ss_environ = new dict<str *, str *>();

    for (int n = 0; environ[n]; n++) {
        str *line = new str(environ[n]);
        int pos = line->find(new str("="));
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

    __ss_O_APPEND = O_APPEND;
    __ss_O_CREAT = O_CREAT;
    __ss_O_EXCL = O_EXCL;
    __ss_O_RDONLY = O_RDONLY;
    __ss_O_RDWR = O_RDWR;
    __ss_O_TRUNC = O_TRUNC;
    __ss_O_WRONLY = O_WRONLY;

    pathconf_names = new dict<str *, int>();
    pathconf_names->__setitem__(new str("PC_MAX_INPUT"), _PC_MAX_INPUT);
    pathconf_names->__setitem__(new str("PC_VDISABLE"), _PC_VDISABLE);
    pathconf_names->__setitem__(new str("PC_SYNC_IO"), _PC_SYNC_IO);
    pathconf_names->__setitem__(new str("PC_SOCK_MAXBUF"), _PC_SOCK_MAXBUF);
    pathconf_names->__setitem__(new str("PC_NAME_MAX"), _PC_NAME_MAX);
    pathconf_names->__setitem__(new str("PC_MAX_CANON"), _PC_MAX_CANON);
    pathconf_names->__setitem__(new str("PC_PRIO_IO"), _PC_PRIO_IO);
    pathconf_names->__setitem__(new str("PC_CHOWN_RESTRICTED"), _PC_CHOWN_RESTRICTED);
    pathconf_names->__setitem__(new str("PC_ASYNC_IO"), _PC_ASYNC_IO);
    pathconf_names->__setitem__(new str("PC_NO_TRUNC"), _PC_NO_TRUNC);
    pathconf_names->__setitem__(new str("PC_FILESIZEBITS"), _PC_FILESIZEBITS);
    pathconf_names->__setitem__(new str("PC_LINK_MAX"), _PC_LINK_MAX);
    pathconf_names->__setitem__(new str("PC_PIPE_BUF"), _PC_PIPE_BUF);
    pathconf_names->__setitem__(new str("PC_PATH_MAX"), _PC_PATH_MAX);

    confstr_names = new dict<str *, int>();
    confstr_names->__setitem__(new str("CS_XBS5_LP64_OFF64_CFLAGS"), _CS_XBS5_LP64_OFF64_CFLAGS);
    confstr_names->__setitem__(new str("CS_LFS64_CFLAGS"), _CS_LFS64_CFLAGS);
    confstr_names->__setitem__(new str("CS_XBS5_LPBIG_OFFBIG_LIBS"), _CS_XBS5_LPBIG_OFFBIG_LIBS);
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFFBIG_LINTFLAGS"), _CS_XBS5_ILP32_OFFBIG_LINTFLAGS);
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFF32_LIBS"), _CS_XBS5_ILP32_OFF32_LIBS);
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFF32_LINTFLAGS"), _CS_XBS5_ILP32_OFF32_LINTFLAGS);
    confstr_names->__setitem__(new str("CS_LFS64_LIBS"), _CS_LFS64_LIBS);
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFF32_CFLAGS"), _CS_XBS5_ILP32_OFF32_CFLAGS);
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFFBIG_CFLAGS"), _CS_XBS5_ILP32_OFFBIG_CFLAGS);
    confstr_names->__setitem__(new str("CS_LFS_LDFLAGS"), _CS_LFS_LDFLAGS);
    confstr_names->__setitem__(new str("CS_LFS_LINTFLAGS"), _CS_LFS_LINTFLAGS);
    confstr_names->__setitem__(new str("CS_LFS_LIBS"), _CS_LFS_LIBS);
    confstr_names->__setitem__(new str("CS_PATH"), _CS_PATH);
    confstr_names->__setitem__(new str("CS_LFS64_LINTFLAGS"), _CS_LFS64_LINTFLAGS);
    confstr_names->__setitem__(new str("CS_LFS_CFLAGS"), _CS_LFS_CFLAGS);
    confstr_names->__setitem__(new str("CS_LFS64_LDFLAGS"), _CS_LFS64_LDFLAGS);
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFFBIG_LIBS"), _CS_XBS5_ILP32_OFFBIG_LIBS);
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFF32_LDFLAGS"), _CS_XBS5_ILP32_OFF32_LDFLAGS);
    confstr_names->__setitem__(new str("CS_XBS5_LPBIG_OFFBIG_LINTFLAGS"), _CS_XBS5_LPBIG_OFFBIG_LINTFLAGS);
    confstr_names->__setitem__(new str("CS_XBS5_ILP32_OFFBIG_LDFLAGS"), _CS_XBS5_ILP32_OFFBIG_LDFLAGS);
    confstr_names->__setitem__(new str("CS_XBS5_LP64_OFF64_LINTFLAGS"), _CS_XBS5_LP64_OFF64_LINTFLAGS);
    confstr_names->__setitem__(new str("CS_XBS5_LP64_OFF64_LIBS"), _CS_XBS5_LP64_OFF64_LIBS);
    confstr_names->__setitem__(new str("CS_XBS5_LPBIG_OFFBIG_CFLAGS"), _CS_XBS5_LPBIG_OFFBIG_CFLAGS);
    confstr_names->__setitem__(new str("CS_XBS5_LPBIG_OFFBIG_LDFLAGS"), _CS_XBS5_LPBIG_OFFBIG_LDFLAGS);
    confstr_names->__setitem__(new str("CS_XBS5_LP64_OFF64_LDFLAGS"), _CS_XBS5_LP64_OFF64_LDFLAGS);

    sysconf_names = new dict<str *, int>();
    sysconf_names->__setitem__(new str("SC_REALTIME_SIGNALS"), _SC_REALTIME_SIGNALS);
    sysconf_names->__setitem__(new str("SC_PII_OSI_COTS"), _SC_PII_OSI_COTS);
    sysconf_names->__setitem__(new str("SC_PII_OSI"), _SC_PII_OSI);
    sysconf_names->__setitem__(new str("SC_T_IOV_MAX"), _SC_T_IOV_MAX);
    sysconf_names->__setitem__(new str("SC_THREADS"), _SC_THREADS);
    sysconf_names->__setitem__(new str("SC_AIO_MAX"), _SC_AIO_MAX);
    sysconf_names->__setitem__(new str("SC_USHRT_MAX"), _SC_USHRT_MAX);
    sysconf_names->__setitem__(new str("SC_THREAD_KEYS_MAX"), _SC_THREAD_KEYS_MAX);
    sysconf_names->__setitem__(new str("SC_XOPEN_XPG4"), _SC_XOPEN_XPG4);
    sysconf_names->__setitem__(new str("SC_SEM_VALUE_MAX"), _SC_SEM_VALUE_MAX);
    sysconf_names->__setitem__(new str("SC_XOPEN_XPG2"), _SC_XOPEN_XPG2);
    sysconf_names->__setitem__(new str("SC_XOPEN_XPG3"), _SC_XOPEN_XPG3);
    sysconf_names->__setitem__(new str("SC_GETGR_R_SIZE_MAX"), _SC_GETGR_R_SIZE_MAX);
    sysconf_names->__setitem__(new str("SC_SEM_NSEMS_MAX"), _SC_SEM_NSEMS_MAX);
    sysconf_names->__setitem__(new str("SC_AVPHYS_PAGES"), _SC_AVPHYS_PAGES);
    sysconf_names->__setitem__(new str("SC_NL_NMAX"), _SC_NL_NMAX);
    sysconf_names->__setitem__(new str("SC_PAGESIZE"), _SC_PAGESIZE);
    sysconf_names->__setitem__(new str("SC_EXPR_NEST_MAX"), _SC_EXPR_NEST_MAX);
    sysconf_names->__setitem__(new str("SC_XOPEN_LEGACY"), _SC_XOPEN_LEGACY);
    sysconf_names->__setitem__(new str("SC_SHRT_MAX"), _SC_SHRT_MAX);
    sysconf_names->__setitem__(new str("SC_2_SW_DEV"), _SC_2_SW_DEV);
    sysconf_names->__setitem__(new str("SC_SSIZE_MAX"), _SC_SSIZE_MAX);
    sysconf_names->__setitem__(new str("SC_RTSIG_MAX"), _SC_RTSIG_MAX);
    sysconf_names->__setitem__(new str("SC_THREAD_PRIO_INHERIT"), _SC_THREAD_PRIO_INHERIT);
    sysconf_names->__setitem__(new str("SC_EQUIV_CLASS_MAX"), _SC_EQUIV_CLASS_MAX);
    sysconf_names->__setitem__(new str("SC_NL_ARGMAX"), _SC_NL_ARGMAX);
    sysconf_names->__setitem__(new str("SC_PII_OSI_CLTS"), _SC_PII_OSI_CLTS);
    sysconf_names->__setitem__(new str("SC_2_CHAR_TERM"), _SC_2_CHAR_TERM);
    sysconf_names->__setitem__(new str("SC_THREAD_PROCESS_SHARED"), _SC_THREAD_PROCESS_SHARED);
    sysconf_names->__setitem__(new str("SC_VERSION"), _SC_VERSION);
    sysconf_names->__setitem__(new str("SC_LONG_BIT"), _SC_LONG_BIT);
    sysconf_names->__setitem__(new str("SC_SIGQUEUE_MAX"), _SC_SIGQUEUE_MAX);
    sysconf_names->__setitem__(new str("SC_ATEXIT_MAX"), _SC_ATEXIT_MAX);
    sysconf_names->__setitem__(new str("SC_BC_BASE_MAX"), _SC_BC_BASE_MAX);
    sysconf_names->__setitem__(new str("SC_SELECT"), _SC_SELECT);
    sysconf_names->__setitem__(new str("SC_XOPEN_ENH_I18N"), _SC_XOPEN_ENH_I18N);
    sysconf_names->__setitem__(new str("SC_PAGE_SIZE"), _SC_PAGE_SIZE);
    sysconf_names->__setitem__(new str("SC_PII_XTI"), _SC_PII_XTI);
    sysconf_names->__setitem__(new str("SC_MEMORY_PROTECTION"), _SC_MEMORY_PROTECTION);
    sysconf_names->__setitem__(new str("SC_TIMER_MAX"), _SC_TIMER_MAX);
    sysconf_names->__setitem__(new str("SC_AIO_LISTIO_MAX"), _SC_AIO_LISTIO_MAX);
    sysconf_names->__setitem__(new str("SC_UCHAR_MAX"), _SC_UCHAR_MAX);
    sysconf_names->__setitem__(new str("SC_SCHAR_MAX"), _SC_SCHAR_MAX);
    sysconf_names->__setitem__(new str("SC_2_UPE"), _SC_2_UPE);
    sysconf_names->__setitem__(new str("SC_NL_SETMAX"), _SC_NL_SETMAX);
    sysconf_names->__setitem__(new str("SC_RE_DUP_MAX"), _SC_RE_DUP_MAX);
    sysconf_names->__setitem__(new str("SC_BC_SCALE_MAX"), _SC_BC_SCALE_MAX);
    sysconf_names->__setitem__(new str("SC_TZNAME_MAX"), _SC_TZNAME_MAX);
    sysconf_names->__setitem__(new str("SC_LOGIN_NAME_MAX"), _SC_LOGIN_NAME_MAX);
    sysconf_names->__setitem__(new str("SC_NPROCESSORS_ONLN"), _SC_NPROCESSORS_ONLN);
    sysconf_names->__setitem__(new str("SC_SEMAPHORES"), _SC_SEMAPHORES);
    sysconf_names->__setitem__(new str("SC_SAVED_IDS"), _SC_SAVED_IDS);
    sysconf_names->__setitem__(new str("SC_XOPEN_SHM"), _SC_XOPEN_SHM);
    sysconf_names->__setitem__(new str("SC_2_FORT_RUN"), _SC_2_FORT_RUN);
    sysconf_names->__setitem__(new str("SC_XOPEN_VERSION"), _SC_XOPEN_VERSION);
    sysconf_names->__setitem__(new str("SC_IOV_MAX"), _SC_IOV_MAX);
    sysconf_names->__setitem__(new str("SC_2_VERSION"), _SC_2_VERSION);
    sysconf_names->__setitem__(new str("SC_THREAD_DESTRUCTOR_ITERATIONS"), _SC_THREAD_DESTRUCTOR_ITERATIONS);
    sysconf_names->__setitem__(new str("SC_ASYNCHRONOUS_IO"), _SC_ASYNCHRONOUS_IO);
    sysconf_names->__setitem__(new str("SC_MESSAGE_PASSING"), _SC_MESSAGE_PASSING);
    sysconf_names->__setitem__(new str("SC_CHILD_MAX"), _SC_CHILD_MAX);
    sysconf_names->__setitem__(new str("SC_ULONG_MAX"), _SC_ULONG_MAX);
    sysconf_names->__setitem__(new str("SC_2_C_VERSION"), _SC_2_C_VERSION);
    sysconf_names->__setitem__(new str("SC_ARG_MAX"), _SC_ARG_MAX);
    sysconf_names->__setitem__(new str("SC_GETPW_R_SIZE_MAX"), _SC_GETPW_R_SIZE_MAX);
    sysconf_names->__setitem__(new str("SC_XOPEN_CRYPT"), _SC_XOPEN_CRYPT);
    sysconf_names->__setitem__(new str("SC_SCHAR_MIN"), _SC_SCHAR_MIN);
    sysconf_names->__setitem__(new str("SC_AIO_PRIO_DELTA_MAX"), _SC_AIO_PRIO_DELTA_MAX);
    sysconf_names->__setitem__(new str("SC_NL_LANGMAX"), _SC_NL_LANGMAX);
    sysconf_names->__setitem__(new str("SC_THREAD_STACK_MIN"), _SC_THREAD_STACK_MIN);
    sysconf_names->__setitem__(new str("SC_CHAR_MIN"), _SC_CHAR_MIN);
    sysconf_names->__setitem__(new str("SC_NL_TEXTMAX"), _SC_NL_TEXTMAX);
    sysconf_names->__setitem__(new str("SC_STREAM_MAX"), _SC_STREAM_MAX);
    sysconf_names->__setitem__(new str("SC_UIO_MAXIOV"), _SC_UIO_MAXIOV);
    sysconf_names->__setitem__(new str("SC_MEMLOCK"), _SC_MEMLOCK);
    sysconf_names->__setitem__(new str("SC_NZERO"), _SC_NZERO);
    sysconf_names->__setitem__(new str("SC_SHARED_MEMORY_OBJECTS"), _SC_SHARED_MEMORY_OBJECTS);
    sysconf_names->__setitem__(new str("SC_THREAD_THREADS_MAX"), _SC_THREAD_THREADS_MAX);
    sysconf_names->__setitem__(new str("SC_THREAD_ATTR_STACKADDR"), _SC_THREAD_ATTR_STACKADDR);
    sysconf_names->__setitem__(new str("SC_INT_MIN"), _SC_INT_MIN);
    sysconf_names->__setitem__(new str("SC_SHRT_MIN"), _SC_SHRT_MIN);
    sysconf_names->__setitem__(new str("SC_COLL_WEIGHTS_MAX"), _SC_COLL_WEIGHTS_MAX);
    sysconf_names->__setitem__(new str("SC_THREAD_PRIORITY_SCHEDULING"), _SC_THREAD_PRIORITY_SCHEDULING);
    sysconf_names->__setitem__(new str("SC_THREAD_ATTR_STACKSIZE"), _SC_THREAD_ATTR_STACKSIZE);
    sysconf_names->__setitem__(new str("SC_PHYS_PAGES"), _SC_PHYS_PAGES);
    sysconf_names->__setitem__(new str("SC_JOB_CONTROL"), _SC_JOB_CONTROL);
    sysconf_names->__setitem__(new str("SC_FSYNC"), _SC_FSYNC);
    sysconf_names->__setitem__(new str("SC_CHARCLASS_NAME_MAX"), _SC_CHARCLASS_NAME_MAX);
    sysconf_names->__setitem__(new str("SC_XOPEN_UNIX"), _SC_XOPEN_UNIX);
    sysconf_names->__setitem__(new str("SC_BC_DIM_MAX"), _SC_BC_DIM_MAX);
    sysconf_names->__setitem__(new str("SC_PII_INTERNET_STREAM"), _SC_PII_INTERNET_STREAM);
    sysconf_names->__setitem__(new str("SC_MB_LEN_MAX"), _SC_MB_LEN_MAX);
    sysconf_names->__setitem__(new str("SC_UINT_MAX"), _SC_UINT_MAX);
    sysconf_names->__setitem__(new str("SC_CHAR_BIT"), _SC_CHAR_BIT);
    sysconf_names->__setitem__(new str("SC_XOPEN_REALTIME"), _SC_XOPEN_REALTIME);
    sysconf_names->__setitem__(new str("SC_MQ_OPEN_MAX"), _SC_MQ_OPEN_MAX);
    sysconf_names->__setitem__(new str("SC_PII_OSI_M"), _SC_PII_OSI_M);
    sysconf_names->__setitem__(new str("SC_PRIORITY_SCHEDULING"), _SC_PRIORITY_SCHEDULING);
    sysconf_names->__setitem__(new str("SC_NGROUPS_MAX"), _SC_NGROUPS_MAX);
    sysconf_names->__setitem__(new str("SC_MQ_PRIO_MAX"), _SC_MQ_PRIO_MAX);
    sysconf_names->__setitem__(new str("SC_XBS5_LPBIG_OFFBIG"), _SC_XBS5_LPBIG_OFFBIG);
    sysconf_names->__setitem__(new str("SC_PII_SOCKET"), _SC_PII_SOCKET);
    sysconf_names->__setitem__(new str("SC_MAPPED_FILES"), _SC_MAPPED_FILES);
    sysconf_names->__setitem__(new str("SC_PII_INTERNET_DGRAM"), _SC_PII_INTERNET_DGRAM);
    sysconf_names->__setitem__(new str("SC_XBS5_LP64_OFF64"), _SC_XBS5_LP64_OFF64);
    sysconf_names->__setitem__(new str("SC_XOPEN_XCU_VERSION"), _SC_XOPEN_XCU_VERSION);
    sysconf_names->__setitem__(new str("SC_OPEN_MAX"), _SC_OPEN_MAX);
    sysconf_names->__setitem__(new str("SC_PRIORITIZED_IO"), _SC_PRIORITIZED_IO);
    sysconf_names->__setitem__(new str("SC_TTY_NAME_MAX"), _SC_TTY_NAME_MAX);
    sysconf_names->__setitem__(new str("SC_WORD_BIT"), _SC_WORD_BIT);
    sysconf_names->__setitem__(new str("SC_SYNCHRONIZED_IO"), _SC_SYNCHRONIZED_IO);
    sysconf_names->__setitem__(new str("SC_PASS_MAX"), _SC_PASS_MAX);
    sysconf_names->__setitem__(new str("SC_PII_INTERNET"), _SC_PII_INTERNET);
    sysconf_names->__setitem__(new str("SC_LINE_MAX"), _SC_LINE_MAX);
    sysconf_names->__setitem__(new str("SC_XBS5_ILP32_OFF32"), _SC_XBS5_ILP32_OFF32);
    sysconf_names->__setitem__(new str("SC_2_C_DEV"), _SC_2_C_DEV);
    sysconf_names->__setitem__(new str("SC_2_C_BIND"), _SC_2_C_BIND);
    sysconf_names->__setitem__(new str("SC_BC_STRING_MAX"), _SC_BC_STRING_MAX);
    sysconf_names->__setitem__(new str("SC_THREAD_PRIO_PROTECT"), _SC_THREAD_PRIO_PROTECT);
    sysconf_names->__setitem__(new str("SC_CHAR_MAX"), _SC_CHAR_MAX);
    sysconf_names->__setitem__(new str("SC_XBS5_ILP32_OFFBIG"), _SC_XBS5_ILP32_OFFBIG);
    sysconf_names->__setitem__(new str("SC_2_LOCALEDEF"), _SC_2_LOCALEDEF);
    sysconf_names->__setitem__(new str("SC_PII"), _SC_PII);
    sysconf_names->__setitem__(new str("SC_POLL"), _SC_POLL);
    sysconf_names->__setitem__(new str("SC_2_FORT_DEV"), _SC_2_FORT_DEV);
    sysconf_names->__setitem__(new str("SC_INT_MAX"), _SC_INT_MAX);
    sysconf_names->__setitem__(new str("SC_NPROCESSORS_CONF"), _SC_NPROCESSORS_CONF);
    sysconf_names->__setitem__(new str("SC_DELAYTIMER_MAX"), _SC_DELAYTIMER_MAX);
    sysconf_names->__setitem__(new str("SC_THREAD_SAFE_FUNCTIONS"), _SC_THREAD_SAFE_FUNCTIONS);
    sysconf_names->__setitem__(new str("SC_MEMLOCK_RANGE"), _SC_MEMLOCK_RANGE);
    sysconf_names->__setitem__(new str("SC_NL_MSGMAX"), _SC_NL_MSGMAX);
    sysconf_names->__setitem__(new str("SC_TIMERS"), _SC_TIMERS);
    sysconf_names->__setitem__(new str("SC_XOPEN_REALTIME_THREADS"), _SC_XOPEN_REALTIME_THREADS);
    sysconf_names->__setitem__(new str("SC_CLK_TCK"), _SC_CLK_TCK);

}

} // module namespace

