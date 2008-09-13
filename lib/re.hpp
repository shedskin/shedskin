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

extern const int I, L, M, S, U, X, 
    IGNORECASE, LOCALE, MULTILINE, DOTALL, UNICODE, VERBOSE;

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
    int pos, endpos;
    
    //last match and last named match
    int lastindex;
    
    //subject string
    str *string;
    
    //NOTE: not implemented
    str *lastgroup;
    
    //functions
    str *expand(str *tpl);
    
    str *group(int m = 0);
    str *group(str *m);
    
    dict<str *, str *> *groupdict(str *defval = 0);
    tuple2<str *, str *> *groups(str *defval = 0);
    
    int __index(int matchid, char isend);
    int __index(str *mname, char isend);
    
    int end(int matchid = 0);
    int end(str *mname);
    int start(int matchid = 0);
    int start(str *mname);
    
    
    //...yeah
};


//compiled regular expression
class re_object : public pyobj 
{
public:
    
    //named captured subpatterns
    dict<str *, int> *groupindex;
    
    //how many captured subpatterns there are
    int capture_count;
    
    //the original pattern
    str *pattern;
    
    //the flags used
    int flags;
    
    //internal functions
    __GC_STRING __group(__GC_STRING *subj, int *captured, int m);
    __GC_STRING __group(__GC_STRING *subj, int *captured, str *m);
    __GC_STRING __expand(__GC_STRING *subj, int *captured, __GC_STRING tpl);
    
    //the compiled pattern + extra info for optimization
    pcre *compiled_pattern;
    pcre_extra *study_info;
    
    match_object *__exec(str *subj, int pos = 0, int endpos = -1, int flags = 0);
    str *__subn(str *repl, str *subj, int maxn = -1, int *howmany = 0);
    list<str *> *__splitfind(str *subj, int maxn, char onlyfind, int flags);
    int __convert_flags(int flags);
    
    match_object *match(str *subj, int pos = 0, int endpos = -1);
    match_object *search(str *subj, int pos = 0, int endpos = -1);
    __iter<match_object *> *finditer(str *subj, int pos = 0, int endpos = -1, int flags = 0);
    list<str *> *split(str *subj, int maxn = -1);
    str *sub(str *repl, str *subj, int maxn = -1);
    str *sub(replfunc repl, str *subj, int maxn = -1);
    tuple2<str *, int> *subn(str *repl, str *subj, int maxn = -1);
    list<str *> *findall(str *subj, int flags = 0);
    
    //stuff
};

class match_iter : public __iter<match_object *> 
{
public:
    re_object *ro;
    str *subj;
    int pos, endpos, flags;
    
    match_iter(re_object *ro, str *subj, int pos, int endpos, int flags);
    match_object *next();
};

//re.* functions
re_object *compile(str *pat, int flags = 0);

match_object *match(str *pat, str *subj, int flags = 0);
match_object *search(str *pat, str *subj, int flags = 0);
__iter<match_object *> *finditer(str *pat, str *subj, int pos = 0, int endpos = -1, int flags = 0);
list<str *> *split(str *pat, str *subj, int maxn = 0);
str *sub(str *pat, str *repl, str *subj, int maxn = 0);
str *sub(str *pat, replfunc repl, str *subj, int maxn = 0);
tuple2<str *, int> *subn(str *pat, str *repl, str *subj, int maxn = 0);
list<str *> *findall(str *pat, str *subj, int flags = 0);
str *escape(str *s);

list<str *> *__splitfind_once(str *pat, str *subj, int maxn, char onlyfind, int flags);
match_object *__exec_once(str *subj, int flags);

//internal functions
void __init(void);

void *re_malloc(size_t n);
void re_free(void *o);

}
#endif
