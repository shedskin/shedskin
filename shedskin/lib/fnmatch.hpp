/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __FNMATCH_HPP
#define __FNMATCH_HPP

#include "builtin.hpp"
#include "os/path.hpp"
#include "os/__init__.hpp"
#include "re.hpp"

using namespace __shedskin__;
namespace __fnmatch__ {

extern dict<str *, __re__::Pattern *> *_cache;
extern str *__name__;

__ss_bool fnmatch(str *name, str *pat);
__ss_bool fnmatchcase(str *name, str *pat);
list<str *> *filter(list<str *> *names, str *pat);
list<str *> *filterfalse(list<str *> *names, str *pat);
str *translate(str *pat);

/* internal: re.escape() for a single character (CPython 3.7+ rule: only
   characters that are special in a regex get a backslash), shared with
   glob.translate(). */
inline void __escape_char(__GC_STR &out, __ss_char c) {
    static const char special[] = "()[]{}?*+-|^$\\.&~# \t\n\r\v\f";
    if (c < 128 && c != 0 && strchr(special, (int)c))
        out += '\\';
    out += c;
}

/* internal: shared pattern-translation core, parameterized over what `*` and
   `?` translate to, so glob.translate() can reuse the exact same wildcard and
   character-class handling with segment-local replacements ("[^/]*", "[^/]").
   Appends to `res`; does not add the "(?s:...)" wrapper or end anchor. If
   `stars` is given, the offset in `res` of each (compressed) `*` is recorded
   there, so fnmatch.translate() can join the pieces like CPython does. */
void __translate_core(const __GC_STR &pat, const __GC_STR &star,
                      const __GC_STR &qmark, __GC_STR &res,
                      std::vector<size_t> *stars=NULL);

void __init(void);

} // module namespace
#endif
