/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

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

dict<str *, __re__::re_object *> *_cache;
str *__name__;

void __init() {
    __name__ = new str("__fnmatch__");

    _cache = (new dict<str *, __re__::re_object *>());
}

namespace {

/* Mirrors re.escape()'s "pass alnum through, backslash-escape everything
   else" rule for a single character, without the overhead of building a
   str object and round-tripping through __re__::escape(). */
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
    __ss_int __2;
    list<str *>::for_in_loop __123;

    result = (new list<str *>());
    pat = __os__::__path__::normcase(pat);
    if ((!_cache->__contains__(pat))) {
        res = translate(pat);
        _cache->__setitem__(pat, __re__::compile(res));
    }
    cpat = _cache->__getitem__(pat);

        FOR_IN(name,names,0,2,123)
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

list<str *> *filterfalse(list<str *> *names, str *pat) {
    /**
    Return the subset of the list NAMES that do not match PAT
    */
    list<str *> *__0, *result;
    str *name, *res;
    __re__::re_object *cpat;
    __ss_int __2;
    list<str *>::for_in_loop __123;

    result = (new list<str *>());
    pat = __os__::__path__::normcase(pat);
    if ((!_cache->__contains__(pat))) {
        res = translate(pat);
        _cache->__setitem__(pat, __re__::compile(res));
    }
    cpat = _cache->__getitem__(pat);

        FOR_IN(name,names,0,2,123)
#ifndef WIN32
            if (!___bool(cpat->match(name))) {
#else
            if (!___bool(cpat->match(__os__::__path__::normcase(name)))) {
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
    const __GC_STRING &p = pat->unit;
    size_t n = p.size();
    size_t i = 0;
    __GC_STRING res;
    bool last_was_star = false;

    while (i < n) {
        char c = p[i];
        i++;

        if (c == '*') {
            /* compress consecutive `*` into one, as CPython's translate()
               does -- purely an optimization (".*.*" and ".*" match the
               same strings), but it keeps pathological patterns like
               "a****************b" from building up redundant, slower
               regexes. */
            if (!last_was_star) {
                res += ".*";
                last_was_star = true;
            }
            continue;
        }
        last_was_star = false;

        if (c == '?') {
            res += '.';
        }
        else if (c == '[') {
            size_t j = i;
            if (j < n && p[j] == '!') j++;
            if (j < n && p[j] == ']') j++;
            while (j < n && p[j] != ']') j++;

            if (j >= n) {
                res += "\\[";
            }
            else {
                __GC_STRING stuff;
                __GC_STRING raw = p.substr(i, j - i); /* pat[i:j] */

                if (raw.find('-') == __GC_STRING::npos) {
                    /* no ranges in this class: just double up backslashes */
                    for (size_t k = 0; k < raw.size(); k++) {
                        if (raw[k] == '\\') stuff += '\\';
                        stuff += raw[k];
                    }
                }
                else {
                    /* Split the class body on '-' into "chunks" the way
                       CPython's fnmatch.translate() does since Python 3.6
                       (bpo-29249), so a lexicographically out-of-order
                       range like "[a-!]" or "[[-*]" -- which PCRE2 (and
                       modern CPython's own re) rejects as invalid at
                       compile time -- gets neutralized into a construct
                       that simply never matches, instead of blowing up
                       the whole program with an uncaught regex-compile
                       exception the moment somebody feeds fnmatch/glob an
                       unlucky pattern. */
                    std::vector<__GC_STRING> chunks;
                    size_t start = i;
                    size_t k = (p[i] == '!') ? i + 2 : i + 1;

                    while (true) {
                        size_t dash = p.find('-', k);
                        if (dash == __GC_STRING::npos || dash >= j) break;
                        chunks.push_back(p.substr(start, dash - start));
                        start = dash + 1;
                        k = dash + 3;
                    }
                    __GC_STRING last_chunk = p.substr(start, j - start);
                    if (!last_chunk.empty()) {
                        chunks.push_back(last_chunk);
                    }
                    else if (!chunks.empty()) {
                        chunks.back() += '-';
                    }
                    else {
                        chunks.push_back(__GC_STRING("-"));
                    }

                    /* Remove empty/out-of-order ranges -- invalid in a
                       regex: if the last character of one chunk sorts
                       after the first character of the next, "x-y" isn't
                       a real range, so fold the two chunks into one
                       literal run instead of emitting it as a range. */
                    for (size_t m = chunks.size(); m-- > 1; ) {
                        if (!chunks[m-1].empty() && !chunks[m].empty() &&
                            (unsigned char)chunks[m-1].back() > (unsigned char)chunks[m].front()) {
                            chunks[m-1] = chunks[m-1].substr(0, chunks[m-1].size()-1) + chunks[m].substr(1);
                            chunks.erase(chunks.begin() + (long)m);
                        }
                    }

                    /* Escape backslashes and hyphens (the hyphens that
                       still form real ranges live *between* chunks, not
                       inside one, so they're untouched by this) then
                       rejoin with '-'; also escape the PCRE2/newer-regex
                       set-operation chars &, ~, | for safety. */
                    for (size_t m = 0; m < chunks.size(); m++) {
                        if (m) stuff += '-';
                        for (size_t k2 = 0; k2 < chunks[m].size(); k2++) {
                            char ch = chunks[m][k2];
                            if (ch == '\\' || ch == '-' || ch == '&' || ch == '~' || ch == '|') {
                                stuff += '\\';
                            }
                            stuff += ch;
                        }
                    }
                }

                i = j + 1;

                if (stuff.empty()) {
                    res += "(?!)"; /* empty range: never matches */
                }
                else if (stuff == "!") {
                    res += '.'; /* negated empty range: matches anything */
                }
                else {
                    if (stuff[0] == '!') {
                        stuff = "^" + stuff.substr(1);
                    }
                    else if (stuff[0] == '^' || stuff[0] == '[') {
                        stuff = "\\" + stuff;
                    }
                    res += '[';
                    res += stuff;
                    res += ']';
                }
            }
        }
        else {
            escape_char(res, c);
        }
    }

    /* PCRE2 note: Python's re.translate()-style fix wraps the pattern in a
       DOTALL scope and anchors with \Z. shedskin's re module hands patterns
       straight to pcre2_compile() with no escape translation, and PCRE2's
       \Z means "end of subject, or just before a trailing newline" -- the
       same loose semantics as a bare $. Python's re \Z (strict end of
       string, no trailing-newline exception) is PCRE2's \z, so that's what
       we anchor with here. */
    return new str("(?s:" + res + ")\\z");
}

} // module namespace
