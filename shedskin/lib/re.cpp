#include "re.hpp"

namespace __re__ {

//flags
const __ss_int
    I = 0x02, IGNORECASE    = 0x02,
    L = 0x04, LOCALE        = 0x04,
    M = 0x08, MULTILINE     = 0x08,
    S = 0x10, DOTALL        = 0x10,
    U = 0x20, __ss_UNICODE  = 0x20,
    X = 0x40, VERBOSE       = 0x40;

const unsigned char *local_table;

//match_object functions
str *match_object::group(__ss_int /* n */, __ss_int matchid)
{
    return new str(re->__group(&string->unit, captured, matchid));
}

str *match_object::group(__ss_int /* n */, str *mname)
{
    return new str(re->__group(&string->unit, captured, mname));
}

tuple2<str *, str *> *match_object::group(__ss_int n, __ss_int m, __ss_int o, ...) {
    tuple2<str *, str *> *t = new tuple2<str *, str *>();
    va_list ap;
    va_start(ap, o);
    t->units.push_back(group(1, m));
    t->units.push_back(group(1, o));
    for(__ss_int i=0; i<n-2; i++)
        t->units.push_back(group(1, va_arg(ap, __ss_int)));
    va_end(ap);
    return t;
}

tuple2<str *, str *> *match_object::group(__ss_int n, str *m, str *o, ...) {
    tuple2<str *, str *> *t = new tuple2<str *, str *>();
    va_list ap;
    va_start(ap, o);
    t->units.push_back(group(1, m));
    t->units.push_back(group(1, o));
    for(__ss_int i=0; i<n-2; i++)
        t->units.push_back(group(1, va_arg(ap, str *)));
    va_end(ap);
    return t;
}

//index functions
__ss_int match_object::__index(__ss_int matchid, char isend)
{
    if(matchid > lastindex) throw new error(new str("group does not exist or is unmatched"));

    return captured[matchid * 2 + isend];
}

__ss_int match_object::__index(str *mname, char isend)
{
    if(!re->groupindex->has_key(mname)) throw new error(new str("no such group exists"));

    return __index(re->groupindex->__getitem__(mname), isend);
}

__ss_int match_object::end(__ss_int matchid)
{
    return __index(matchid, 1);
}

__ss_int match_object::end(str *mname)
{
    return __index(mname, 1);
}

__ss_int match_object::start(__ss_int matchid)
{
    return __index(matchid, 0);
}

__ss_int match_object::start(str *mname)
{
    return __index(mname, 0);
}

str *match_object::expand(str *tpl)
{
    return new str(re->__expand(&string->unit, captured, tpl->unit));
}

tuple2<str *, str *> *match_object::groups(str *defval)
{
    tuple2<str *, str *> *r;
    int i;

    r = new tuple2<str *, str *>();

    for(i = 1; i <= re->capture_count; i++)
    {
        if(captured[i * 2] != -1)
            r->units.push_back(new str(string->unit.substr(captured[i * 2], captured[i * 2 + 1] - captured[i * 2])));

        else r->units.push_back(defval ? new str(defval->unit) : 0);
    }

    return r;
}

dict<str *, str *> *match_object::groupdict(str *defval)
{
    dict<str *, str *> *r;
    int t;
    r = new dict<str *, str *>();
    str *k;
    dict<str *, __ss_int>::for_in_loop __3;
    int __2;
    dict<str *, __ss_int> *__1;
    FOR_IN_NEW(k,re->groupindex,1,2,3)
        t = re->groupindex->__getitem__(k);

        if(captured[t * 2] != -1) r->__setitem__(new str(k->unit),
            new str(string->unit.substr(captured[t * 2], captured[t * 2 + 1] - captured[t * 2])));

        else r->__setitem__(new str(k->unit), defval ? new str(defval->unit) : 0);
    END_FOR

    return r;
}

str *match_object::__repr__() {
    return new str("<match_object>");
}

str *re_object::__repr__() {
    return new str("<re_object>");
}

//these are for internal use
__GC_STRING re_object::__group(__GC_STRING *subj, int *captured, __ss_int matchid)
{
    if(matchid > capture_count || matchid < 0) throw new error(new str("group does not exist"));
    if(captured[matchid * 2] == -1) throw new error(new str("group is unmatched"));

    return subj->substr(captured[matchid * 2], captured[matchid * 2 + 1] - captured[matchid * 2]);
}

__GC_STRING re_object::__group(__GC_STRING *subj, int *captured, str *mname)
{
    if(!groupindex->has_key(mname)) throw new error(new str("no such group exists"));

    return __group(subj, captured, groupindex->__getitem__(mname));
}

__GC_STRING re_object::__expand(__GC_STRING *subj, int *captured, __GC_STRING tpl)
{
    __GC_STRING out;
    int i, j, len, ref;
    char c;

    out = "";
    len = tpl.length();

    for(i = 0; i < len; i++)
    {
        //zip past anything that we don't need to worry about
        j = i;
        while(tpl[i] != '\\' && i < len) i++;
        if(i - j) out += tpl.substr(j, i - j);

        if(i == len) break;

        //we've hit a backslash
        switch(tpl[++i])
        {
            //reference
            case '1' :
            case '2' :
            case '3' :
            case '4' :
            case '5' :
            case '6' :
            case '7' :
            case '8' :
            case '9' :

                j = i;
                while(isdigit(tpl[i]) && i < len) i++;

                ref = strtol(tpl.substr(j, i - j).c_str(), 0, 10);
                out += __group(subj, captured, ref);

                i--;
                continue;

            //named reference
            case 'g' :

                if(tpl[++i] != '<') throw new error(new str("invalid name group"));
                i++;

                j = i;
                c = 1;
                while(tpl[i] != '>' && i < len) c = c && ::isdigit((int)tpl[i]), i++;

                if(tpl[i] != '>') throw new error(new str("unterminated name group"));
                if(::isdigit((int)tpl[j]) && !c) throw new error(new str("invalid first character in name group"));

                if(c) out += __group(subj, captured, strtol(tpl.substr(j, i - j).c_str(), 0, 10));
                else out += __group(subj, captured, new str(tpl.substr(j, i - j)));

                continue;

            //escape char
            case 'n' : c = '\n'; break;
            case 'v' : c = '\v'; break;
            case 'a' : c = '\a'; break;
            case 'b' : c = '\b'; break;
            case 'f' : c = '\f'; break;
            case 't' : c = '\t'; break;
            case 'r' : c = '\r'; break;

            //nothing meaningful here, ignore
            default :
                c = 0;
        }

        if(c) out += c;
        else
        {
            out += '\\';
            i--;
        }
    }

    return out;
}



//replacing pcre's allocation functions with ours using the garbage collector
void *re_malloc(size_t n)
{
    return GC_MALLOC(n);
}

void re_free(void *o)
{
    GC_FREE(o);
}

str *re_object::__subn(str *repl, str *subj, __ss_int maxn, int *howmany)
{
    __GC_STRING *s, out;
    int *captured, clen, i, cur;
    const char *c_subj;

    //temporary data
    clen = (capture_count + 1) * 2 * 3;
    captured = (int *)GC_MALLOC(clen * sizeof(int));

    out = "";

    s = &subj->unit;
    c_subj = s->c_str();
    for(cur = i = 0; maxn <= 0 || cur < maxn; cur++)
    {
        //get a match
        if(pcre_exec(
            compiled_pattern,
            study_info,
            c_subj,
            s->size(),
            i,
            0,
            captured,
            clen
        ) <= 0) break;

        //append stuff we skipped
        out += s->substr(i, captured[0] - i);

        //replace section
        out += __expand(s, captured, repl->unit);

        //move our index
        if(i == captured[1]) i++;
        else i = captured[1];
    }

    //extra
    out += s->substr(i);
    if(howmany) *howmany = cur;

    GC_FREE(captured);

    return new str(out);
}

str *re_object::sub(str *repl, str *subj, __ss_int maxn)
{
    return __subn(repl, subj, maxn, 0);
}

str *re_object::sub(replfunc func, str *string, __ss_int maxn) {
    list<str *> *l;
    int at;

    at = 0;
    l = (new list<str *>());

    __re__::match_object *match;
    __iter<__re__::match_object *>::for_in_loop __3;
    int __2;
    __iter<__re__::match_object *> *__1;

    FOR_IN_NEW(match,finditer(string),1,2,3)
        l->append(string->__slice__(3, at, match->start(), 0));
        l->append(func(match));
        at = match->end();
        if ((maxn>0)) {
            maxn = (maxn-1);
            if ((maxn==0)) {
                break;
            }
        }
    END_FOR

    l->append(string->__slice__(1, at, 0, 0));
    return (new str(""))->join(l);
}


tuple2<str *, __ss_int> *re_object::subn(str *repl, str *subj, __ss_int maxn)
{
    str *r;
    int n;

    r = __subn(repl, subj, maxn, &n);

    return new tuple2<str *, __ss_int>(2, r, n);
}

list<str *> *re_object::__splitfind(str *subj, __ss_int maxn, char onlyfind, __ss_int flags)
{
    __GC_STRING *subjs;
    list<str *> *r;
    int *captured, clen, i, j, cur;
    const char *c_subj;

    //temporary data
    clen = (capture_count + 1) * 2 * 3;
    captured = (int *)GC_MALLOC(clen * sizeof(int));

    //'permanent' (in respect to the lifetime of this function)
    r = new list<str *>();

    subjs = &subj->unit;
    c_subj = subjs->c_str();
    for(cur = i = 0; maxn <= 0 || cur < maxn; cur++)
    {
        //get a match
        if(pcre_exec(
            compiled_pattern,
            study_info,
            c_subj,
            subjs->size(),
            i,
            flags,
            captured,
            clen
        ) <= 0) break;

        //this whole subroutine is very similar to findall, so we might as well save some code and merge them...
        if(onlyfind)
        {
            r->append(new str(subjs->substr(captured[0], captured[1] - captured[0])));

            //for split we ignore zero-length matches, but findall dosn't
            if(captured[1] == captured[0]) captured[1]++;
        }
        else
        {
            //is it worth it?
            if(captured[1] == i)
            {
                cur--;
                i++;
                continue;
            }

            //append block of text
            r->append(new str(subjs->substr(i, captured[0] - i)));

            //append all the submatches to list
            for(j = 1; j <= capture_count; j++)
            {
                if(captured[j * 2] != -1) r->append(new str(subjs->substr(captured[j * 2], captured[j * 2 + 1] - captured[j * 2])));
                else r->append(0); //should this be new str() ?
            }
        }

        //move our index
        i = captured[1];
    }

    if(!onlyfind) r->append(new str(subjs->substr(i)));

    GC_FREE(captured);

    return r;
}

list<str *> *re_object::split(str *subj, __ss_int maxn)
{
    return __splitfind(subj, maxn, 0, 0);
}

list<str *> *re_object::findall(str *subj, __ss_int flags)
{
    return __splitfind(subj, -1, 1, flags);
}

match_iter::match_iter(re_object *ro, str *subj, __ss_int pos, __ss_int endpos, __ss_int flags)
{
    this->subj = subj;
    this->pos = pos;
    this->endpos = endpos;
    this->flags = flags;
    this->ro = ro;
}

match_object *match_iter::next(void)
{
    match_object *mobj;

    if((pos > endpos && endpos != -1) || (unsigned int)pos >= subj->unit.size()) throw new StopIteration();

    //get next match
    mobj = ro->__exec(subj, pos, endpos, flags);
    if(!mobj) throw new StopIteration();

    if(mobj->captured[1] == pos) pos++;
    else pos = mobj->captured[1];

    return mobj;
}

__iter<match_object *> *re_object::finditer(str *subj, __ss_int pos, __ss_int endpos, __ss_int flags)
{
    if(endpos < pos && endpos != -1) throw new error(new str("end position less than initial"));
    if((unsigned int)pos >= subj->unit.size()) throw new error(new str("starting position >= string length"));

    return new match_iter(this, subj, pos, endpos, flags);
}

match_object *re_object::__exec(str *subj, __ss_int pos, __ss_int endpos, __ss_int flags)
{
    match_object *mobj;
    int *captured, clen, r, t, mx_i, nendpos;
    str *mx_s;
    mx_s = NULL;

    //allocate captured array
    clen = (capture_count + 1) * 2 * 3;
    captured = (int *)GC_MALLOC(clen * sizeof(int));

    //sanity checking
    if(endpos == -1) nendpos = subj->unit.size() - 1;
    else if(endpos < pos) throw new error(new str("end position less than initial"));
    else nendpos = endpos;

    if((unsigned int)pos >= subj->unit.size()) throw new error(new str("starting position >= string length"));

    r = pcre_exec(
        compiled_pattern,
        study_info,
        subj->unit.c_str(),
        nendpos + 1,
        pos,
        flags,
        captured,
        clen
    );

    //no match was found (dont have to worry about freeing thanks to the garbage collector)
    if(r < 0) return (match_object *)NULL;

    //create object now that we know we're successful
    mobj = new match_object();
    mobj->re = this;

    //extra info
    mobj->captured = captured;
    mobj->pos = pos;
    mobj->endpos = endpos;
    mobj->string = subj;
    mobj->lastindex = r - 1;

    //find lastgroup
    mx_i = -1;

    str *k;
    dict<str *, __ss_int>::for_in_loop __3;
    int __2;
    dict<str *, __ss_int> *__1;
    FOR_IN_NEW(k,groupindex,1,2,3)
        t = groupindex->__getitem__(k);
        if(captured[t * 2] != -1 && t > mx_i)
        {
            mx_s = k;
            mx_i = t;
        }
    END_FOR
    if(mx_i != -1) mobj->lastgroup = mx_s;
    else mobj->lastgroup = 0;

    return mobj;
}

match_object *re_object::match(str *subj, __ss_int pos, __ss_int endpos)
{
    return __exec(subj, pos, endpos, PCRE_ANCHORED);
}

match_object *re_object::search(str *subj, __ss_int pos, __ss_int endpos)
{
    return __exec(subj, pos, endpos, 0);
}


//re.* functions
__ss_int __convert_flags(__ss_int flags)
{
    int ta[] = {IGNORECASE, MULTILINE, DOTALL, __ss_UNICODE, VERBOSE},
        tb[] = {PCRE_CASELESS, PCRE_MULTILINE, PCRE_DOTALL, PCRE_UTF8, PCRE_EXTENDED};
    int i, r;

    r = 0;
    for(i = sizeof(ta) / sizeof(ta[0]) - 1; i >= 0; i--)
        if(flags & ta[i]) r |= tb[i];

    return r;
}

re_object *compile(str *pat, __ss_int flags)
{
    re_object *reobj;
    __GC_STRING fullerr;
    pcre *cpat;
    char *errmsg, *nametable;
    int options, erroff, ntlen, nteach, i;

    //convert flags
    options = __convert_flags(flags);

    //attempt a compilation
    cpat = pcre_compile(
        pat->unit.c_str(),
        options,
        (const char **)&errmsg,
        &erroff,
        (flags & LOCALE ? local_table : 0)
    );

    //...
    if(!cpat)
    {
        fullerr = "char " + erroff;
        fullerr += ":";
        fullerr += errmsg;

        throw new error(new str(fullerr));
    }

    //everythings ok, create object
    reobj = new re_object();
    reobj->compiled_pattern = cpat;

    //might as well study it
    reobj->study_info = pcre_study(cpat, 0, (const char **)&errmsg);

    //any named indices?
    reobj->groupindex = new dict<str *, __ss_int>();

    pcre_fullinfo(cpat, reobj->study_info, PCRE_INFO_NAMECOUNT, (void *)&ntlen);
    pcre_fullinfo(cpat, reobj->study_info, PCRE_INFO_NAMEENTRYSIZE, (void *)&nteach);
    pcre_fullinfo(cpat, reobj->study_info, PCRE_INFO_NAMETABLE, (void *)&nametable);

    for(i = 0; i < ntlen; i++)
    {
        //first 2 bytes = number
        //rest = name
        reobj->groupindex->__setitem__(new str((char *)&nametable[i * nteach + 2]),
            (short)nametable[i * nteach] << 8 | (short)nametable[i * nteach + 1]);
    }

    //extra info
    reobj->pattern = new str(pat->unit);
    reobj->flags = flags;
    pcre_fullinfo(cpat, 0, PCRE_INFO_CAPTURECOUNT, &reobj->capture_count);

    return reobj;
}

str *escape(str *s)
{
    __GC_STRING *ps, out;
    int i, j, len;

    ps = &s->unit;
    len = ps->size();
    out = "";
    for(i = 0; i < len; i++)
    {
        //skip alphanumerics
        for(j = i; ::isalnum((int)(*ps)[j]) && j < len; j++) ;

        if(j != i)
        {
            out += ps->substr(i, j - i);

            i = j;
        }

        //now process potential metachars
        while(!::isalnum((int)(*ps)[i]) && i < len)
        {
            out += "\\";
            out += (*ps)[i];

            i++;
        }
    }

    return new str(out);
}

match_object *__exec_once(str *pat, str *subj, __ss_int flags)
{
    re_object *r;
    match_object *mo;

    r = compile(pat, flags);
    mo = r->__exec(subj, 0, -1, 0);

    if(!mo) delete r;

    return mo;
}

match_object *search(str *pat, str *subj, __ss_int flags)
{
    return __exec_once(pat, subj, flags);
}

match_object *match(str *pat, str *subj, __ss_int flags)
{
    return __exec_once(pat, subj, flags | PCRE_ANCHORED);
}

__iter<match_object *> *finditer(str *pat, str *subj, __ss_int pos, __ss_int endpos, __ss_int flags)
{
    re_object *ro;
    __iter<match_object *> *r;

    ro = compile(pat, flags);
    r = ro->finditer(subj, pos, endpos, 0);

    return r;
}

str *sub(str *pat, str *repl, str *subj, __ss_int maxn)
{
    re_object *ro;
    str *r;

    ro = compile(pat, 0);
    r = ro->sub(repl, subj, maxn);

    return r;
}

str *sub(str *pat, replfunc func, str *subj, __ss_int maxn) {
    re_object *ro;
    str *r;

    ro = compile(pat, 0);
    r = ro->sub(func, subj, maxn);

    return r;
}

tuple2<str *, __ss_int> *subn(str *pat, str *repl, str *subj, __ss_int maxn)
{
    re_object *ro;
    tuple2<str *, __ss_int> *r;

    ro = compile(pat, 0);
    r = ro->subn(repl, subj, maxn);

    return r;
}

list<str *> *__splitfind_once(str *pat, str *subj, __ss_int maxn, char onlyfind, __ss_int flags)
{
    re_object *ro;
    list<str *> *r;

    ro = compile(pat, flags);
    r = ro->__splitfind(subj, maxn, onlyfind, 0);

    //return subj->substr(captured[matchid * 2], captured[matchid * 2 + 1] - captured[matchid * 2]);
    return r;
}

list<str *> *split(str *pat, str *subj, __ss_int maxn)
{
    return __splitfind_once(pat, subj, maxn, 0, 0);
}

list<str *> *findall(str *pat, str *subj, __ss_int flags)
{
    return __splitfind_once(pat, subj, -1, 1, flags);
}

void __init(void)
{

    pcre_malloc = &re_malloc;
    pcre_free = &re_free;

    local_table = pcre_maketables();

}

}
