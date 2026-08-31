/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "os/path.hpp"

#ifndef WIN32
#include <pwd.h>
#else
#ifdef _MSC_VER
#ifndef NOMINMAX
#define NOMINMAX
#endif
#endif
#include <windows.h>
#endif

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
str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;
str *__name__, *altsep, *curdir, *defpath, *devnull, *extsep, *pardir, *pathsep, *sep;
#ifdef WIN32
__ss_int supports_unicode_filenames;
#endif

#ifndef WIN32
void __init() {
    const_0 = new str("");
    const_1 = new str(".");
    const_2 = (new tuple2<str *, str *>(2, const_0, const_1));
    const_3 = new str("..");
    const_4 = new str("/");
    const_5 = new str(":");
    const_6 = new str("/bin:/usr/bin");
    const_7 = new str("/dev/null");
    const_14 = new str("//");
    const_15 = new str("///");
    const_20 = new str("~");
    const_21 = new str("HOME");

    __name__ = new str("__main__");

    curdir = const_1;
    pardir = const_3;
    extsep = const_1;
    sep = const_4;
    pathsep = const_5;
    defpath = const_6;
    altsep = NULL;
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
    list<str *>::for_in_loop __123;
    str *__0, *b, *path;
    __ss_int __4, __5;

    __0 = l->__getfast__(0);
    __1 = l->__slice__(1, 1, 0, 0);
    path = __0;
    p = __1;

    FOR_IN(b,p,2,4,123)
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

    Leading dots on the basename are skipped, so dotfiles like ".cshrc"
    are not treated as having an extension.
    */
    __ss_int sep_index, dot_index, filename_index;

    sep_index = p->rfind(const_4);
    dot_index = p->rfind(const_1);
    if (dot_index > sep_index) {
        filename_index = sep_index + 1;
        while (filename_index < dot_index) {
            if (__ne(p->__getitem__(filename_index), const_1)) {
                return (new tuple2<str *, str *>(2, p->__slice__(2, 0, dot_index, 0), p->__slice__(1, dot_index, 0, 0)));
            }
            filename_index++;
        }
    }
    return (new tuple2<str *, str *>(2, p, const_0));
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

bytes *basename(bytes *p) {
    /**
    Returns the final component of a pathname
    */

    return new bytes(basename(new str(p->unit))->unit);
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
    s1 = ___min(1, __ss_void, 0, m);
    s2 = ___max(1, __ss_void, 0, m);
    n = ___min(2, __ss_void, 0, len(s1), len(s2));

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
    try {
        __os__::stat(path);
    } catch (__os__::error *) {
        return False;
    }
    return True;
}

__ss_bool lexists(str *path) {
    /**
    Test whether a path exists.  Returns True for broken symbolic links
    */

    try {
        __os__::lstat(path);
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

__ss_bool ismount(str *path) {
    /**
    Test whether a path is a mount point
    */
    __os__::__cstat *s1, *s2;
    str *parent;

    try {
        s1 = __os__::lstat(path);
    } catch (__os__::error *) {
        return False;
    }
    if (__stat__::__ss_S_ISLNK(s1->st_mode)) {
        return False; /* A symlink can never be a mount point */
    }

    parent = join(2, path, pardir);
    try {
        parent = realpath(parent);
    } catch (__os__::error *) {
        return False;
    }
    try {
        s2 = __os__::lstat(parent);
    } catch (__os__::error *) {
        return False;
    }

    if (s1->st_dev != s2->st_dev) {
        return True; /* path/.. on a different device as path */
    }
    if (s1->st_ino == s2->st_ino) {
        return True; /* path/.. is the same i-node as path */
    }
    return False;
}

str *normpath(str *path) {
    /**
    Normalize path, eliminating double slashes, etc.
    */
    list<str *> *__28, *comps, *new_comps;
    list<str *>::for_in_loop __123;
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

    FOR_IN(comp,comps,28,30,123)
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

str *relpath(str *path, str *start) {
    /**
    Return a relative version of a path
    */
    list<str *> *__50, *start_list, *path_list, *rel_list;
    list<str *>::for_in_loop __123;
    str *start_abs, *path_abs, *part;
    __ss_int __51, i, n, j;

    if (!start) {
        start = curdir;
    }

    if ((!___bool(path))) {
        throw new ValueError(new str("no path specified"));
    }

    start_abs = abspath(start);
    path_abs = abspath(path);

    start_list = new list<str *>();
    FOR_IN(part,start_abs->split(const_4),50,51,123)
        if (___bool(part)) {
            start_list->append(part);
        }
    END_FOR

    path_list = new list<str *>();
    FOR_IN(part,path_abs->split(const_4),50,51,123)
        if (___bool(part)) {
            path_list->append(part);
        }
    END_FOR

    n = ___min(2, __ss_void, 0, len(start_list), len(path_list));
    i = 0;
    while ((i < n) && __eq(start_list->__getfast__(i), path_list->__getfast__(i))) {
        i++;
    }

    rel_list = new list<str *>();
    for (j = i; j < len(start_list); j++) {
        rel_list->append(const_3);
    }
    for (j = i; j < len(path_list); j++) {
        rel_list->append(path_list->__getfast__(j));
    }

    if ((!___bool(rel_list))) {
        return const_1;
    }
    return joinl(rel_list);
}

str *realpath(str *filename, __ss_bool strict) {
    /**
    Return the canonical path of the specified filename, eliminating any
    symbolic links encountered in the path. If strict is true, raise
    FileNotFoundError for the first path component that does not exist.

    Note: this is a lighter-weight approximation of CPython's strict mode:
    a broken symlink's *target* is not specially detected as missing, only
    path components that don't exist as a direct directory entry.
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
        if (strict.value && (!lexists(component).value)) {
            throw new FileNotFoundError(component);
        }
        if (islink(component)) {
            resolved = _resolve_link(component);
            if (resolved==0) {
                return abspath(joinl(((new list<str *>(1, component)))->__add__(bits->__slice__(1, i, 0, 0))));
            }
            else {
                newpath = joinl(((new list<str *>(1, resolved)))->__add__(bits->__slice__(1, i, 0, 0)));
                return realpath(newpath, strict);
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

str *expanduser(str *path) {
    /**
    Expand ~ and ~user constructions.  If user or $HOME is unknown,
    do nothing.
    */
    str *userhome, *result;
    __ss_int i;

    if (!path->startswith(const_20))
        return path;

    i = path->find(const_4, 1);
    if (i < 0)
        i = len(path);

    if (i != 1) {
        /* ~user: look up the user's home directory via getpwnam() */
        str *username = path->__slice__(3, 1, i, 0);
        struct passwd *pw = getpwnam(username->c_str());
        if (!pw)
            return path;
        userhome = new str(pw->pw_dir);
    } else {
        userhome = __os__::getenv(const_21);
        if (!userhome)
            return path;
    }

    userhome = userhome->rstrip(const_4);
    result = userhome->__add__(path->__slice__(1, i, 0, 0));
    if (!len(result))
        return const_4;
    return result;
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
    const_20 = new str("~");
    const_21 = new str("USERPROFILE");
    const_23 = new str("HOMEPATH");
    const_24 = new str("HOMEDRIVE");
    const_25 = new str("USERNAME");

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
    list<str *>::for_in_loop __123;
    __iter<str *> *__5;
    str *__2, *b, *path;
    __ss_int __10, __11, __12, __13, __14, __6, __7, __8, __9, b_wins;

    __2 = l->__getfast__(0);
    __3 = l->__slice__(1, 1, 0, 0);
    path = __2;
    p = __3;

    FOR_IN(b,p,4,6,123)
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

    Leading dots on the basename are skipped, so dotfiles like ".cshrc"
    are not treated as having an extension.
    */
    __ss_int sep_index, dot_index, filename_index;

    sep_index = ___max(2, __ss_void, 0, p->rfind(const_6), p->rfind(const_4));
    dot_index = p->rfind(const_0);
    if (dot_index > sep_index) {
        filename_index = sep_index + 1;
        while (filename_index < dot_index) {
            if (__ne(p->__getitem__(filename_index), const_0)) {
                return (new tuple2<str *, str *>(2, p->__slice__(2, 0, dot_index, 0), p->__slice__(1, dot_index, 0, 0)));
            }
            filename_index++;
        }
    }
    return (new tuple2<str *, str *>(2, p, const_1));
}

str *basename(str *p) {
    /**
    Returns the final component of a pathname
    */

    return (split(p))->__getsecond__();
}

bytes *basename(bytes *p) {
    /**
    Returns the final component of a pathname
    */

    return new bytes(basename(new str(p->unit))->unit);
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
    list<str *>::for_in_loop __123;
    __ss_int __26, __27, __28, i;
    str *item, *prefix;

    if ((!___bool(m))) {
        return const_1;
    }
    prefix = m->__getfast__(0);

    FOR_IN(item,m,24,26,123)

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

__ss_bool samefile(str *f1, str *f2) {
    /**
    Test whether two pathnames reference the same actual file.

    Windows' C runtime stat() does not reliably fill in st_ino/st_dev,
    so identity is determined directly via the Win32 API instead of
    going through samestat().
    */
    HANDLE h1, h2;
    BY_HANDLE_FILE_INFORMATION info1, info2;
    __ss_bool result;

    h1 = CreateFileA(f1->c_str(), 0, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                      NULL, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, NULL);
    if (h1 == INVALID_HANDLE_VALUE) {
        throw new OSError(f1);
    }

    h2 = CreateFileA(f2->c_str(), 0, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                      NULL, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, NULL);
    if (h2 == INVALID_HANDLE_VALUE) {
        CloseHandle(h1);
        throw new OSError(f2);
    }

    result = False;
    if (GetFileInformationByHandle(h1, &info1) && GetFileInformationByHandle(h2, &info2)) {
        result = __mbool((info1.dwVolumeSerialNumber == info2.dwVolumeSerialNumber) &&
                          (info1.nFileIndexHigh == info2.nFileIndexHigh) &&
                          (info1.nFileIndexLow == info2.nFileIndexLow));
    }

    CloseHandle(h1);
    CloseHandle(h2);
    return result;
}

__ss_bool samestat(__os__::__cstat *s1, __os__::__cstat *s2) {
    /**
    Test whether two stat buffers reference the same file
    */
    __ss_int __18;
    return __mbool(__AND((s1->st_ino==s2->st_ino), (s1->st_dev==s2->st_dev), 18));
}

__ss_bool ismount(str *path) {
    /**
    Test whether a path is a mount point (a drive root or a UNC share root)
    */
    tuple2<str *, str *> *__sd;
    str *root, *rest, *x, *y;
    char volpath[MAX_PATH];

    path = abspath(path);
    __sd = splitdrive(path);
    root = __sd->__getfirst__();
    rest = __sd->__getsecond__();

    if (___bool(root) && (const_18)->__contains__(root->__slice__(2, 0, 1, 0))) {
        /* UNC root, e.g. \\server\share */
        return __mbool((!___bool(rest)) || ((len(rest)==1) && (const_18)->__contains__(rest)));
    }
    if ((len(rest)==1) && (const_18)->__contains__(rest)) {
        /* drive root, e.g. C:\ */
        return True;
    }

    if (!GetVolumePathNameA(path->c_str(), volpath, MAX_PATH)) {
        return False;
    }
    x = path->rstrip(const_4);
    y = (new str(volpath))->rstrip(const_4);
    return __mbool(__eq(x, y));
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

str *relpath(str *path, str *start) {
    /**
    Return a relative version of a path
    */
    tuple2<str *, str *> *__60, *__61;
    list<str *> *__62, *start_list, *path_list, *rel_list;
    list<str *>::for_in_loop __123;
    str *start_abs, *path_abs, *start_drive, *start_rest, *path_drive, *path_rest, *part;
    __ss_int __63, i, n, j;

    if (!start) {
        start = curdir;
    }

    if ((!___bool(path))) {
        throw new ValueError(new str("no path specified"));
    }

    start_abs = abspath(start);
    path_abs = abspath(path);

    __60 = splitdrive(start_abs);
    start_drive = __60->__getfirst__();
    start_rest = __60->__getsecond__();
    __61 = splitdrive(path_abs);
    path_drive = __61->__getfirst__();
    path_rest = __61->__getsecond__();

    if (__ne(normcase(start_drive), normcase(path_drive))) {
        throw new ValueError(__add_strs(4, new str("path is on mount "), path_drive, new str(", start on mount "), start_drive));
    }

    start_list = new list<str *>();
    FOR_IN(part,start_rest->split(const_4),62,63,123)
        if (___bool(part)) {
            start_list->append(part);
        }
    END_FOR

    path_list = new list<str *>();
    FOR_IN(part,path_rest->split(const_4),62,63,123)
        if (___bool(part)) {
            path_list->append(part);
        }
    END_FOR

    n = ___min(2, __ss_void, 0, len(start_list), len(path_list));
    i = 0;
    while ((i < n) && __eq(start_list->__getfast__(i), path_list->__getfast__(i))) {
        i++;
    }

    rel_list = new list<str *>();
    for (j = i; j < len(start_list); j++) {
        rel_list->append(pardir);
    }
    for (j = i; j < len(path_list); j++) {
        rel_list->append(path_list->__getfast__(j));
    }

    if ((!___bool(rel_list))) {
        return curdir;
    }
    return joinl(rel_list);
}

str *realpath(str *path, __ss_bool strict) {

    if (strict.value && (!exists(path).value)) {
        throw new FileNotFoundError(path);
    }
    return abspath(path);
}

str *expanduser(str *path) {
    /**
    Expand ~ and ~user constructs.  If user or $HOME is unknown,
    do nothing.
    */
    str *userhome, *homepath, *homedrive, *target_user, *current_user;
    __ss_int i, n;

    if (!path->startswith(const_20))
        return path;

    n = len(path);
    i = 1;
    while ((i < n) && (!(const_18)->__contains__(path->__getitem__(i))))
        i++;

    userhome = __os__::getenv(const_21); /* USERPROFILE */
    if (!userhome) {
        homepath = __os__::getenv(const_23); /* HOMEPATH */
        if (!homepath)
            return path;
        homedrive = __os__::getenv(const_24, const_1); /* HOMEDRIVE, default '' */
        userhome = join(2, homedrive, homepath);
    }

    if (i != 1) { /* ~user */
        target_user = path->__slice__(3, 1, i, 0);
        current_user = __os__::getenv(const_25); /* USERNAME */
        if (!current_user)
            return path;
        if (__ne(target_user, current_user)) {
            /* Try to guess the user's home directory.  By default all
               user profile directories are located in the same place and
               are named by corresponding usernames.  If userhome isn't a
               normal profile directory, this guess is likely wrong, so
               bail out. */
            if (__ne(current_user, basename(userhome)))
                return path;
            userhome = join(2, dirname(userhome), target_user);
        }
    }

    return userhome->__add__(path->__slice__(1, i, 0, 0));
}

#endif

/* --------------------------------------------------------------------
   The functions below are intentionally written without any
   #ifdef WIN32 / #else split: they only use the shared, per-platform
   sep/curdir/pardir variables set up in __init() above, so the same
   source compiles correctly for every target.

   NOTE: this means they currently only implement posix-style
   semantics. Matching CPython's ntpath behavior exactly needs
   follow-up work (see TODOs below) -- until then, on Windows targets
   they behave like posixpath, not like ntpath.
   -------------------------------------------------------------------- */

str *expandvars(str *path) {
    /**
    Expand shell variables of form $var and ${var}.  Unknown variables
    are left unchanged.

    TODO: ntpath.expandvars also supports %var% syntax and quote
    handling ('...' sections are left unexpanded) on Windows. Not
    implemented here yet -- needs a platform-specific pass.
    */
    str *dollar, *lbrace, *rbrace, *underscore, *result, *name, *value, *ch;
    __ss_int i, j, n, start;

    dollar = new str("$");
    if (path->find(dollar) == -1)
        return path;

    lbrace = new str("{");
    rbrace = new str("}");
    underscore = new str("_");

    n = len(path);
    result = new str("");
    i = 0;
    while (i < n) {
        if (__eq(path->__getitem__(i), dollar) && i + 1 < n) {
            if (__eq(path->__getitem__(i + 1), lbrace)) {
                j = path->find(rbrace, i + 2);
                if (j == -1) {
                    /* no closing brace: leave the rest untouched */
                    result = result->__add__(path->__slice__(1, i, 0, 0));
                    i = n;
                    continue;
                }
                name = path->__slice__(3, i + 2, j, 0);
                start = j + 1;
            } else {
                j = i + 1;
                while (j < n) {
                    ch = path->__getitem__(j);
                    if (!(::isalnum((unsigned char)ch->c_str()[0]) || __eq(ch, underscore)))
                        break;
                    j++;
                }
                if (j == i + 1) {
                    /* bare '$' not followed by a name: keep literally */
                    result = result->__add__(dollar);
                    i++;
                    continue;
                }
                name = path->__slice__(3, i + 1, j, 0);
                start = j;
            }
            value = __os__::getenv(name);
            if (value)
                result = result->__add__(value);
            else
                result = result->__add__(path->__slice__(3, i, start, 0));
            i = start;
        } else {
            result = result->__add__(path->__getitem__(i));
            i++;
        }
    }
    return result;
}

str *commonpath(list<str *> *paths) {
    /**
    Given a list of pathnames, returns the longest common sub-path.

    TODO: ntpath.commonpath also enforces that all paths share the
    same drive/UNC root (case-insensitively) and raises ValueError on
    mismatch. Not implemented here yet -- needs a platform-specific
    pass using splitdrive()/normcase().
    */
    list<list<str *> *> *part_lists;
    list<str *> *parts, *common;
    str *p, *part, *posix_sep;
    __ss_bool have_abs, this_abs, first, match;
    __ss_int i, num_paths, n, k, m;

    if (!___bool(paths))
        throw new ValueError(new str("commonpath() arg is an empty sequence"));

    /* This function is intentionally posix-style on every platform (see
       the file-level NOTE above), so split on '/' explicitly rather than
       the platform's `sep` -- on Windows `sep` is '\\', which would leave
       these forward-slash paths unsplit. */
    posix_sep = new str("/");

    part_lists = new list<list<str *> *>();
    have_abs = False;
    first = True;
    n = -1;
    num_paths = len(paths);

    for (i = 0; i < num_paths; i++) {
        p = paths->__getfast__(i);
        this_abs = isabs(p);
        if (first) {
            have_abs = this_abs;
            first = False;
        } else if (!(this_abs == have_abs)) {
            throw new ValueError(new str("Can't mix absolute and relative paths"));
        }

        parts = new list<str *>();
        list<str *> *raw = p->split(posix_sep);
        for (k = 0; k < len(raw); k++) {
            part = raw->__getfast__(k);
            if (___bool(part) && !__eq(part, curdir))
                parts->append(part);
        }
        part_lists->append(parts);

        m = len(parts);
        if (n == -1 || m < n)
            n = m;
    }

    common = new list<str *>();
    k = 0;
    while (k < n) {
        part = part_lists->__getfast__(0)->__getfast__(k);
        match = True;
        for (i = 1; i < num_paths; i++) {
            if (!__eq(part_lists->__getfast__(i)->__getfast__(k), part)) {
                match = False;
                break;
            }
        }
        if (!match)
            break;
        common->append(part);
        k++;
    }

    /* Join with the hardcoded posix separator, not joinl()/sep -- joinl()
       applies platform-specific (e.g. drive-letter) join rules via the
       platform `sep`, which would reintroduce backslashes on Windows. */
    str *joined = new str("");
    for (i = 0; i < len(common); i++) {
        if (i > 0)
            joined = joined->__iadd__(posix_sep);
        joined = joined->__iadd__(common->__getfast__(i));
    }

    if (have_abs) {
        if (___bool(common))
            return posix_sep->__add__(joined);
        return posix_sep;
    }
    if (___bool(common))
        return joined;
    return new str("");
}

} // module namespace
} // module namespace

