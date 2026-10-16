/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

/* the re module, on top of CPython's own sre engine (see sre/): patterns are
   parsed and compiled by a port of CPython's re._parser/re._compiler
   (sre/compile.hpp), and the scanning loops below follow those of sre.c */

#include <stdint.h>
#include <algorithm>
#include "re.hpp"
#include "sre/sre_engine.h"
#include "sre/compile.hpp"

namespace __re__ {

//flags
const __ss_int
    NOFLAG = 0,
    I = 0x02, IGNORECASE    = 0x02,
    L = 0x04, LOCALE        = 0x04,
    M = 0x08, MULTILINE     = 0x08,
    S = 0x10, DOTALL        = 0x10,
    U = 0x20, __ss_UNICODE  = 0x20,
    X = 0x40, VERBOSE       = 0x40,
    DEBUG = 0x80,
    A = 0x100, ASCII         = 0x100;

class_ *cl_error;

PatternError::PatternError(str *msg, str *pattern, __ss_int pos) : Exception(msg) {
    this->msg = msg;
    this->pattern = pattern;
    this->pos = this->lineno = this->colno = 0;

    //CPython: msg + " at position N" (+ " (line L, column C)" if multi-line)
    if(pattern && pos >= 0) {
        const __GC_STR &p = pattern->unit;
        size_t n = std::min((size_t)pos, p.size());
        __ss_int lineno = 1, lastnl = -1;
        for(size_t i = 0; i < n; i++)
            if(p[i] == '\n') { lineno++; lastnl = (__ss_int)i; }

        this->pos = pos;
        this->lineno = lineno;
        this->colno = pos - lastnl;

        __GC_STR full = msg->unit;
        full += __gcs(" at position ") + __gcs(std::to_string(pos));
        if(p.find('\n') != __GC_STR::npos)
            full += __gcs(" (line ") + __gcs(std::to_string(lineno)) + __gcs(", column ") + __gcs(std::to_string(this->colno)) + __gcs(")");
        __init__(new str(full));
    }
}

//engine state for a subject string (sre.c: state_init/state_fini)
struct __state {
    SRE_STATE s;
    Pattern *p;
    __state(Pattern *p, str *subj, Py_ssize_t pos, Py_ssize_t endpos) : p(p) {
        state_init(&s, p->groups, (const Py_UCS4 *)subj->unit.data(), (Py_ssize_t)subj->unit.size(), pos, endpos);
    }
    ~__state() { state_fini(&s); }
    __ss_int offset(const void *ptr) { return (__ss_int)STATE_OFFSET(&s, ptr); }
    Py_ssize_t search() {
        state_reset(&s);
        s.ptr = s.start;
        return check(sre_ucs4_search(&s, p->code.data()));
    }
    Py_ssize_t match() {
        state_reset(&s);
        s.ptr = s.start;
        return check(sre_ucs4_match(&s, p->code.data(), 1));
    }
    Py_ssize_t check(Py_ssize_t status) {
        if(status == SRE_ERROR_MEMORY) throw new MemoryError();
        if(status < 0) throw new RuntimeError(new str("internal error in regular expression engine"));
        return status;
    }
    //a group's slice of the subject, or 0 if it did not participate (sre.c: state_getslice)
    str *getslice(str *subj, __ss_int index, bool empty) {
        index = (index - 1) * 2;
        if(index >= s.lastmark || !s.mark[index] || !s.mark[index + 1])
            return empty ? new str() : 0;
        __ss_int i = offset(s.mark[index]), j = offset(s.mark[index + 1]);
        return new str(subj->unit.substr(i, j - i));
    }
    //make the next search start where the last match ended
    void advance() {
        s.must_advance = (s.ptr == s.start);
        s.start = s.ptr;
    }
};

//sre.c: pattern_new_match
static Match *__new_match(Pattern *p, __state &st, str *subj) {
    Match *m = new Match();
    m->re = p;
    m->string = subj;
    m->pos = st.s.pos;
    m->endpos = st.s.endpos;
    m->regs.resize(2 * (p->groups + 1));
    m->regs[0] = st.offset(st.s.start);
    m->regs[1] = st.offset(st.s.ptr);
    for(__ss_int i = 0, j = 0; i < p->groups; i++, j += 2) {
        if(j + 1 <= st.s.lastmark && st.s.mark[j] && st.s.mark[j + 1]) {
            m->regs[j + 2] = st.offset(st.s.mark[j]);
            m->regs[j + 3] = st.offset(st.s.mark[j + 1]);
        } else
            m->regs[j + 2] = m->regs[j + 3] = -1;
    }
    m->lastindex = st.s.lastindex >= 0 ? st.s.lastindex : 0;
    if(st.s.lastindex >= 0 && st.s.lastindex < (int)p->indexgroup.size())
        m->lastgroup = p->indexgroup[st.s.lastindex];
    return m;
}

//Match functions
static __ss_int __groupid(Match *m, __ss_int matchid) {
    if(matchid > m->re->groups || matchid < 0) throw new IndexError(new str("no such group"));
    return matchid;
}

static __ss_int __groupid(Match *m, str *mname) {
    if(!m->re->groupindex->has_key(mname)) throw new IndexError(new str("no such group"));
    return m->re->groupindex->__getitem__(mname);
}

str *Match::group(__ss_int /* n */, __ss_int matchid)
{
    __groupid(this, matchid);
    if(regs[2 * matchid] == -1) return 0; // group exists but did not participate in the match
    return new str(string->unit.substr(regs[2 * matchid], regs[2 * matchid + 1] - regs[2 * matchid]));
}

str *Match::group(__ss_int /* n */, str *mname)
{
    return group(0, __groupid(this, mname));
}

str *Match::__getitem__(__ss_int g) {
    return group(0, g);
}

str *Match::__getitem__(str *mname) {
    return group(0, mname);
}

//index functions
__ss_int Match::__index(__ss_int matchid, char isend)
{
    return regs[2 * __groupid(this, matchid) + isend];
}

__ss_int Match::__index(str *mname, char isend)
{
    return __index(__groupid(this, mname), isend);
}

__ss_int Match::end(__ss_int matchid)
{
    return __index(matchid, 1);
}

__ss_int Match::end(str *mname)
{
    return __index(mname, 1);
}

__ss_int Match::start(__ss_int matchid)
{
    return __index(matchid, 0);
}

__ss_int Match::start(str *mname)
{
    return __index(mname, 0);
}

tuple2<__ss_int, __ss_int> *Match::span(__ss_int matchid)
{
    return new tuple2<__ss_int, __ss_int>(2, start(matchid), end(matchid));
}
tuple2<__ss_int, __ss_int> *Match::span(str *mname)
{
    return new tuple2<__ss_int, __ss_int>(2, start(mname), end(mname));
}

str *Match::expand(str *tpl)
{
    return __expand(re->__compile_template(tpl));
}

tuple2<str *, str *> *Match::groups(str *defval)
{
    tuple<str *> *r = new tuple<str *>();

    for(__ss_int i = 1; i <= re->groups; i++) {
        str *g = group(0, i);
        r->units.push_back(g ? g : defval);
    }

    return r;
}

dict<str *, str *> *Match::groupdict(str *defval)
{
    dict<str *, str *> *r = new dict<str *, str *>();

    for(size_t i = 1; i < re->indexgroup.size(); i++) {
        if(!re->indexgroup[i]) continue;
        str *g = group(0, (__ss_int)i);
        r->__setitem__(re->indexgroup[i], g ? g : defval);
    }

    return r;
}

//like CPython's %.<n>R: a repr, cut off after n characters
static __GC_STR __repr_cut(str *s, size_t n) {
    return repr(s)->unit.substr(0, n);
}

//sre.c: match_repr
str *Match::__repr__() {
    if(!re) return new str("<Match object>"); //directly constructed
    return new str(__gcs("<re.Match object; span=(") + __gcs(std::to_string(regs[0])) + __gcs(", ") + __gcs(std::to_string(regs[1])) + __gcs("), match=") + __repr_cut(group((__ss_int)0, (__ss_int)0), 50) + __gcs(">"));
}

//sre.c: pattern_repr
str *Pattern::__repr__() {
    static const struct { const char *name; __ss_int value; } flag_names[] = {
        {"re.IGNORECASE", I}, {"re.LOCALE", L}, {"re.MULTILINE", M}, {"re.DOTALL", S},
        {"re.UNICODE", U}, {"re.VERBOSE", X}, {"re.DEBUG", DEBUG}, {"re.ASCII", A}
    };
    if(!pattern) return new str("<Pattern object>"); //directly constructed

    __GC_STR r = __gcs("re.compile(") + __repr_cut(pattern, 200);

    //omit the (default) UNICODE flag for str patterns
    __ss_int f = flags;
    if((f & (L | U | A)) == U)
        f &= ~U;
    if(f) {
        __GC_STR names;
        for(auto &fn : flag_names) {
            if(f & fn.value) {
                if(!names.empty()) names += '|';
                names += __gcs(fn.name);
                f &= ~fn.value;
            }
        }
        if(f) {
            char buf[32];
            snprintf(buf, sizeof(buf), "0x%x", (unsigned int)f);
            if(!names.empty()) names += '|';
            names += __gcs(buf);
        }
        r += __gcs(", ") + names;
    }
    return new str(r + __gcs(")"));
}

//template (sub/subn/expand) errors: like CPython, report the template as the
//pattern, plus the position in it
static inline PatternError *__tpl_error(__GC_STR msg, __GC_STR &tpl, size_t pos) {
    return new PatternError(new str(msg), new str(tpl), (__ss_int)pos);
}

static inline bool __is_octdigit(__ss_char c) { return c >= '0' && c <= '7'; }
static inline bool __is_digit(__ss_char c) { return c >= '0' && c <= '9'; }

//compile a replacement template, following CPython's _parser.parse_template
__template *Pattern::__compile_template(str *tpl_)
{
    __template *t = new __template();
    __GC_STR &tpl = tpl_->unit, lit;
    size_t i, j, len = tpl.length();
    __ss_char c;

    auto addgroup = [&](__ss_int index, size_t pos) {
        if(index > groups)
            throw __tpl_error(__gcs("invalid group reference ") + __gcs(std::to_string(index)), tpl, pos);
        t->literals.push_back(lit);
        lit.clear();
        t->groups.push_back(index);
    };

    for(i = 0; i < len; i++)
    {
        //zip past anything that we don't need to worry about
        j = i;
        while(i < len && tpl[i] != '\\') i++;
        if(i - j) lit += tpl.substr(j, i - j);

        if(i == len) break;

        //we've hit a backslash
        size_t bs = i;
        if(++i == len) throw __tpl_error(__gcs("bad escape (end of pattern)"), tpl, bs);
        c = tpl[i];

        if(c == 'g')
        {
            //named or numbered reference: \g<name>, \g<2>
            if(++i == len || tpl[i] != '<') throw __tpl_error(__gcs("missing <"), tpl, i);
            j = ++i;
            bool alldigits = true;
            while(i < len && tpl[i] != '>') alldigits = alldigits && __is_digit(tpl[i]), i++;

            if(i == len) {
                if(i == j) throw __tpl_error(__gcs("missing group name"), tpl, j);
                throw __tpl_error(__gcs("missing >, unterminated name"), tpl, j);
            }
            if(i == j) throw __tpl_error(__gcs("missing group name"), tpl, j);

            str *name = new str(tpl.substr(j, i - j));
            if(alldigits) {
                __ss_int index = 0;
                for(size_t k = j; k < i; k++)
                    index = std::min<__ss_int>(index * 10 + (tpl[k] - '0'), (__ss_int)SRE_MAXGROUPS);
                if(index >= (__ss_int)SRE_MAXGROUPS) {
                    size_t k = j;
                    while(k + 1 < i && tpl[k] == '0') k++;
                    throw __tpl_error(__gcs("invalid group reference ") + tpl.substr(k, i - k), tpl, j);
                }
                addgroup(index, j);
            }
            else if(!name->isidentifier()) throw __tpl_error(__gcs("bad character in group name ") + repr(name)->unit, tpl, j);
            else if(!groupindex->has_key(name)) throw new IndexError(new str(__gcs("unknown group name ") + repr(name)->unit));
            else addgroup(groupindex->__getitem__(name), j);
        }
        else if(c == '0')
        {
            //octal escape: \0 followed by at most two more octal digits
            __ss_char v = 0;
            for(j = 0; j < 2 && i + 1 < len && __is_octdigit(tpl[i + 1]); j++)
                v = (__ss_char)(v * 8 + (tpl[++i] - '0'));
            lit += v;
        }
        else if(__is_digit(c))
        {
            //three octal digits form an octal escape, otherwise it is a
            //group reference of at most two digits (\100 is '@', \10 is group 10)
            if(i + 2 < len && __is_octdigit(c) && __is_octdigit(tpl[i + 1]) && __is_octdigit(tpl[i + 2]))
            {
                __ss_char v = (__ss_char)((c - '0') * 64 + (tpl[i + 1] - '0') * 8 + (tpl[i + 2] - '0'));
                if(v > 0377) throw __tpl_error(__gcs("octal escape value \\") + tpl.substr(i, 3) + __gcs(" outside of range 0-0o377"), tpl, bs);
                lit += v;
                i += 2;
            }
            else
            {
                __ss_int ref = (__ss_int)(c - '0');
                size_t refpos = i;
                if(i + 1 < len && __is_digit(tpl[i + 1]))
                    ref = ref * 10 + (__ss_int)(tpl[++i] - '0');
                addgroup(ref, refpos);
            }
        }
        else
        {
            switch(c)
            {
                case 'n' : lit += '\n'; break;
                case 'v' : lit += '\v'; break;
                case 'a' : lit += '\a'; break;
                case 'b' : lit += '\b'; break;
                case 'f' : lit += '\f'; break;
                case 't' : lit += '\t'; break;
                case 'r' : lit += '\r'; break;
                case '\\': lit += '\\'; break;
                default:
                    //unknown ascii letter escapes are errors (CPython 3.7+),
                    //anything else is kept as is, including the backslash
                    if((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'))
                    {
                        __GC_STR msg = __gcs("bad escape \\");
                        msg += c;
                        throw __tpl_error(msg, tpl, bs);
                    }
                    lit += '\\';
                    lit += c;
            }
        }
    }
    t->literals.push_back(lit);

    return t;
}

//expand a compiled template (sre.c: expand_template)
str *Match::__expand(__template *t)
{
    __GC_STR out = t->literals[0];
    for(size_t i = 0; i < t->groups.size(); i++) {
        __ss_int g = t->groups[i];
        if(regs[2 * g] != -1) //a group that did not participate expands to an empty string
            out += string->unit.substr(regs[2 * g], regs[2 * g + 1] - regs[2 * g]);
        out += t->literals[i + 1];
    }
    return new str(out);
}

//sub/subn, with either a template or a function (sre.c: pattern_subx)
str *Pattern::__subx(__template *tpl, replfunc func, str *subj, __ss_int maxn, __ss_int *howmany)
{
    __state st(this, subj, 0, PY_SSIZE_T_MAX);
    __GC_STR out;
    __ss_int n = 0, i = 0;

    while(!maxn || n < maxn) {
        if(!st.search()) break;

        __ss_int b = st.offset(st.s.start), e = st.offset(st.s.ptr);

        //get segment before this match
        if(i < b) out += subj->unit.substr(i, b - i);

        if(tpl && tpl->groups.empty())
            out += tpl->literals[0];
        else {
            Match *m = __new_match(this, st, subj);
            str *item = tpl ? m->__expand(tpl) : func(m);
            if(item) out += item->unit;
        }

        i = e;
        n = n + 1;
        st.advance();
    }

    //get segment following last match
    if(i < st.s.endpos) out += subj->unit.substr(i, st.s.endpos - i);

    if(howmany) *howmany = n;
    return new str(out);
}

str *Pattern::sub(str *repl, str *subj, __ss_int maxn)
{
    return __subx(__compile_template(repl), 0, subj, maxn, 0);
}

str *Pattern::sub(replfunc func, str *subj, __ss_int maxn)
{
    return __subx(0, func, subj, maxn, 0);
}

tuple2<str *, __ss_int> *Pattern::subn(str *repl, str *subj, __ss_int maxn)
{
    __ss_int n;
    str *r = __subx(__compile_template(repl), 0, subj, maxn, &n);
    return new tuple2<str *, __ss_int>(2, r, n);
}

tuple2<str *, __ss_int> *Pattern::subn(replfunc func, str *subj, __ss_int maxn)
{
    __ss_int n;
    str *r = __subx(0, func, subj, maxn, &n);
    return new tuple2<str *, __ss_int>(2, r, n);
}

//sre.c: _sre_SRE_Pattern_split_impl
list<str *> *Pattern::split(str *subj, __ss_int maxn)
{
    __state st(this, subj, 0, PY_SSIZE_T_MAX);
    list<str *> *r = new list<str *>();
    __ss_int n = 0, last = 0;

    while(!maxn || n < maxn) {
        if(!st.search()) break;

        //get segment before this match
        __ss_int b = st.offset(st.s.start);
        r->append(new str(subj->unit.substr(last, b - last)));

        //add groups (if any)
        for(__ss_int i = 0; i < groups; i++)
            r->append(st.getslice(subj, i + 1, false));

        n = n + 1;
        st.advance();
        last = st.offset(st.s.start);
    }

    //get segment following last match (even if empty)
    r->append(new str(subj->unit.substr(last, st.s.endpos - last)));
    return r;
}

//sre.c: _sre_SRE_Pattern_findall_impl (with several groups, CPython returns
//tuples, which shedskin does not support; the whole match is returned then)
list<str *> *Pattern::__findall(str *subj, __ss_int pos, Py_ssize_t endpos)
{
    __state st(this, subj, pos, endpos);
    list<str *> *r = new list<str *>();

    while(st.s.start <= st.s.end) {
        if(!st.search()) break;

        if(groups == 1)
            r->append(st.getslice(subj, 1, true));
        else {
            __ss_int b = st.offset(st.s.start), e = st.offset(st.s.ptr);
            r->append(new str(subj->unit.substr(b, e - b)));
        }

        st.advance();
    }

    return r;
}

//finditer (sre.c: the scanner object, with its search method)
match_iter::match_iter(Pattern *ro_, str *subj_, Py_ssize_t pos_, Py_ssize_t endpos_)
{
    this->ro = ro_;
    this->subj = subj_;
    this->pos = pos_;
    this->endpos = endpos_;
    this->start = -2; //not started
    this->must_advance = 0;
}

Match *match_iter::__next__(void)
{
    if(start == -1) throw new StopIteration();

    __state st(ro, subj, pos, endpos);
    if(start != -2) {
        st.s.start = (const Py_UCS4 *)st.s.beginning + start;
        st.s.must_advance = must_advance;
    }

    if(!st.search()) {
        start = -1;
        throw new StopIteration();
    }

    Match *m = __new_match(ro, st, subj);
    st.advance();
    start = st.offset(st.s.start);
    must_advance = st.s.must_advance;
    return m;
}


//match (mode 1), fullmatch (mode 2) or search (mode 0)
Match *Pattern::__exec(str *subj, __ss_int pos, Py_ssize_t endpos, int mode)
{
    __state st(this, subj, pos, endpos);
    st.s.match_all = (mode == 2);
    if(!(mode ? st.match() : st.search()))
        return 0;
    return __new_match(this, st, subj);
}

//endpos not given (__ss_void) means no limit
Match *Pattern::match(str *subj, __ss_int pos, __ss_void_struct) { return __exec(subj, pos, PY_SSIZE_T_MAX, 1); }
Match *Pattern::match(str *subj, __ss_int pos, __ss_int endpos) { return __exec(subj, pos, endpos, 1); }
Match *Pattern::prefixmatch(str *subj, __ss_int pos, __ss_void_struct) { return __exec(subj, pos, PY_SSIZE_T_MAX, 1); }
Match *Pattern::prefixmatch(str *subj, __ss_int pos, __ss_int endpos) { return __exec(subj, pos, endpos, 1); }
Match *Pattern::fullmatch(str *subj, __ss_int pos, __ss_void_struct) { return __exec(subj, pos, PY_SSIZE_T_MAX, 2); }
Match *Pattern::fullmatch(str *subj, __ss_int pos, __ss_int endpos) { return __exec(subj, pos, endpos, 2); }
Match *Pattern::search(str *subj, __ss_int pos, __ss_void_struct) { return __exec(subj, pos, PY_SSIZE_T_MAX, 0); }
Match *Pattern::search(str *subj, __ss_int pos, __ss_int endpos) { return __exec(subj, pos, endpos, 0); }
list<str *> *Pattern::findall(str *subj, __ss_int pos, __ss_void_struct) { return __findall(subj, pos, PY_SSIZE_T_MAX); }
list<str *> *Pattern::findall(str *subj, __ss_int pos, __ss_int endpos) { return __findall(subj, pos, endpos); }
__iter<Match *> *Pattern::finditer(str *subj, __ss_int pos, __ss_void_struct) { return new match_iter(this, subj, pos, PY_SSIZE_T_MAX); }
__iter<Match *> *Pattern::finditer(str *subj, __ss_int pos, __ss_int endpos) { return new match_iter(this, subj, pos, endpos); }


//re.* functions

//like CPython, keep the most recently used compiled patterns around
static const size_t __CACHE_SIZE = 256;
static Pattern *__cache[__CACHE_SIZE];

Pattern *compile(str *pat, __ss_int flags)
{
    size_t slot = ((size_t)pat->__hash__() ^ (size_t)flags * 0x9e3779b9u) % __CACHE_SIZE;
    Pattern *c = __cache[slot];
    if(c && c->flags_given == flags && c->pattern->unit == pat->unit)
        return c;

    __sre::Code code;
    int outflags, groups;
    std::vector<std::pair<__GC_STR, int> > names;
    __sre::compile_pattern(pat, (int)flags, code, outflags, groups, names);

    Pattern *p = new Pattern();
    p->pattern = pat;
    p->flags = outflags;
    p->flags_given = flags;
    p->groups = p->capture_count = groups;
    p->code.assign(code.begin(), code.end());
    p->groupindex = new dict<str *, __ss_int>();
    p->indexgroup.assign(groups + 1, 0);
    for(auto &name : names) {
        str *s = new str(name.first);
        p->groupindex->__setitem__(s, name.second);
        p->indexgroup[name.second] = s;
    }

    __cache[slot] = p;
    return p;
}

void *purge() {
    std::fill(__cache, __cache + __CACHE_SIZE, (Pattern *)0);
    return NULL;
}

str *escape(str *s)
{
    //like CPython (3.7+), only escape characters that are special in regular
    //expressions; e.g. '_', '!', '@', '"' or ':' are left alone
    static const char special[] = "()[]{}?*+-|^$\\.&~# \t\n\r\v\f";
    __GC_STR *ps, out;
    size_t i, len;
    __ss_char c;

    ps = &s->unit;
    len = ps->size();
    out = __GC_STR();

    for(i = 0; i < len; i++)
    {
        c = (*ps)[i];
        if(c < 128 && c != 0 && strchr(special, (int)c))
            out += '\\';
        out += c;
    }

    return new str(out);
}

Match *search(str *pat, str *subj, __ss_int flags)
{
    return compile(pat, flags)->search(subj);
}

Match *match(str *pat, str *subj, __ss_int flags)
{
    return compile(pat, flags)->match(subj);
}

Match *prefixmatch(str *pat, str *subj, __ss_int flags)
{
    return match(pat, subj, flags);
}

Match *fullmatch(str *pat, str *subj, __ss_int flags)
{
    return compile(pat, flags)->fullmatch(subj);
}

__iter<Match *> *finditer(str *pat, str *subj, __ss_int flags)
{
    return compile(pat, flags)->finditer(subj);
}

str *sub(str *pat, str *repl, str *subj, __ss_int maxn, __ss_int flags)
{
    return compile(pat, flags)->sub(repl, subj, maxn);
}

str *sub(str *pat, replfunc func, str *subj, __ss_int maxn, __ss_int flags)
{
    return compile(pat, flags)->sub(func, subj, maxn);
}

tuple2<str *, __ss_int> *subn(str *pat, str *repl, str *subj, __ss_int maxn, __ss_int flags)
{
    return compile(pat, flags)->subn(repl, subj, maxn);
}

tuple2<str *, __ss_int> *subn(str *pat, replfunc func, str *subj, __ss_int maxn, __ss_int flags)
{
    return compile(pat, flags)->subn(func, subj, maxn);
}

list<str *> *split(str *pat, str *subj, __ss_int maxn, __ss_int flags)
{
    return compile(pat, flags)->split(subj, maxn);
}

list<str *> *findall(str *pat, str *subj, __ss_int flags)
{
    return compile(pat, flags)->findall(subj);
}

void __init(void)
{
    cl_error = new class_("error");
}

}
