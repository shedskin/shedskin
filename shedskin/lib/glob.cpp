#include "glob.hpp"

/**
Filename globbing utility.
*/

namespace __glob__ {

str *const_0, *const_2, *const_3;

str *__name__;
__re__::re_object *magic_check;

void __init() {
    const_0 = new str("[*?[]");
    const_2 = new str(".");
    const_3 = new str("");

    __name__ = new str("__glob__");

    magic_check = __re__::compile(const_0);
}

list<str *> *glob(str *pathname) {
    /**
    Return a list of paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la fnmatch.

    */

    return new list<str *>(iglob(pathname));
}

class __gen_iglob : public __iter<str *> {
public:
    pyiter<str *> *dirs;
    __iter<str *> *__11;
    str *name;
    pyiter<str *> *__10;
    str *basename;
    __ss_int __15;
    list<str *> *__13;
    __iter<str *> *__5;
    pyiter<str *> *__4;
    list<str *> *__7;
    __ss_int __6;
    list<str *> *__1;
    tuple2<str *, str *> *__0;
    __ss_int __3;
    __iter<str *> *__2;
    str *pathname;
    str *dirname;
    __ss_int __9;
    __iter<str *> *__8;
    __ss_int __12;
    __iter<str *> *__14;
    int __last_yield;

    __gen_iglob(str *pathname) {
        this->pathname = pathname;
        __last_yield = -1;
    }

    str * next() {
        switch(__last_yield) {
            case 0: goto __after_yield_0;
            case 1: goto __after_yield_1;
            case 2: goto __after_yield_2;
            case 3: goto __after_yield_3;
            default: break;
        }
        if ((!has_magic(pathname))) {
            if (__os__::__path__::lexists(pathname)) {
                __last_yield = 0;
                return pathname;
                __after_yield_0:;
            }
            throw new StopIteration();
        }
        __0 = __os__::__path__::split(pathname);
        dirname = __0->__getfirst__();
        basename = __0->__getsecond__();
        if ((!___bool(dirname))) {

            FOR_IN_SEQ(name,glob1(__os__::curdir, basename),1,3)
                __last_yield = 1;
                return name;
                __after_yield_1:;
            END_FOR

            throw new StopIteration();
        }
        if (has_magic(dirname)) {
            dirs = iglob(dirname);
        }
        else {
            dirs = (new list<str *>(1, dirname));
        }
        if (has_magic(basename)) {

            FOR_IN(dirname,dirs,5)

                FOR_IN_SEQ(name,glob1(dirname, basename),7,9)
                    __last_yield = 2;
                    return __os__::__path__::join(2, dirname, name);
                    __after_yield_2:;
                END_FOR

            END_FOR

        }
        else {

            FOR_IN(dirname,dirs,11)

                FOR_IN_SEQ(name,glob0(dirname, basename),13,15)
                    __last_yield = 3;
                    return __os__::__path__::join(2, dirname, name);
                    __after_yield_3:;
                END_FOR

            END_FOR

        }
        throw new StopIteration();
    }

};

__iter<str *> *iglob(str *pathname) {
    /**
    Return a list of paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la fnmatch.

    */
    return new __gen_iglob(pathname);

}

list<str *> *glob1(str *dirname, str *pattern) {
    list<str *> *__17, *n2, *names;
    __iter<str *> *__18;
    str *nm;
    __ss_int __19;

    if ((!___bool(dirname))) {
        dirname = __os__::curdir;
    }
    try {
        names = __os__::listdir(dirname);
    } catch (__os__::error *) {
        return ((list<str *> *)((new list<void *>())));
    }
    if (__ne(pattern->__getitem__(0), const_2)) {
        n2 = (new list<str *>());

        FOR_IN_SEQ(nm,names,17,19)
            if (__ne(nm->__getitem__(0), const_2)) {
                n2->append(nm);
                names = n2;
            }
        END_FOR

    }
    return __fnmatch__::filter(names, pattern);
}

list<str *> *glob0(str *dirname, str *basename) {

    if (__eq(basename, const_3)) {
        if (__os__::__path__::isdir(dirname)) {
            return (new list<str *>(1, basename));
        }
    }
    else {
        if (__os__::__path__::lexists(__os__::__path__::join(2, dirname, basename))) {
            return (new list<str *>(1, basename));
        }
    }
    return ((list<str *> *)((new list<void *>())));
}

__ss_bool has_magic(str *s) {

    return __mbool(magic_check->search(s)!=0);
}

} // module namespace
