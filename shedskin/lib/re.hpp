/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __RE_HPP
#define __RE_HPP

#include "builtin.hpp"

using namespace __shedskin__;

namespace __re__ {

extern const __ss_int I, L, M, S, U, X, A,
    IGNORECASE, LOCALE, MULTILINE, DOTALL, __ss_UNICODE, VERBOSE, ASCII, DEBUG, NOFLAG;

class Match;
typedef str *(*replfunc)(Match *);

extern class_ *cl_error;

//re.PatternError (re.error): like CPython, when both pattern and pos are
//given, pos/lineno/colno are filled in and the message gets " at position N"
//(plus " (line L, column C)" for multi-line patterns). CPython uses None for
//pos/lineno/colno otherwise; as these are ints here, they are 0 instead.
class PatternError : public Exception
{
public:
    str *msg;
    str *pattern;
    __ss_int pos, lineno, colno;

    PatternError(str *msg = 0, str *pattern = 0, __ss_int pos = -1);

#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_Exception; } // TODO re.PatternError?
#endif
};

using error = PatternError;

//we have a circular declaration, so we need to forward declare Pattern
class Pattern;

//a compiled replacement template: literal chunks and group references
struct __template {
    std::vector<__GC_STR, __ss_allocator<__GC_STR> > literals; //one more than groups
    std::vector<__ss_int, __ss_allocator<__ss_int> > groups;
};

//MatchObject
class Match : public pyobj
{
public:

    //note: all members are default-initialized, so that directly
    //constructing re.Match() (which CPython disallows) stays harmless

    //our regular expression
    Pattern *re = 0;

    //start and end of the match and of each group (-1 if it did not participate)
    std::vector<__ss_int, __ss_allocator<__ss_int> > regs;

    //self-explanatory
    __ss_int pos = 0, endpos = 0;

    //the last group that was closed (0 if none, CPython: None)
    __ss_int lastindex = 0;

    //subject string
    str *string = 0;

    //the name of the lastindex group, if it has one
    str *lastgroup = 0;

    //functions
    str *expand(str *tpl);

    str *group(__ss_int n, __ss_int m = 0);
    str *group(__ss_int n, str *m);
    str *__getitem__(__ss_int n);
    str *__getitem__(str *mname);

    template <class T1, class T2, class ... Args> tuple<str *> *group(__ss_int, T1 m, T2 o, Args ... args) {
        tuple<str *> *t = new tuple<str *>();

        t->units.push_back(group(1, m));
        t->units.push_back(group(1, o));

        (t->units.push_back(group(1, args)), ...);

        return t;
    }

    dict<str *, str *> *groupdict(str *defval = 0);
    tuple2<str *, str *> *groups(str *defval = 0);

    __ss_int __index(__ss_int matchid, char isend);
    __ss_int __index(str *mname, char isend);

    __ss_int end(__ss_int matchid = 0);
    __ss_int end(str *mname);
    __ss_int start(__ss_int matchid = 0);
    __ss_int start(str *mname);
    tuple2<__ss_int, __ss_int> *span(__ss_int matchid = 0);
    tuple2<__ss_int, __ss_int> *span(str *mname);

    str *__expand(__template *t);
    str *__repr__();
};


//compiled regular expression
class Pattern : public pyobj
{
public:

    //note: all members are default-initialized, so that directly
    //constructing re.Pattern() (which CPython disallows) stays harmless

    //named captured subpatterns
    dict<str *, __ss_int> *groupindex = 0;

    //how many captured subpatterns there are
    __ss_int capture_count = 0;

    //the original pattern
    str *pattern = 0;

    //the flags used (as given to compile, and after parsing)
    __ss_int flags = 0, flags_given = 0;

    //number of captured groups
    __ss_int groups = 0;

    //the compiled pattern (code for the sre engine)
    std::vector<unsigned int, __ss_allocator<unsigned int> > code;

    //group names by index (0 if unnamed), for Match.lastgroup
    std::vector<str *, __ss_allocator<str *> > indexgroup;

    //internal functions
    __template *__compile_template(str *tpl);
    Match *__exec(str *subj, __ss_int pos, ptrdiff_t endpos, int mode);
    list<str *> *__findall(str *subj, __ss_int pos, ptrdiff_t endpos);
    str *__subx(__template *tpl, replfunc func, str *subj, __ss_int maxn, __ss_int *howmany);

    //endpos is __ss_void when not given (no limit); any given endpos is
    //clamped, like in CPython
    Match *match(str *subj, __ss_int pos = 0, __ss_void_struct endpos = {});
    Match *match(str *subj, __ss_int pos, __ss_int endpos);
    Match *prefixmatch(str *subj, __ss_int pos = 0, __ss_void_struct endpos = {});
    Match *prefixmatch(str *subj, __ss_int pos, __ss_int endpos);
    Match *fullmatch(str *subj, __ss_int pos = 0, __ss_void_struct endpos = {});
    Match *fullmatch(str *subj, __ss_int pos, __ss_int endpos);
    Match *search(str *subj, __ss_int pos = 0, __ss_void_struct endpos = {});
    Match *search(str *subj, __ss_int pos, __ss_int endpos);
    __iter<Match *> *finditer(str *subj, __ss_int pos = 0, __ss_void_struct endpos = {});
    __iter<Match *> *finditer(str *subj, __ss_int pos, __ss_int endpos);
    list<str *> *split(str *subj, __ss_int maxn = 0);
    str *sub(str *repl, str *subj, __ss_int maxn = 0);
    str *sub(replfunc repl, str *subj, __ss_int maxn = 0);
    tuple2<str *, __ss_int> *subn(str *repl, str *subj, __ss_int maxn = 0);
    tuple2<str *, __ss_int> *subn(replfunc repl, str *subj, __ss_int maxn = 0);
    list<str *> *findall(str *subj, __ss_int pos = 0, __ss_void_struct endpos = {});
    list<str *> *findall(str *subj, __ss_int pos, __ss_int endpos);

    str *__repr__();
};

class match_iter : public __iter<Match *>
{
public:
    Pattern *ro;
    str *subj;
    ptrdiff_t pos, endpos; //Py_ssize_t (sre)
    __ss_int start; //start: where the next search begins (-1: exhausted)
    int must_advance;

    match_iter(Pattern *ro, str *subj, ptrdiff_t pos, ptrdiff_t endpos);
    Match *__next__();
};

Pattern *compile(str *pat, __ss_int flags = 0);

Match *match(str *pat, str *subj, __ss_int flags = 0);
Match *prefixmatch(str *pat, str *subj, __ss_int flags = 0);
Match *fullmatch(str *pat, str *subj, __ss_int flags = 0);
Match *search(str *pat, str *subj, __ss_int flags = 0);
__iter<Match *> *finditer(str *pat, str *subj, __ss_int flags = 0);
list<str *> *split(str *pat, str *subj, __ss_int maxn = 0, __ss_int flags = 0);
str *sub(str *pat, str *repl, str *subj, __ss_int maxn = 0, __ss_int flags_ = 0);
str *sub(str *pat, replfunc repl, str *subj, __ss_int maxn = 0, __ss_int flags_ = 0);
tuple2<str *, __ss_int> *subn(str *pat, str *repl, str *subj, __ss_int maxn = 0, __ss_int flags_ = 0);
tuple2<str *, __ss_int> *subn(str *pat, replfunc repl, str *subj, __ss_int maxn = 0, __ss_int flags_ = 0);
list<str *> *findall(str *pat, str *subj, __ss_int flags = 0);
str *escape(str *s);

void *purge();

//internal functions
void __init(void);

}
#endif
