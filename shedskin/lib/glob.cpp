/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "glob.hpp"

/**
Filename globbing utility.
*/

namespace __glob__ {

str *const_0, *const_2, *const_3, *const_4, *const_5, *const_6;

str *__name__;
__re__::re_object *magic_check;
__re__::re_object *magic_check_escape;

void __init() {
    const_0 = new str("[*?[]");
    const_2 = new str(".");
    const_3 = new str("");
    const_4 = new str("([*?[])");
    const_5 = new str("[\\1]");
    const_6 = new str("**");

    __name__ = new str("__glob__");

    magic_check = __re__::compile(const_0);
    magic_check_escape = __re__::compile(const_4);
}

static inline list<str *> *list_comp_0(list<str *> *names);
static inline list<str *> *list_comp_1(str *dirname, list<str *> *names);

static inline list<str *> *list_comp_0(list<str *> *names) {
    str *x;
    list<str *> *__52;
    __iter<str *> *__53;
    __ss_int __54;
    list<str *>::for_in_loop __55;

    list<str *> *__ss_result = new list<str *>();

    __SS_LIST_RESERVE(__ss_result, 4);
    FOR_IN(x,names,52,54,55)
        if (__NOT(_ishidden(x))) {
            __ss_result->append(x);
        }
    END_FOR

    return __ss_result;
}

static inline list<str *> *list_comp_1(str *dirname, list<str *> *names) {
    str *x;
    list<str *> *__63;
    __iter<str *> *__64;
    __ss_int __65;
    list<str *>::for_in_loop __66;

    list<str *> *__ss_result = new list<str *>();

    __SS_LIST_RESERVE(__ss_result, 4);
    FOR_IN(x,names,63,65,66)
        if (__os__::__path__::isdir(__os__::__path__::join(2, dirname, x))) {
            __ss_result->append(x);
        }
    END_FOR

    return __ss_result;
}

list<str *> *glob(str *pathname, __ss_bool recursive, __ss_bool include_hidden, str *root_dir) {
    /**
    Return a list of paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la
    fnmatch. Unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns by default.

    If `include_hidden` is true, the patterns '*', '?', '**'  will match hidden
    directories.

    If `recursive` is true, the pattern '**' will match any files and
    zero or more directories and subdirectories.

    If `root_dir` is not None, it should be a path specifying the root
    directory for searching. It has the same effect as changing the current
    directory before calling it. If pathname is relative, the result will
    contain paths relative to `root_dir`.
    */
    return (new list<str *>(iglob(pathname, recursive, include_hidden, root_dir)));
}

__iter<str *> *iglob(str *pathname, __ss_bool recursive, __ss_bool include_hidden, str *root_dir) {
    /**
    Return an iterator which yields the paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns.

    If recursive is true, the pattern '**' will match any files and
    zero or more directories and subdirectories.
    */
    __iter<str *> *it;

    if (!root_dir)
        root_dir = const_3;
    it = _iglob(pathname, root_dir, recursive, False, include_hidden);
    if ((__NOT(___bool(pathname)) or (recursive and _isrecursive(pathname->__slice__(__ss_int(2LL), __ss_int(0LL), __ss_int(2LL), __ss_int(0LL)))))) {
        return _skip_empty(it);
    }
    return it;
}

class __gen__skip_empty : public __iter<str *> {
public:
    __ss_bool first;
    str *x;
    __iter<str *> *__7, *__8, *it;
    __ss_int __9;
    __iter<str *>::for_in_loop __10;

    int __last_yield;

    __gen__skip_empty(__iter<str *> *it) {
        this->it = it;
        __last_yield = -1;
    }

    str * __get_next() {
        return __get_next_awesome();
    }
    str * __get_next_awesome() {
        switch(__last_yield) {
            case 0: goto __after_yield_0;
            default: break;
        }
        first = True;

        FOR_IN(x,it,7,9,10)
            if (first) {
                first = False;
                if (__NOT(___bool(x))) {
                    continue;
                }
            }
            __last_yield = 0;
            __result = x;
            return __result;
            __after_yield_0:;
        END_FOR

        __stop_iteration = true;
        return __zero<str *>();
    }

};

__iter<str *> *_skip_empty(__iter<str *> *it) {
    return new __gen__skip_empty(it);

}

class __gen__iglob : public __iter<str *> {
public:
    str *basename, *dirname, *name, *pathname, *root_dir;
    pyiter<str *> *__26, *__34, *__42, *dirs;
    __ss_bool __12, __13, __22, __23, __24, __25, dironly, include_hidden, recursive;
    tuple<str *> *__11;
    __iter<str *> *__14, *__15, *__19, *__27, *__30, *__31, *__35, *__39, *__43, *__47;
    __ss_int __16, __20, __28, __32, __36, __40, __44, __48;
    __iter<str *>::for_in_loop __17, __33;
    list<str *> *__18, *__38, *__46;
    list<str *>::for_in_loop __21, __41, __49;
    pyiter<str *>::for_in_loop __29, __37, __45;

