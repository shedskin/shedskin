#ifndef __RE_HPP
#define __RE_HPP

//depending on what you want...
//#define PCRE_STATIC

#include "builtin.hpp"

#ifndef __sun
#include <pcre.h>
#else
#include <pcre/pcre.h>
#endif


using namespace __shedskin__;

namespace __re__ {

extern const __ss_int I, L, M, S, U, X,
    IGNORECASE, LOCALE, MULTILINE, DOTALL, __ss_UNICODE, VERBOSE;

class match_object;
typedef str *(*replfunc)(match_object *);

//re.error
class error : public Exception
{
public:

    error(str *m = 0) : Exception(m) {}

#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_Exception; }
#endif
};

//we have a circular declaration, so we need to forward declare re_object
class re_object;

//MatchObject
class match_object : public pyobj
{
public:

    //our regular expression
    re_object *re;

    //internal: captured subpatterns
    int *captured;

    //self-explanatory
    __ss_int pos, endpos;

    //last match and last named match
    __ss_int lastindex;

    //subject string
    str *string;

    //NOTE: not implemented
    str *lastgroup;

    //functions
    str *expand(str *tpl);

    str *group(__ss_int n, __ss_int m = 0);
    tuple2<str *, str *> *group(__ss_int n, __ss_int m, __ss_int o, ...);
    str *group(__ss_int n, str *m);
    tuple2<str *, str *> *group(__ss_int n, str *m, str *o, ...);

    dict<str *, str *> *groupdict(str *defval = 0);
    tuple2<str *, str *> *groups(str *defval = 0);

    __ss_int __index(__ss_int matchid, char isend);
    __ss_int __index(str *mname, char isend);

    __ss_int end(__ss_int matchid = 0);
    __ss_int end(str *mname);
    __ss_int start(__ss_int matchid = 0);
    __ss_int start(str *mname);

    str *__repr__();
};


//compiled regular expression
class re_object : public pyobj
{
public:

    //named captured subpatterns
    dict<str *, __ss_int> *groupindex;

    //how many captured subpatterns there are
    __ss_int capture_count;

    //the original pattern
    str *pattern;

    //the flags used
    __ss_int flags;

    //internal functions
    __GC_STRING __group(__GC_STRING *subj, int *captured, __ss_int m);
    __GC_STRING __group(__GC_STRING *subj, int *captured, str *m);
    __GC_STRING __expand(__GC_STRING *subj, int *captured, __GC_STRING tpl);

    //the compiled pattern + extra info for optimization
    pcre *compiled_pattern;
    pcre_extra *study_info;

    match_object *__exec(str *subj, __ss_int pos = 0, __ss_int endpos = -1, __ss_int flags = 0);
    str *__subn(str *repl, str *subj, __ss_int maxn = -1, int *howmany = 0);
    list<str *> *__splitfind(str *subj, __ss_int maxn, char onlyfind, __ss_int flags);
    __ss_int __convert_flags(__ss_int flags);

    match_object *match(str *subj, __ss_int pos = 0, __ss_int endpos = -1);
    match_object *search(str *subj, __ss_int pos = 0, __ss_int endpos = -1);
    __iter<match_object *> *finditer(str *subj, __ss_int pos = 0, __ss_int endpos = -1, __ss_int flags = 0);
    list<str *> *split(str *subj, __ss_int maxn = -1);
    str *sub(str *repl, str *subj, __ss_int maxn = -1);
    str *sub(replfunc repl, str *subj, __ss_int maxn = -1);
    tuple2<str *, __ss_int> *subn(str *repl, str *subj, __ss_int maxn = -1);
    list<str *> *findall(str *subj, __ss_int flags = 0);

    str *__repr__();
};

class match_iter : public __iter<match_object *>
{
public:
    re_object *ro;
    str *subj;
    __ss_int pos, endpos, flags;

    match_iter(re_object *ro, str *subj, __ss_int pos, __ss_int endpos, __ss_int flags);
    match_object *next();
};

re_object *compile(str *pat, __ss_int flags = 0);

match_object *match(str *pat, str *subj, __ss_int flags = 0);
match_object *search(str *pat, str *subj, __ss_int flags = 0);
__iter<match_object *> *finditer(str *pat, str *subj, __ss_int pos = 0, __ss_int endpos = -1, __ss_int flags = 0);
list<str *> *split(str *pat, str *subj, __ss_int maxn = 0);
str *sub(str *pat, str *repl, str *subj, __ss_int maxn = 0);
str *sub(str *pat, replfunc repl, str *subj, __ss_int maxn = 0);
tuple2<str *, __ss_int> *subn(str *pat, str *repl, str *subj, __ss_int maxn = 0);
list<str *> *findall(str *pat, str *subj, __ss_int flags = 0);
str *escape(str *s);

list<str *> *__splitfind_once(str *pat, str *subj, __ss_int maxn, char onlyfind, __ss_int flags);
match_object *__exec_once(str *subj, __ss_int flags);

//internal functions
void __init(void);

void *re_malloc(size_t n);
void re_free(void *o);

}
#endif
