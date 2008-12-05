#include "__init__.hpp"
#include "path.hpp"

#include <cstdlib>
#include <sstream>
#include <sys/stat.h>
#include <stdio.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>

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
struct stat sbuf;

const int MAXENTRIES = 4096; /* XXX probably have to fix each function that uses this */

str *altsep, *curdir, *defpath, *devnull, *extsep, *pardir, *pathsep, *sep;

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
int getgid() { return ::getgid(); }
int geteuid() { return ::geteuid(); }
int getegid() { return ::getegid(); }
int getppid() { return ::getppid(); }

int fork() {
    int ret;
    if ((ret = ::fork()) == -1)
        throw new OSError(new str("os.fork"));
    return ret;
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

int getsid(int pid) {
    int nr = ::getsid(pid);
    if(nr == -1)
        throw new OSError(new str("os.getsid"));
    return nr;
}

int getpgid(int pid) {
    int nr = ::getpgid(pid);
    if(nr == -1)
        throw new OSError(new str("os.getpgid"));
    return nr;
}

int getpgrp() {
    return getpgid(0);
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

}

} // module namespace