    int __last_yield;

    __gen__iglob(str *pathname,str *root_dir,__ss_bool recursive,__ss_bool dironly,__ss_bool include_hidden) {
        this->pathname = pathname;
        this->root_dir = root_dir;
        this->recursive = recursive;
        this->dironly = dironly;
        this->include_hidden = include_hidden;
        __last_yield = -1;
    }

    str * __get_next() {
        return __get_next_awesome();
    }
    str * __get_next_awesome() {
        switch(__last_yield) {
            case 0: goto __after_yield_0;
            case 1: goto __after_yield_1;
            case 2: goto __after_yield_2;
            case 3: goto __after_yield_3;
            case 4: goto __after_yield_4;
            case 5: goto __after_yield_5;
            case 6: goto __after_yield_6;
            default: break;
        }
        __11 = __os__::__path__::split(pathname);
        __SS_UNPACK_CHECK(__11, 2);
        dirname = __11->__getfirst__();
        basename = __11->__getsecond__();
        if (__NOT(has_magic(pathname))) {
            if (___bool(basename)) {
                if (__os__::__path__::lexists(_join(root_dir, pathname))) {
                    __last_yield = 0;
                    __result = pathname;
                    return __result;
                    __after_yield_0:;
                }
            }
            else if (__os__::__path__::isdir(_join(root_dir, dirname))) {
                __last_yield = 1;
                __result = pathname;
                return __result;
                __after_yield_1:;
            }
            __stop_iteration = true;
            return __zero<str *>();
        }
        if (__NOT(___bool(dirname))) {
            if ((recursive and _isrecursive(basename))) {

                FOR_IN(name,_glob2(root_dir, basename, dironly, include_hidden),14,16,17)
                    __last_yield = 2;
                    __result = name;
                    return __result;
                    __after_yield_2:;
                END_FOR

            }
            else {

                FOR_IN(name,_glob1(root_dir, basename, dironly, include_hidden),18,20,21)
                    __last_yield = 3;
                    __result = name;
                    return __result;
                    __after_yield_3:;
                END_FOR

            }
            __stop_iteration = true;
            return __zero<str *>();
        }
        if ((__ne(dirname, pathname) and has_magic(dirname))) {
            dirs = ((pyiter<str *> *)(_iglob(dirname, root_dir, recursive, True, include_hidden)));
        }
        else {
            dirs = (new list<str *>(1,dirname));
        }
        if (has_magic(basename)) {
            if ((recursive and _isrecursive(basename))) {

                FOR_IN(dirname,dirs,26,28,29)

                    FOR_IN(name,_glob2(_join(root_dir, dirname), basename, dironly, include_hidden),30,32,33)
                        __last_yield = 4;
                        __result = __os__::__path__::join(2, dirname, name);
                        return __result;
                        __after_yield_4:;
                    END_FOR

                END_FOR

            }
            else {

                FOR_IN(dirname,dirs,34,36,37)

                    FOR_IN(name,_glob1(_join(root_dir, dirname), basename, dironly, include_hidden),38,40,41)
                        __last_yield = 5;
                        __result = __os__::__path__::join(2, dirname, name);
                        return __result;
                        __after_yield_5:;
                    END_FOR

                END_FOR

            }
        }
        else {

            FOR_IN(dirname,dirs,42,44,45)

                FOR_IN(name,_glob0(_join(root_dir, dirname), basename, dironly, include_hidden),46,48,49)
                    __last_yield = 6;
                    __result = __os__::__path__::join(2, dirname, name);
                    return __result;
                    __after_yield_6:;
                END_FOR

            END_FOR

        }
        __stop_iteration = true;
        return __zero<str *>();
    }

};

__iter<str *> *_iglob(str *pathname, str *root_dir, __ss_bool recursive, __ss_bool dironly, __ss_bool include_hidden) {
    return new __gen__iglob(pathname,root_dir,recursive,dironly,include_hidden);

}

list<str *> *_glob1(str *dirname, str *pattern, __ss_bool dironly, __ss_bool include_hidden) {
    list<str *> *names;
    __ss_bool __50, __51;

    names = _listdir(dirname, dironly);
    if (__NOT((include_hidden or _ishidden(pattern)))) {
        names = list_comp_0(names);
    }
    return __fnmatch__::filter(names, pattern);
}

list<str *> *_glob0(str *dirname, str *basename, __ss_bool dironly, __ss_bool include_hidden) {
    if (___bool(basename)) {
        if (__os__::__path__::lexists(__os__::__path__::join(2, dirname, basename))) {
            return (new list<str *>(1,basename));
        }
    }
    else if (__os__::__path__::isdir(dirname)) {
        return (new list<str *>(1,basename));
    }
    return (__ss_list<str *, 0>());
}

class __gen__glob2 : public __iter<str *> {
public:
    str *dirname, *name, *pattern;
    __ss_bool __56, __57, dironly, include_hidden;
    __iter<str *> *__58, *__59;
    __ss_int __60;
    __iter<str *>::for_in_loop __61;

