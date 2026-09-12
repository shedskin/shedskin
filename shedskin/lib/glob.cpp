/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "glob.hpp"

/**
Filename globbing utility.
*/

namespace __glob__ {

str *const_0, *const_2, *const_3, *const_4, *const_5;

str *__name__;
__re__::re_object *magic_check;
__re__::re_object *magic_check_escape;

void __init() {
    const_0 = new str("[*?[]");
    const_2 = new str(".");
    const_3 = new str("");
    const_4 = new str("([*?[])");
    const_5 = new str("[\\1]");

    __name__ = new str("__glob__");

    magic_check = __re__::compile(const_0);
    magic_check_escape = __re__::compile(const_4);
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
    str *name;
    pyiter<str *> *__10;
    str *basename;
    __ss_int __15;
    list<str *> *__13;
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
    pyiter<str *>::for_in_loop __103;
    int __102;
    pyiter<str *> *__101;
    int __last_yield;
    list<str *>::for_in_loop __123;

    __gen_iglob(str *pathname_) {
        this->pathname = pathname_;
        __last_yield = -1;
    }

    str * __next__() {
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

            FOR_IN(name,glob1(__os__::curdir, basename),1,3,123)
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

            FOR_IN(dirname,dirs,101,102,103)

                FOR_IN(name,glob1(dirname, basename),7,9,123)
                    __last_yield = 2;
                    return __os__::__path__::join(2, dirname, name);
                    __after_yield_2:;
                END_FOR

            END_FOR

        }
        else {

            FOR_IN(dirname,dirs,101,102,103)

                FOR_IN(name,glob0(dirname, basename),13,15,123)
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
    str *nm;
    __ss_int __19;
    list<str *>::for_in_loop __123;

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

        FOR_IN(nm,names,17,19,123)
            if (__ne(nm->__getitem__(0), const_2)) {
                n2->append(nm);
            }
        END_FOR

        names = n2;
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
inline void escape_char(__GC_STRING &out, char c) {
    if (::isalnum((unsigned char)c)) {
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
    __GC_STRING seps_s;
    if (seps && seps->unit.size()) {
        seps_s = seps->unit;
    }
    else {
#ifdef WIN32
        seps_s = "\\/";
#else
        seps_s = "/";
#endif
    }

    __GC_STRING escaped_seps;
    for (size_t k = 0; k < seps_s.size(); k++)
        escape_char(escaped_seps, seps_s[k]);

    __GC_STRING any_sep;
    if (seps_s.size() > 1)
        any_sep = "[" + escaped_seps + "]";
    else
        any_sep = escaped_seps;
    __GC_STRING not_sep = "[^" + escaped_seps + "]";

    __GC_STRING one_last_segment, one_segment, any_segments, any_last_segments;
    if (include_hidden.value) {
        one_last_segment = not_sep + "+";
        one_segment = one_last_segment + any_sep;
        any_segments = "(?:.+" + any_sep + ")?";
        any_last_segments = ".*";
    }
    else {
        one_last_segment = "[^" + escaped_seps + ".]" + not_sep + "*";
        one_segment = one_last_segment + any_sep;
        any_segments = "(?:" + one_segment + ")*";
        any_last_segments = any_segments + "(?:" + one_last_segment + ")?";
    }

    /* split the pattern on any separator character (like CPython's
       re.split(any_sep, pat): separators between/around segments produce
       empty parts, so "a//b" -> ["a", "", "b"] and "/a" -> ["", "a"]) */
    std::vector<__GC_STRING> parts;
    {
        const __GC_STRING &p = pat->unit;
        __GC_STRING cur;
        for (size_t k = 0; k < p.size(); k++) {
            if (seps_s.find(p[k]) != __GC_STRING::npos) {
                parts.push_back(cur);
                cur.clear();
            }
            else {
                cur += p[k];
            }
        }
        parts.push_back(cur);
    }

    __GC_STRING res;
    __GC_STRING seg_star = not_sep + "*"; /* what `*` means inside a segment */
    size_t last_part_idx = parts.size() - 1;

    for (size_t idx = 0; idx < parts.size(); idx++) {
        const __GC_STRING &part = parts[idx];
        if (part == "*") {
            res += (idx < last_part_idx) ? one_segment : one_last_segment;
        }
        else if (recursive.value && part == "**") {
            if (idx < last_part_idx) {
                if (parts[idx + 1] != "**") /* consecutive '**' collapse */
                    res += any_segments;
            }
            else {
                res += any_last_segments;
            }
        }
        else {
            if (!part.empty()) {
                if (!include_hidden.value && (part[0] == '*' || part[0] == '?'))
                    res += "(?!\\.)"; /* wildcards must not match hidden names */
                __fnmatch__::__translate_core(part, seg_star, not_sep, res);
            }
            if (idx < last_part_idx)
                res += any_sep;
        }
    }

    return new str("(?s:" + res + ")\\z");
}

} // module namespace
