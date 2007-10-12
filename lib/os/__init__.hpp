#ifndef __OS_HPP
#define __OS_HPP

#include "builtin.hpp"


using namespace __shedskin__;
namespace __os__ {

list<str *> *listdir(str *path);

str *_getcwd();
int _chdir(str *dir);
str *getenv(str *name, str *alternative=0);
int rename(str *a, str *b);
int system(str *c);

class __cstat;

extern class_ *cl___cstat;
class __cstat : public pyobj {
public:
    int st_mode, st_ino, st_dev, st_rdev, st_nlink, st_uid, st_gid, st_size, st_blksize, st_blocks;
    int hop1, hop2, hop3;

    __cstat(str *path, int t);
    str *__repr__();
};

__cstat *stat(str *path);
__cstat *lstat(str *path);

void __init();

} // module namespace
#endif