    int __last_yield;

    __gen__glob2(str *dirname,str *pattern,__ss_bool dironly,__ss_bool include_hidden) {
        this->dirname = dirname;
        this->pattern = pattern;
        this->dironly = dironly;
        this->include_hidden = include_hidden;
        __last_yield = -1;
    }

    str * __get_next() {
        return __get_next_awesome();
    }
    str * __get_next_awesome() {
        switch(__last_yield) {
            case 0: goto __after_yield_0;
            case 1: goto __after_yield_1;
            default: break;
        }
        if ((__NOT(___bool(dirname)) or __os__::__path__::isdir(dirname))) {
            __last_yield = 0;
            __result = const_3;
            return __result;
            __after_yield_0:;
        }

        FOR_IN(name,_rlistdir(dirname, dironly, include_hidden),58,60,61)
            __last_yield = 1;
            __result = name;
            return __result;
            __after_yield_1:;
        END_FOR

        __stop_iteration = true;
        return __zero<str *>();
    }

};

__iter<str *> *_glob2(str *dirname, str *pattern, __ss_bool dironly, __ss_bool include_hidden) {
    return new __gen__glob2(dirname,pattern,dironly,include_hidden);

}

list<str *> *_listdir(str *dirname, __ss_bool dironly) {
    list<str *> *names;

    if (__NOT(___bool(dirname))) {
        dirname = __os__::curdir;
    }
    try {
        names = __os__::listdir(dirname);
    } catch (OSError *) {
        return (__ss_list<str *, 1>());
    }
    if (dironly) {
        names = list_comp_1(dirname, names);
    }
    return names;
}

class __gen__rlistdir : public __iter<str *> {
public:
    list<str *> *__67, *names;
    str *dirname, *path, *x, *y;
    __ss_bool __71, __72, dironly, include_hidden;
    __iter<str *> *__68, *__73, *__74;
    __ss_int __69, __75;
    list<str *>::for_in_loop __70;
    __iter<str *>::for_in_loop __76;

    int __last_yield;

    __gen__rlistdir(str *dirname,__ss_bool dironly,__ss_bool include_hidden) {
        this->dirname = dirname;
        this->dironly = dironly;
        this->include_hidden = include_hidden;
        __last_yield = -1;
    }

