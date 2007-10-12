#include "__init__.hpp"

#include <cstdlib>
#include <sys/stat.h>
#include <stdio.h>
#include <dirent.h>

namespace std {
#include <unistd.h>
}

namespace __os__ {

str *const_0;
struct stat sbuf;

list<str *> *listdir(str *path) {
    list<str *> *r = new list<str *>();
    DIR *dp;
    struct dirent *ep;
    int count = 0;

    dp = opendir(path->unit.c_str());

    while (ep = readdir(dp))
        if(++count > 2) 
            r->append(new str(ep->d_name));

    closedir (dp);
    return r;
}

str *_getcwd() {
    str *r;
    char *d=getcwd(0, 0);
    r = new str(d);
    free(d);
    return r;
}

int _chdir(str *dir) {
    if(chdir(dir->unit.c_str()) == -1)
        throw new OSError(new str("no such directory"));
    return 0;
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

int rename(str *a, str *b) {
    if(std::rename(a->unit.c_str(), b->unit.c_str()) == -1)
        throw new OSError(new str("could not rename file"));
}

/* class __cstat */

class_ *cl___cstat;

__cstat::__cstat(str *path, int t) {
    int hop;
    this->__class__ = cl___cstat;
    
    if(t==1) {
        if(stat(path->unit.c_str(), &sbuf) == -1)
            throw new OSError(new str("file does not exist"));
    } else if (t==2) {
#ifndef WIN32
        if(lstat(path->unit.c_str(), &sbuf) == -1)
#endif
            throw new OSError(new str("link does not exist"));
    }
    
    this->st_mode = sbuf.st_mode;
    this->st_ino = sbuf.st_ino;
    this->st_dev = sbuf.st_dev;
    this->st_rdev = sbuf.st_rdev;
    this->st_nlink = sbuf.st_nlink;
    this->hop1 = sbuf.st_atime;
    this->hop2 = sbuf.st_mtime;
    this->hop3 = sbuf.st_ctime;
    this->st_uid = sbuf.st_uid;
    this->st_gid = sbuf.st_gid;
    this->st_size = sbuf.st_size;
#ifndef WIN32
    this->st_blksize = sbuf.st_blksize;
    this->st_blocks = sbuf.st_blocks;
#endif
}

str *__cstat::__repr__() {
    return __mod(const_0, this->st_mode, this->st_ino, this->st_dev, this->st_nlink, this->st_uid, this->st_gid, this->st_size, this->hop1, this->hop2, this->hop3);
}

__cstat *stat(str *path) {
    return new __cstat(path, 1);
}
__cstat *lstat(str *path) {
    return new __cstat(path, 2);
}

void __init() {
    const_0 = new str("(%d, %d, %d, %d, %d, %d, %d, %d, %d, %d)");

    cl___cstat = new class_("__cstat", 4, 4);

}

} // module namespace

