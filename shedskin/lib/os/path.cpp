#include "os/path.hpp"

/* converted using Shed Skin from the CPython implementation */

/**
Common operations on Posix pathnames.

Instead of importing this module directly, import os and refer to
this module as os.path.  The "os.path" name is an alias for this
module on Posix systems; on other systems (e.g. Mac, Windows),
os.path provides the same operations in a manner specific to that
platform, and is an alias to another module (e.g. macpath, ntpath).

Some of this can actually be useful on non-Posix systems too, e.g.
for manipulation of the pathname component of URLs.
*/

namespace __os__ {
namespace __path__ {

tuple2<str *, str *> *const_2;
str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;
str *__name__, *altsep, *curdir, *defpath, *devnull, *extsep, *pardir, *pathsep, *sep;
#ifdef WIN32
__ss_int supports_unicode_filenames;
#endif

str *join(__ss_int n, ...) { /* varargs hack */
    list<str *> *p = new list<str *>();
    va_list ap;
    va_start(ap, n);
    for(__ss_int i=0; i<n; i++) {
        str *t = va_arg(ap, str *);
        p->append(t);
    }
    va_end(ap);

    return joinl(p);
}

#ifndef WIN32
void __init() {
    const_0 = new str("");
    const_1 = new str(".");
    const_2 = (new tuple2<str *, str *>(2, const_0, const_1));
    const_3 = new str("..");
    const_4 = new str("/");
    const_5 = new str(":");
    const_6 = new str(":/bin:/usr/bin");
    const_7 = new str("/dev/null");
    const_14 = new str("//");
    const_15 = new str("///");

    __name__ = new str("__main__");

    curdir = const_1;
    pardir = const_3;
    extsep = const_1;
    sep = const_4;
    pathsep = const_5;
    defpath = const_6;
    altsep = const_0;
    devnull = const_7;
}

str *normcase(str *s) {
    /**
    Normalize case of pathname.  Has no effect under Posix
    */

    return s;
}

__ss_bool isabs(str *s) {
    /**
    Test whether a path is absolute
    */

    return __mbool(s->startswith(const_4));
}

str *joinl(list<str *> *l) {
    /**
    Join two or more pathname components, inserting '/' as needed
    */
    list<str *> *__1, *__2, *p;
    str *__0, *b, *path;
    __ss_int __4, __5;

    __0 = l->__getfast__(0);
    __1 = l->__slice__(1, 1, 0, 0);
    path = __0;
    p = __1;

    FOR_IN_SEQ(b,p,2,4)
        if (b->startswith(const_4)) {
            path = b;
        }
        else if (__OR(__eq(path, const_0), path->endswith(const_4), 5)) {
            path = path->__iadd__(b);
        }
        else {
            path = __add_strs(3, path, const_4, b);
        }
    END_FOR

    return path;
}

tuple2<str *, str *> *split(str *p) {
    /**
    Split a pathname.  Returns tuple "(head, tail)" where "tail" is
    everything after the final slash.  Either part may be empty.
    */
    str *__7, *__8, *head, *tail;
    __ss_int i;

    i = (p->rfind(const_4)+1);
    __7 = p->__slice__(2, 0, i, 0);
    __8 = p->__slice__(1, i, 0, 0);
    head = __7;
    tail = __8;
    if ((___bool(head) && __ne(head, (const_4)->__mul__(len(head))))) {
        head = head->rstrip(const_4);
    }
    return (new tuple2<str *, str *>(2, head, tail));
}

tuple2<str *, str *> *splitext(str *p) {
    /**
    Split the extension from a pathname.  Extension is everything from the
    last dot to the end.  Returns "(root, ext)", either part may be empty.
    */
    __ss_int i;

    i = p->rfind(const_1);
    if ((i<=p->rfind(const_4))) {
        return (new tuple2<str *, str *>(2, p, const_0));
    }
    else {
        return (new tuple2<str *, str *>(2, p->__slice__(2, 0, i, 0), p->__slice__(1, i, 0, 0)));
    }
    return 0;
}

tuple2<str *, str *> *splitdrive(str *p) {
    /**
    Split a pathname into drive and path. On Posix, drive is always
    empty.
    */

    return (new tuple2<str *, str *>(2, const_0, p));
}

str *basename(str *p) {
    /**
    Returns the final component of a pathname
    */

    return (split(p))->__getsecond__();
}

str *dirname(str *p) {
    /**
    Returns the directory component of a pathname
    */

    return (split(p))->__getfirst__();
}

str *commonprefix(list<str *> *m) {
    /**
    Given a list of pathnames, returns the longest common leading component
    */
    str *s1, *s2;
    __ss_int __11, __12, i, n;

    if ((!___bool(m))) {
        return const_0;
    }
    s1 = ___min(1, 0, m);
    s2 = ___max(1, 0, m);
    n = ___min(2, 0, len(s1), len(s2));

    FAST_FOR(i,0,n,1,11,12)
        if (__ne(s1->__getitem__(i), s2->__getitem__(i))) {
            return s1->__slice__(2, 0, i, 0);
        }
    END_FOR

    return s1->__slice__(2, 0, n, 0);
}

__ss_int getsize(str *filename) {
    /**
    Return the size of a file, reported by os.stat().
    */

    return (__os__::stat(filename))->st_size;
}

double getmtime(str *filename) {
    /**
    Return the last modification time of a file, reported by os.stat().
    */

    return (__os__::stat(filename))->__ss_st_mtime;
}

double getatime(str *filename) {
    /**
    Return the last access time of a file, reported by os.stat().
    */

    return (__os__::stat(filename))->__ss_st_atime;
}

double getctime(str *filename) {
    /**
    Return the metadata change time of a file, reported by os.stat().
    */

    return (__os__::stat(filename))->__ss_st_ctime;
}

__ss_bool islink(str *path) {
    /**
    Test whether a path is a symbolic link
    */
    __os__::__cstat *st;

    try {
        st = __os__::lstat(path);
    } catch (__os__::error *) {
        return False;
    }
    return __mbool(__stat__::__ss_S_ISLNK(st->st_mode));
}

__ss_bool exists(str *path) {
    /**
    Test whether a path exists.  Returns False for broken symbolic links
    */
    __os__::__cstat *st;

    try {
        st = __os__::stat(path);
    } catch (__os__::error *) {
        return False;
    }
    return True;
}

__ss_bool lexists(str *path) {
    /**
    Test whether a path exists.  Returns True for broken symbolic links
    */
    __os__::__cstat *st;

    try {
        st = __os__::lstat(path);
    } catch (__os__::error *) {
        return False;
    }
    return True;
}

__ss_bool isdir(str *path) {
    /**
    Test whether a path is a directory
    */
    __os__::__cstat *st;

    try {
        st = __os__::stat(path);
    } catch (__os__::error *) {
        return False;
    }
    return __mbool(__stat__::__ss_S_ISDIR(st->st_mode));
}

__ss_bool isfile(str *path) {
    /**
    Test whether a path is a regular file
    */
    __os__::__cstat *st;

    try {
        st = __os__::stat(path);
    } catch (__os__::error *) {
        return False;
    }
    return __mbool(__stat__::__ss_S_ISREG(st->st_mode));
}

__ss_bool samefile(str *f1, str *f2) {
    /**
    Test whether two pathnames reference the same actual file
    */
    __os__::__cstat *s1, *s2;

    s1 = __os__::stat(f1);
    s2 = __os__::stat(f2);
    return __mbool(samestat(s1, s2));
}

__ss_bool samestat(__os__::__cstat *s1, __os__::__cstat *s2) {
    /**
    Test whether two stat buffers reference the same file
    */
    __ss_int __18;
    return __mbool(__AND((s1->st_ino==s2->st_ino), (s1->st_dev==s2->st_dev), 18));
}

str *normpath(str *path) {
    /**
    Normalize path, eliminating double slashes, etc.
    */
    list<str *> *__28, *comps, *new_comps;
    str *__38, *comp;
    __ss_int __25, __26, __30, __32, initial_slashes;

    if (__eq(path, const_0)) {
        return const_1;
    }
    initial_slashes = path->startswith(const_4);
    if (__AND(initial_slashes, __AND(path->startswith(const_14), (!path->startswith(const_15)), 26), 25)) {
        initial_slashes = 2;
    }
    comps = path->split(const_4);
    new_comps = (new list<str *>());

    FOR_IN_SEQ(comp,comps,28,30)
        if ((const_2)->__contains__(comp)) {
            continue;
        }
        if ((__ne(comp, const_3) || __AND((!initial_slashes), (!___bool(new_comps)), 32) || ___bool((___bool(new_comps) && __eq(new_comps->__getfast__(-1), const_3))))) {
            new_comps->append(comp);
        }
        else if (___bool(new_comps)) {
            new_comps->pop();
        }
    END_FOR

    comps = new_comps;
    path = (const_4)->join(comps);
    if (initial_slashes) {
        path = ((const_4)->__mul__(initial_slashes))->__add__(path);
    }
    return __OR(path, const_1, 38);
}

str *abspath(str *path) {
    /**
    Return an absolute path.
    */

    if ((!isabs(path))) {
        path = join(2, __os__::getcwd(), path);
    }
    return normpath(path);
}

str *realpath(str *filename) {
    /**
    Return the canonical path of the specified filename, eliminating any
    symbolic links encountered in the path.
    */
    list<str *> *bits;
    str *component, *newpath, *resolved;
    __ss_int __40, __41, i;

    if (isabs(filename)) {
        bits = ((new list<str *>(1, const_4)))->__add__((filename->split(const_4))->__slice__(1, 1, 0, 0));
    }
    else {
        bits = filename->split(const_4);
    }

    FAST_FOR(i,2,(len(bits)+1),1,40,41)
        component = joinl(bits->__slice__(3, 0, i, 0));
        if (islink(component)) {
            resolved = _resolve_link(component);
            if ((resolved==0)) {
                return abspath(joinl(((new list<str *>(1, component)))->__add__(bits->__slice__(1, i, 0, 0))));
            }
            else {
                newpath = joinl(((new list<str *>(1, resolved)))->__add__(bits->__slice__(1, i, 0, 0)));
                return realpath(newpath);
            }
        }
    END_FOR

    return abspath(filename);
}

str *_resolve_link(str *path) {
    /**
    Internal helper function.  Takes a path and follows symlinks
    until we either arrive at something that isn't a symlink, or
    encounter a path we've seen before (meaning that there's a loop).
    */
    list<str *> *paths_seen;
    str *dir, *resolved;

    paths_seen = (new list<str *>());

    while(islink(path)) {
        if (paths_seen->__contains__(path)) {
            return 0;
        }
        paths_seen->append(path);
        resolved = __os__::readlink(path);
        if ((!isabs(resolved))) {
            dir = dirname(path);
            path = normpath(join(2, dir, resolved));
        }
        else {
            path = normpath(resolved);
        }
    }
    return path;
}
#else
void __init() {
    const_0 = new str(".");
    const_1 = new str("");
    const_2 = (new tuple2<str *, str *>(2, const_0, const_1));
    const_3 = new str("..");
    const_4 = new str("\\");
    const_5 = new str(";");
    const_6 = new str("/");
    const_7 = new str(".;C:\\bin");
    const_8 = new str("nul");
    const_18 = new str("/\\");
    const_19 = new str(":");

    __name__ = new str("__main__");

    curdir = const_0;
    pardir = const_3;
    extsep = const_0;
    sep = const_4;
    pathsep = const_5;
    altsep = const_6;
    defpath = const_7;
    devnull = const_8;
    supports_unicode_filenames = 0;
}

str *normcase(str *s) {
    /**
    Normalize case of pathname.

    Makes all characters lowercase and all slashes into backslashes.
    */

    return (s->replace(const_6, const_4))->lower();
}

__ss_bool isabs(str *s) {
    /**
    Test whether a path is absolute
    */
    __ss_int __0, __1;

    s = (splitdrive(s))->__getsecond__();
    return __mbool(__AND(__ne(s, const_1), (const_18)->__contains__(s->__slice__(2, 0, 1, 0)), 0));
}

str *joinl(list<str *> *l) {
    /**
    Join two or more pathname components, inserting "\" as needed
    */
    list<str *> *__3, *__4, *p;
    __iter<str *> *__5;
    str *__2, *b, *path;
    __ss_int __10, __11, __12, __13, __14, __6, __7, __8, __9, b_wins;

    __2 = l->__getfast__(0);
    __3 = l->__slice__(1, 1, 0, 0);
    path = __2;
    p = __3;

    FOR_IN_SEQ(b,p,4,6)
        b_wins = 0;
        if (__eq(path, const_1)) {
            b_wins = 1;
        }
        else if (isabs(b)) {
            if (__OR(__ne(path->__slice__(3, 1, 2, 0), const_19), __eq(b->__slice__(3, 1, 2, 0), const_19), 7)) {
                b_wins = 1;
            }
            else if (__OR((len(path)>3), __AND((len(path)==3), (!(const_18)->__contains__(path->__getitem__(-1))), 10), 9)) {
                b_wins = 1;
            }
        }
        if (b_wins) {
            path = b;
        }
        else {
            ASSERT((len(path)>0), 0);
            if ((const_18)->__contains__(path->__getitem__(-1))) {
                if ((___bool(b) && (const_18)->__contains__(b->__getitem__(0)))) {
                    path = path->__iadd__(b->__slice__(1, 1, 0, 0));
                }
                else {
                    path = path->__iadd__(b);
                }
            }
            else if (__eq(path->__getitem__(-1), const_19)) {
                path = path->__iadd__(b);
            }
            else if (___bool(b)) {
                if ((const_18)->__contains__(b->__getitem__(0))) {
                    path = path->__iadd__(b);
                }
                else {
                    path = __add_strs(3, path, const_4, b);
                }
            }
            else {
                path = path->__iadd__(const_4);
            }
        }
    END_FOR

    return path;
}

tuple2<str *, str *> *splitdrive(str *p) {
    /**
    Split a pathname into drive and path specifiers. Returns a 2-tuple
    "(drive,path)";  either part may be empty
    */

    if (__eq(p->__slice__(3, 1, 2, 0), const_19)) {
        return (new tuple2<str *, str *>(2, p->__slice__(3, 0, 2, 0), p->__slice__(1, 2, 0, 0)));
    }
    return (new tuple2<str *, str *>(2, const_1, p));
}

tuple2<str *, str *> *split(str *p) {
    /**
    Split a pathname.

    Return tuple (head, tail) where tail is everything after the final slash.
    Either part may be empty.
    */
    tuple2<str *, str *> *__15;
    str *__18, *__19, *__22, *__23, *d, *head, *head2, *tail;
    __ss_int __16, __17, __20, __21, i;

    __15 = splitdrive(p);
    d = __15->__getfirst__();
    p = __15->__getsecond__();
    i = len(p);

    while(__AND(i, (!(const_18)->__contains__(p->__getitem__((i-1)))), 16)) {
        i = (i-1);
    }
    __18 = p->__slice__(2, 0, i, 0);
    __19 = p->__slice__(1, i, 0, 0);
    head = __18;
    tail = __19;
    head2 = head;

    while((___bool(head2) && (const_18)->__contains__(head2->__getitem__(-1)))) {
        head2 = head2->__slice__(2, 0, -1, 0);
    }
    head = __OR(head2, head, 22);
    return (new tuple2<str *, str *>(2, d->__add__(head), tail));
}

tuple2<str *, str *> *splitext(str *p) {
    /**
    Split the extension from a pathname.

    Extension is everything from the last dot to the end.
    Return (root, ext), either part may be empty.
    */
    __ss_int i;

    i = p->rfind(const_0);
    if ((i<=___max(2, 0, p->rfind(const_6), p->rfind(const_4)))) {
        return (new tuple2<str *, str *>(2, p, const_1));
    }
    else {
        return (new tuple2<str *, str *>(2, p->__slice__(2, 0, i, 0), p->__slice__(1, i, 0, 0)));
    }
    return 0;
}

str *basename(str *p) {
    /**
    Returns the final component of a pathname
    */

    return (split(p))->__getsecond__();
}

str *dirname(str *p) {
    /**
    Returns the directory component of a pathname
    */

    return (split(p))->__getfirst__();
}

str *commonprefix(list<str *> *m) {
    /**
    Given a list of pathnames, returns the longest common leading component
    */
    list<str *> *__24;
    __iter<str *> *__25;
    __ss_int __26, __27, __28, i;
    str *item, *prefix;

    if ((!___bool(m))) {
        return const_1;
    }
    prefix = m->__getfast__(0);

    FOR_IN_SEQ(item,m,24,26)

        FAST_FOR(i,0,len(prefix),1,27,28)
            if (__ne(prefix->__slice__(2, 0, (i+1), 0), item->__slice__(2, 0, (i+1), 0))) {
                prefix = prefix->__slice__(2, 0, i, 0);
                if ((i==0)) {
                    return const_1;
                }
                break;
            }
        END_FOR

    END_FOR

    return prefix;
}

__ss_int getsize(str *filename) {
    /**
    Return the size of a file, reported by os.stat()
    */

    return (__os__::stat(filename))->st_size;
}

double getmtime(str *filename) {
    /**
    Return the last modification time of a file, reported by os.stat()
    */

    return (__os__::stat(filename))->__ss_st_mtime;
}

double getatime(str *filename) {
    /**
    Return the last access time of a file, reported by os.stat()
    */

    return (__os__::stat(filename))->__ss_st_atime;
}

double getctime(str *filename) {
    /**
    Return the creation time of a file, reported by os.stat().
    */

    return (__os__::stat(filename))->__ss_st_ctime;
}

__ss_bool islink(str *path) {
    /**
    Test for symbolic link.  On WindowsNT/95 always returns false
    */

    return False;
}

__ss_bool exists(str *path) {
    /**
    Test whether a path exists
    */
    __os__::__cstat *st;

    try {
        st = __os__::stat(path);
    } catch (__os__::error *) {
        return False;
    }
    return True;
}

__ss_bool lexists(str *path) {
    return exists(path);
}

__ss_bool isdir(str *path) {
    /**
    Test whether a path is a directory
    */
    __os__::__cstat *st;

    try {
        st = __os__::stat(path);
    } catch (__os__::error *) {
        return False;
    }
    return __mbool(__stat__::__ss_S_ISDIR(st->st_mode));
}

__ss_bool isfile(str *path) {
    /**
    Test whether a path is a regular file
    */
    __os__::__cstat *st;

    try {
        st = __os__::stat(path);
    } catch (__os__::error *) {
        return False;
    }
    return __mbool(__stat__::__ss_S_ISREG(st->st_mode));
}

str *normpath(str *path) {
    /**
    Normalize path, eliminating double slashes, etc.
    */
    tuple2<str *, str *> *__36;
    list<str *> *comps;
    str *prefix;
    __ss_int __37, __38, __39, __40, __41, __42, i;

    path = path->replace(const_6, const_4);
    __36 = splitdrive(path);
    prefix = __36->__getfirst__();
    path = __36->__getsecond__();
    if (__eq(prefix, const_1)) {

        while(__eq(path->__slice__(2, 0, 1, 0), const_4)) {
            prefix = prefix->__add__(const_4);
            path = path->__slice__(1, 1, 0, 0);
        }
    }
    else {
        if (path->startswith(const_4)) {
            prefix = prefix->__add__(const_4);
            path = path->lstrip(const_4);
        }
    }
    comps = path->split(const_4);
    i = 0;

    while((i<len(comps))) {
        if ((const_2)->__contains__(comps->__getfast__(i))) {
            comps->__delitem__(i);
        }
        else if (__eq(comps->__getfast__(i), const_3)) {
            if (__AND((i>0), __ne(comps->__getfast__((i-1)), const_3), 37)) {
                comps->__delete__(3, (i-1), (i+1), 0);
                i = (i-1);
            }
            else if (__AND((i==0), prefix->endswith(const_4), 39)) {
                comps->__delitem__(i);
            }
            else {
                i = (i+1);
            }
        }
        else {
            i = (i+1);
        }
    }
    if (__AND((!___bool(prefix)), (!___bool(comps)), 41)) {
        comps->append(const_0);
    }
    return prefix->__add__((const_4)->join(comps));
}

str *abspath(str *path) {
    /**
    Return an absolute path.
    */

    if ((!isabs(path))) {
        path = join(2, __os__::getcwd(), path);
    }
    return normpath(path);
}

str *realpath(str *path) {

    return abspath(path);
}

#endif

} // module namespace
} // module namespace

