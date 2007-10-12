#include "os/path.hpp"

namespace __os__ {
namespace __path__ {

str *const_0, *const_1, *const_2;

void __init() {
    const_0 = new str("/");
    const_1 = new str(".");
    const_2 = new str("");

}

/**
Split a pathname.  Returns tuple "(head, tail)" where "tail" is
    everything after the final slash.  Either part may be empty.
*/
tuple2<str *, str *> *split(str *p) {
    str *__0, *__1, *head, *tail;
    int i;

    i = (p->rfind(const_0)+1);
    __0 = p->__slice__(2, 0, i, 0);
    __1 = p->__slice__(1, i, 0, 0);
    head = __0;
    tail = __1;
    if ((__bool(head) && (!__eq(head, (const_0)->__mul__(len(head)))))) {
        head = head->rstrip(const_0);
    }
    return (new tuple2<str *, str *>(2, head, tail));
}

/**
Split the extension from a pathname.  Extension is everything from the
    last dot to the end.  Returns "(root, ext)", either part may be empty.
*/
tuple2<str *, str *> *splitext(str *p) {
    int i;

    i = p->rfind(const_1);
    if ((i<=p->rfind(const_0))) {
        return (new tuple2<str *, str *>(2, p, const_2));
    }
    else {
        return (new tuple2<str *, str *>(2, p->__slice__(2, 0, i, 0), p->__slice__(1, i, 0, 0)));
    }
    return 0;
}

/**
Test whether a path is a directory
*/
int isdir(str *path) {
    __os__::__cstat *st;

    try {
        st = __os__::stat(path);
    } catch (OSError *__2) {
        return 0;
    }
    return __stat__::S_ISDIR(st->st_mode);
}

/**
Test whether a path exists.  Returns False for broken symbolic links
*/
int exists(str *path) {
    __os__::__cstat *st;

    try {
        st = __os__::stat(path);
    } catch (OSError *__3) {
        return 0;
    }
    return 1;
}

/**
Test whether a path is a symbolic link
*/
int islink(str *path) {
    __os__::__cstat *st;

    try {
        st = __os__::lstat(path);
    } catch (OSError *__4) {
        return 0;
    }
    return __stat__::S_ISLNK(st->st_mode);
}

/**
Test whether a path is a regular file
*/
int isfile(str *path) {
    __os__::__cstat *st;

    try {
        st = __os__::stat(path);
    } catch (OSError *__5) {
        return 0;
    }
    return __stat__::S_ISREG(st->st_mode);
}

} // module namespace
} // module namespace

