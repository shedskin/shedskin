#include "fnmatch.hpp"

/**
Filename matching with shell patterns.

fnmatch(FILENAME, PATTERN) matches according to the local convention.
fnmatchcase(FILENAME, PATTERN) always takes case in account.

The functions operate by translating the pattern into a regular
expression.  They cache the compiled regular expressions for speed.

The function translate(PATTERN) returns a regular expression
corresponding to PATTERN.  (It does not compile it.)
*/

namespace __fnmatch__ {

str *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_5, *const_6, *const_7, *const_8, *const_9;

dict<str *, __re__::re_object *> *_cache;
str *__name__;

void __init() {
    const_5 = new str("");
    const_6 = new str("*");
    const_7 = new str(".*");
    const_8 = new str("?");
    const_9 = new str(".");
    const_10 = new str("[");
    const_11 = new str("!");
    const_12 = new str("]");
    const_13 = new str("\\[");
    const_14 = new str("\\");
    const_15 = new str("\\\\");
    const_16 = new str("^");
    const_17 = new str("%s[%s]");
    const_18 = new str("$");

    __name__ = new str("__fnmatch__");

    _cache = (new dict<str *, __re__::re_object *>());
}

__ss_bool fnmatch(str *name, str *pat) {
    /**
    Test whether FILENAME matches PATTERN.

    Patterns are Unix shell style:

    *       matches everything
    ?       matches any single character
    [seq]   matches any character in seq
    [!seq]  matches any char not in seq

    An initial period in FILENAME is not special.
    Both FILENAME and PATTERN are first case-normalized
    if the operating system requires it.
    If you don't want this, use fnmatchcase(FILENAME, PATTERN).
    */

    name = __os__::__path__::normcase(name);
    pat = __os__::__path__::normcase(pat);
    return fnmatchcase(name, pat);
}

list<str *> *filter(list<str *> *names, str *pat) {
    /**
    Return the subset of the list NAMES that match PAT
    */
    list<str *> *__0, *result;
    str *name, *res;
    __re__::re_object *cpat;
    __iter<str *> *__1, *__4;
    __ss_int __2;

    result = (new list<str *>());
    pat = __os__::__path__::normcase(pat);
    if ((!_cache->__contains__(pat))) {
        res = translate(pat);
        _cache->__setitem__(pat, __re__::compile(res));
    }
    cpat = _cache->__getitem__(pat);

        FOR_IN_SEQ(name,names,0,2)
#ifndef WIN32
            if (___bool(cpat->match(name))) {
#else
            if (___bool(cpat->match(__os__::__path__::normcase(name)))) {
#endif
                result->append(name);
            }
        END_FOR

    return result;
}

__ss_bool fnmatchcase(str *name, str *pat) {
    /**
    Test whether FILENAME matches PATTERN, including case.

    This is a version of fnmatch() which doesn't case-normalize
    its arguments.
    */
    str *res;

    if ((!_cache->__contains__(pat))) {
        res = translate(pat);
        _cache->__setitem__(pat, __re__::compile(res));
    }
    return __mbool((_cache->__getitem__(pat))->match(name)!=0);
}

str *translate(str *pat) {
    /**
    Translate a shell PATTERN to a regular expression.

    There is no way to quote meta-characters.
    */
    str *c, *res, *stuff;
    __ss_int __10, __11, __12, __6, __7, __8, __9, i, j, n;

    __6 = len(pat);
    i = 0;
    n = __6;
    res = const_5;

    while((i<n)) {
        c = pat->__getitem__(i);
        i = (i+1);
        if (__eq(c, const_6)) {
            res = res->__add__(const_7);
        }
        else if (__eq(c, const_8)) {
            res = res->__add__(const_9);
        }
        else if (__eq(c, const_10)) {
            j = i;
            if (__AND((j<n), __eq(pat->__getitem__(j), const_11), 7)) {
                j = (j+1);
            }
            if (__AND((j<n), __eq(pat->__getitem__(j), const_12), 9)) {
                j = (j+1);
            }

            while(__AND((j<n), __ne(pat->__getitem__(j), const_12), 11)) {
                j = (j+1);
            }
            if ((j>=n)) {
                res = res->__add__(const_13);
            }
            else {
                stuff = (pat->__slice__(3, i, j, 0))->replace(const_14, const_15);
                i = (j+1);
                if (__eq(stuff->__getitem__(0), const_11)) {
                    stuff = (const_16)->__add__(stuff->__slice__(1, 1, 0, 0));
                }
                else if (__eq(stuff->__getitem__(0), const_16)) {
                    stuff = (const_14)->__add__(stuff);
                }
                res = __modct(const_17, 2, res, stuff);
            }
        }
        else {
            res = res->__add__(__re__::escape(c));
        }
    }
    return res->__add__(const_18);
}

} // module namespace