    str * __get_next() {
        return __get_next_awesome();
    }
    str * __get_next_awesome() {
        switch(__last_yield) {
            case 0: goto __after_yield_0;
            case 1: goto __after_yield_1;
            default: break;
        }
        names = _listdir(dirname, dironly);

        FOR_IN(x,names,67,69,70)
            if ((include_hidden or __NOT(_ishidden(x)))) {
                __last_yield = 0;
                __result = x;
                return __result;
                __after_yield_0:;
                if (___bool(dirname)) {
                    path = __os__::__path__::join(2, dirname, x);
                }
                else {
                    path = x;
                }

                FOR_IN(y,_rlistdir(path, dironly, include_hidden),73,75,76)
                    __last_yield = 1;
                    __result = __os__::__path__::join(2, x, y);
                    return __result;
                    __after_yield_1:;
                END_FOR

            }
        END_FOR

        __stop_iteration = true;
        return __zero<str *>();
    }

};

__iter<str *> *_rlistdir(str *dirname, __ss_bool dironly, __ss_bool include_hidden) {
    return new __gen__rlistdir(dirname,dironly,include_hidden);

}

__ss_bool _ishidden(str *path) {
    return ___bool(__eq(path->__getfast__(__ss_int(0LL)), const_2));
}

__ss_bool _isrecursive(str *pattern) {
    return ___bool(__eq(pattern, const_6));
}

str *_join(str *dirname, str *basename) {
    /* it is common if dirname or basename is empty */
    if (!___bool(dirname) || !___bool(basename))
        return ___bool(dirname) ? dirname : basename;
    return __os__::__path__::join(2, dirname, basename);
}

__ss_bool has_magic(str *s) {

    return __mbool(magic_check->search(s)!=0);
}

str *escape(str *pathname) {
    /**
    Escape all special characters ('?', '*' and '[').

    This is useful if you want to match an arbitrary literal string that may
    have special characters in it.

    */
    tuple2<str *, str *> *__0;
    str *drive, *rest;

    __0 = __os__::__path__::splitdrive(pathname);
    drive = __0->__getfirst__();
    rest = __0->__getsecond__();

    rest = magic_check_escape->sub(const_5, rest);

    return __add_strs(2, drive, rest);
}


namespace {

/* Mirrors re.escape()'s rule for one character, matching the convention the
   fnmatch translation core uses (see escape_char there): alphanumerics pass
   through, everything else is backslash-escaped (safe in PCRE2: a backslash
   before a non-alphanumeric always means the literal character). */
inline void escape_char(__GC_STR &out, __ss_char c) {
    if (c > 127 || ::isalnum((int)c)) {
        out += c;
    }
    else {
        out += '\\';
        out += c;
    }
}

} // anonymous namespace

str *translate(str *pat, __ss_bool recursive, __ss_bool include_hidden, str *seps) {
    /**
    Translate a pathname with shell wildcards to a regular expression.
    (Python 3.13+ glob.translate)

    If `recursive` is true, the pattern segment '**' will match any number
    of path segments.

    If `include_hidden` is true, wildcards can match path segments beginning
    with a dot ('.').

    If a string of separator characters is given as `seps`, they will be
    used to split the pattern into segments and match path separators. If
    not given, os.sep (and os.altsep on Windows) is used. (CPython also
    accepts a tuple of single-character strings here; we support the string
    form.)

    Note: like fnmatch.translate, the produced regex is anchored with \z
    (PCRE2's strict end-of-string) rather than CPython's \Z, and literal
    characters are escaped slightly more eagerly than re.escape() -- the
    resulting regex text can differ from CPython's character for character,
    but matches the same strings when compiled with shedskin's re module.
    */
    __GC_STR seps_s;
    if (seps && seps->unit.size()) {
        seps_s = seps->unit;
    }
    else {
#ifdef WIN32
        seps_s = __gcs("\\/");
#else
        seps_s = __gcs("/");
#endif
    }

    __GC_STR escaped_seps;
    for (size_t k = 0; k < seps_s.size(); k++)
        escape_char(escaped_seps, seps_s[k]);

    __GC_STR any_sep;
    if (seps_s.size() > 1)
        any_sep = __gcs("[") + escaped_seps + __gcs("]");
    else
        any_sep = escaped_seps;
    __GC_STR not_sep = __gcs("[^") + escaped_seps + __gcs("]");

    __GC_STR one_last_segment, one_segment, any_segments, any_last_segments;
    if (include_hidden.value) {
        one_last_segment = not_sep + __gcs("+");
        one_segment = one_last_segment + any_sep;
        any_segments = __gcs("(?:.+") + any_sep + __gcs(")?");
        any_last_segments = __gcs(".*");
    }
    else {
        one_last_segment = __gcs("[^") + escaped_seps + __gcs(".]") + not_sep + __gcs("*");
        one_segment = one_last_segment + any_sep;
        any_segments = __gcs("(?:") + one_segment + __gcs(")*");
        any_last_segments = any_segments + __gcs("(?:") + one_last_segment + __gcs(")?");
    }

    /* split the pattern on any separator character (like CPython's
       re.split(any_sep, pat): separators between/around segments produce
       empty parts, so "a//b" -> ["a", "", "b"] and "/a" -> ["", "a"]) */
    std::vector<__GC_STR> parts;
    {
        const __GC_STR &p = pat->unit;
        __GC_STR cur;
        for (size_t k = 0; k < p.size(); k++) {
            if (seps_s.find(p[k]) != __GC_STR::npos) {
                parts.push_back(cur);
                cur.clear();
            }
            else {
                cur += p[k];
            }
        }
        parts.push_back(cur);
    }

    __GC_STR res;
    __GC_STR seg_star = not_sep + __gcs("*"); /* what `*` means inside a segment */
    size_t last_part_idx = parts.size() - 1;

    for (size_t idx = 0; idx < parts.size(); idx++) {
        const __GC_STR &part = parts[idx];
        if (part == U"*") {
            res += (idx < last_part_idx) ? one_segment : one_last_segment;
        }
        else if (recursive.value && part == U"**") {
            if (idx < last_part_idx) {
                if (parts[idx + 1] != U"**") /* consecutive '**' collapse */
                    res += any_segments;
            }
            else {
                res += any_last_segments;
            }
        }
        else {
            if (!part.empty()) {
                if (!include_hidden.value && (part[0] == '*' || part[0] == '?'))
                    res += __gcs("(?!\\.)"); /* wildcards must not match hidden names */
                __fnmatch__::__translate_core(part, seg_star, not_sep, res);
            }
            if (idx < last_part_idx)
                res += any_sep;
        }
    }

    return new str(__gcs("(?s:") + res + __gcs(")\\z"));
}

} // module namespace
