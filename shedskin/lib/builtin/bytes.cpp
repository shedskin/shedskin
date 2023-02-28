/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

/* bytes methods TODO share code with str */

bytes::bytes(int frozen) : hash(-1), frozen(frozen) {
    __class__ = cl_bytes;
}

bytes::bytes(const char *s) : unit(s), hash(-1), frozen(1) {
    __class__ = cl_bytes;
}

bytes::bytes(__GC_STRING s, int frozen) : unit(s), hash(-1), frozen(frozen) {
    __class__ = cl_bytes;
}

bytes::bytes(bytes *b, int frozen) : hash(-1), frozen(frozen) {
    __class__ = cl_bytes;
    unit = b->unit;
}

bytes::bytes(const char *s, int size, int frozen) : unit(s, size), hash(-1), frozen(frozen) { /* '\0' delimiter in C */
    __class__ = cl_bytes;
}

const char *bytes::c_str() const {
    return this->unit.c_str();
}

const size_t bytes::size() const {
    return this->unit.size();
}

str *bytes::__str__() {
    return __repr__();
}

const __ss_int bytes::find(const char c, __ss_int a) const {
    return this->unit.find(c, a);
}

const __ss_int bytes::find(const char *c, __ss_int a) const {
    return this->unit.find(c, a);
}

__ss_int bytes::__fixstart(__ss_int a, __ss_int b) {
    if(a == -1) return a;
    return a+b;
}

__ss_int bytes::find(bytes *s, __ss_int a) { return __fixstart(unit.substr(a, size()-a).find(s->unit), a); }
__ss_int bytes::find(bytes *s, __ss_int a, __ss_int b) { return __fixstart(unit.substr(a, b-a).find(s->unit), a); }

__ss_int bytes::rfind(bytes *s, __ss_int a) { return __fixstart(unit.substr(a, size()-a).rfind(s->unit), a); }
__ss_int bytes::rfind(bytes *s, __ss_int a, __ss_int b) { return __fixstart(unit.substr(a, b-a).rfind(s->unit), a); }

__ss_int bytes::__checkneg(__ss_int i) {
    if(i == -1)
        throw new ValueError(new str("substring not found"));
    return i;
}

__ss_int bytes::index(bytes *s, __ss_int a) { return __checkneg(find(s, a)); }
__ss_int bytes::index(bytes *s, __ss_int a, __ss_int b) { return __checkneg(find(s, a, b)); }

__ss_int bytes::rindex(bytes *s, __ss_int a) { return __checkneg(find(s, a)); }
__ss_int bytes::rindex(bytes *s, __ss_int a, __ss_int b) { return __checkneg(find(s, a, b)); }

str *bytes::__repr__() {
    std::stringstream ss;
    __GC_STRING sep = "\\\n\r\t";
    __GC_STRING let = "\\nrt";

    const char *quote = "'";
    size_t hasq = find('\'');
    size_t hasd = find('\"');

    if (hasq != std::string::npos && hasd != std::string::npos) {
        sep += "'"; let += "'";
    }
    if (hasq != std::string::npos && hasd == std::string::npos)
        quote = "\"";

    if(frozen == 0)
        ss << "bytearray(";

    ss << 'b';
    ss << quote;
    for(unsigned int i=0; i<size(); i++)
    {
        char c = unit[i];
        size_t k;

        if((k = sep.find_first_of(c)) != std::string::npos)
            ss << "\\" << let[k];
        else {
            int j = (int)((unsigned char)c);

            if(j<16)
                ss << "\\x0" << std::hex << j;
            else if(j>=' ' && j<='~')
                ss << (char)j;
            else
                ss << "\\x" << std::hex << j;
        }
    }
    ss << quote;
    if(frozen == 0)
        ss << ')';

    return new str(ss.str().c_str());
}

long bytes::__hash__() {
    if(!frozen)
        throw new TypeError(new str("unhashable type: 'bytearray'"));

    if (hash != -1)
        return hash;

    hash = std::hash<std::string>{}(unit.c_str());

    return hash;
}

__ss_bool bytes::__eq__(pyobj *p) {
    bytes *q = (bytes *)p;
    size_t len = size();
    if(len != q->size() or (hash != -1 and q->hash != -1 and hash != q->hash))
        return False;
    return __mbool(memcmp(unit.data(), q->unit.data(), len) == 0);
}

bytes *bytes::__add__(bytes *b) {
    bytes *s = new bytes(frozen);

    s->unit.reserve(size()+b->size());
    s->unit.append(unit);
    s->unit.append(b->unit);

    return s;
}

bytes *bytes::__iadd__(bytes *b) {
    unit = unit + b->unit;
    return this;
}

bytes *bytes::__imul__(__ss_int n) {
    __GC_STRING s = unit;
    for(__ss_int i=0; i<n-1; i++)
        unit += s;
    return this;
}

bytes *bytes::__mul__(__ss_int n) { /* optimize */
    bytes *r = new bytes(frozen);
    if(n<=0) return r;
    __GC_STRING &s = r->unit;
    __ss_int ulen = size();

    if(ulen == 1)
        r->unit = __GC_STRING(n, unit[0]);
    else {
        s.resize(ulen*n);

        for(__ss_int i=0; i<ulen*n; i+=ulen)
            s.replace(i, ulen, unit);
    }

    return r;
}

bytes *bytes::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    int len = size();
    slicenr(x, l, u, s, len);
    bytes *b;
    if(s == 1)
        b = new bytes(unit.data()+l, u-l, frozen);
    else {
        __GC_STRING r;
        if(!(x&1) && !(x&2) && s==-1) {
            r.resize(len);
            for(int i=0; i<len; i++)
                r[i] = unit[len-i-1];
        }
        else if(s > 0)
            for(int i=l; i<u; i += s)
                r += unit[i];
        else
            for(int i=l; i>u; i += s)
                r += unit[i];
        b = new bytes(r, frozen);
    }
    return b;
}

bytes *__bytes() {
    return new bytes();
}

bytes *__bytes(bytes *b) {
    return new bytes(b->unit);
}

bytes *__bytes(__ss_int t) {
    bytes *b = new bytes();
    for(int i=0; i<t; i++)
        b->unit += '\x00';
    return b;
}

bytes *__bytearray() {
    return new bytes(0);
}

bytes *__bytearray(bytes * b) {
    bytes *c = __bytes(b);
    c->frozen = 0;
    return c;
}

bytes *__bytearray(__ss_int t) {
    bytes *c = __bytes(t);
    c->frozen = 0;
    return c;
}

bytes *bytes::rstrip(bytes *chars) {
    __GC_STRING remove;
    if(chars) remove = chars->unit;
    else remove = ws;
    size_t last = unit.find_last_not_of(remove);
    if( last == std::string::npos )
        return new bytes(frozen);
    return new bytes(unit.substr(0,last+1), frozen);
}

bytes *bytes::lstrip(bytes *chars) {
    __GC_STRING remove;
    if(chars) remove = chars->unit;
    else remove = ws;
    size_t first = unit.find_first_not_of(remove);
    if( first == std::string::npos )
        return new bytes(frozen);
    return new bytes(unit.substr(first,size()-first), frozen);
}

bytes *bytes::strip(bytes *chars) {
    return lstrip(chars)->rstrip(chars);
}

list<bytes *> *bytes::split(bytes *sp, __ss_int max_splits) {
    __GC_STRING s = unit;
    int num_splits = 0;
    size_t sep_iter = 0, tmp, chunk_iter = 0;
    list<bytes *> *result = new list<bytes *>();
    if (sp == NULL)
    {
#define next_separator(iter) (s.find_first_of(ws, (iter)))
#define skip_separator(iter) (s.find_first_not_of(ws, (iter)))

        if(skip_separator(chunk_iter) == std::string::npos) /* XXX */
            return result;
        if(next_separator(chunk_iter) == 0)
            chunk_iter = skip_separator(chunk_iter);
        while((max_splits < 0 or num_splits < max_splits)
              and ((sep_iter = next_separator(chunk_iter)) != std::string::npos))
        {
            result->append(new bytes(s.substr(chunk_iter, sep_iter - chunk_iter), frozen));
            if((tmp = skip_separator(sep_iter)) == std::string::npos) {
                chunk_iter = sep_iter;
                break;
            } else
                chunk_iter = tmp;
            ++num_splits;
        }
        if(not (max_splits < 0 or num_splits < max_splits))
            result->append(new bytes(s.substr(chunk_iter, s.size()-chunk_iter), frozen));
        else if(sep_iter == std::string::npos)
            result->append(new bytes(s.substr(chunk_iter, s.size()-chunk_iter), frozen));

#undef next_separator
#undef skip_separator

    } else { /* given separator (slightly different algorithm required)
              * (python is very inconsistent in this respect) */
        const char *sep = sp->c_str();
        size_t sep_size = sp->size();

#define next_separator(iter) s.find(sep, (iter))
#define skip_separator(iter) ((iter + sep_size) > s.size()? -1 : (iter + sep_size))

        if (max_splits == 0) {
            result->append(this);
            return result;
        }
        if(next_separator(chunk_iter) == 0) {
            chunk_iter = skip_separator(chunk_iter);
            result->append(new bytes(frozen));
            ++num_splits;
        }
        while((max_splits < 0 or num_splits < max_splits)
              and (sep_iter = next_separator(chunk_iter)) != std::string::npos)
        {
            result->append(new bytes(s.substr(chunk_iter, sep_iter - chunk_iter), frozen));
            if((tmp = skip_separator(sep_iter)) == std::string::npos) {
                chunk_iter = sep_iter;
                break;
            } else
                chunk_iter = tmp;
            ++num_splits;
        }
        if(not (max_splits < 0 or num_splits < max_splits))
            result->append(new bytes(s.substr(chunk_iter, s.size()-chunk_iter), frozen));
        else if(sep_iter == std::string::npos)
            result->append(new bytes(s.substr(chunk_iter, s.size()-chunk_iter), frozen));


#undef next_separator
#undef skip_separator

    }

    return result;
}

list<bytes *> *bytes::rsplit(bytes *sep, __ss_int maxsep)
{
    __GC_STRING ts;
    list<bytes *> *r = new list<bytes *>();
    size_t i, j, curi, tslen;
    size_t maxsep2 = (size_t)maxsep;

    curi = 0;
    i = j = size() - 1;

    //split by whitespace
    if(!sep)
    {
        while(i != std::string::npos && j != std::string::npos && (curi < maxsep2 || maxsep2 < 0))
        {
            j = unit.find_last_not_of(ws, i);
            if(j == std::string::npos) break;

            i = unit.find_last_of(ws, j);

            //this works out pretty nicely; i will be -1 if no more is found, and thus i + 1 will be 0th index
            r->append(new bytes(unit.substr(i + 1, j - i), frozen));
            curi++;
        }

        //thus we only bother about extra stuff here if we *have* found more whitespace
        if(i != std::string::npos && j != std::string::npos && (j = unit.find_last_not_of(ws, i)) != std::string::npos)
            r->append(new bytes(unit.substr(0, j), frozen));
    }

    //split by seperator
    else
    {
        ts = sep->unit;
        tslen = ts.length();

        i++;
        while(i != std::string::npos && j != std::string::npos && (curi < maxsep2 || maxsep2 < 0))
        {
            j = i;
            i--;

            i = unit.rfind(ts, i);
            if(i == std::string::npos)
            {
                i = j;
                break;
            }

            r->append(new bytes(unit.substr(i + tslen, j - i - tslen), frozen));

            curi++;
        }

        //either left over (beyond max) or very last match (see loop break)
        if(i != std::string::npos)
            r->append(new bytes(unit.substr(0, i), frozen));
    }

    r->reverse();

    return r;
}

tuple2<bytes *, bytes *> *bytes::partition(bytes *sep)
{
    size_t i;

    i = find(sep->c_str());
    if(i != std::string::npos)
        return new tuple2<bytes *, bytes *>(3, new bytes(unit.substr(0, i), frozen), new bytes(sep->unit, frozen), new bytes(unit.substr(i + sep->unit.length()), frozen));
    else
        return new tuple2<bytes *, bytes *>(3, new bytes(unit, frozen), new bytes(frozen), new bytes(frozen));
}

tuple2<bytes *, bytes *> *bytes::rpartition(bytes *sep)
{
    size_t i;

    i = unit.rfind(sep->unit);
    if(i != std::string::npos)
        return new tuple2<bytes *, bytes *>(3, new bytes(unit.substr(0, i), frozen), new bytes(sep->unit, frozen), new bytes(unit.substr(i + sep->unit.length()), frozen));
    else
        return new tuple2<bytes *, bytes *>(3, new bytes(unit, frozen), new bytes(frozen), new bytes(frozen));
}

list<bytes *> *bytes::splitlines(__ss_int keepends)
{
    list<bytes *> *r = new list<bytes *>();
    size_t i, j, endlen;
    const char *ends = "\r\n";

    endlen = i = 0;
    do
    {
        j = i + endlen;
        i = unit.find_first_of(ends, j);
        if(i == std::string::npos) break;

        //for all we know the character sequence could change mid-way...
        if(unit[i] == '\r' && unit[i + 1] == '\n') endlen = 2;
        else endlen = 1;

        r->append(new bytes(unit.substr(j, i - j + (keepends ? endlen : 0)), frozen));
    }
    while(i >= 0);

    if(j != size()) r->append(new bytes(unit.substr(j), frozen));

    return r;
}

__ss_bool bytes::startswith(bytes *s, __ss_int start) { return startswith(s, start, __len__()); }
__ss_bool bytes::startswith(bytes *s, __ss_int start, __ss_int end) {
    __ss_int i, j, one = 1;
    slicenr(7, start, end, one, __len__());

    for(i = start, j = 0; i < end && j < len(s); )
        if (unit[i++] != s->unit[j++])
            return False;

    return __mbool(j == len(s));
}

__ss_bool bytes::endswith(bytes *s, __ss_int start) { return endswith(s, start, __len__()); }
__ss_bool bytes::endswith(bytes *s, __ss_int start, __ss_int end) {
    __ss_int i, j, one = 1;
    slicenr(7, start, end, one, __len__());

    for(i = end, j = len(s); i > start && j > 0; )
        if (unit[--i] != s->unit[--j])
            return False;

    return __mbool(j == 0);
}


__ss_int bytes::count(bytes *s, __ss_int start) { return count(s, start, __len__()); }
__ss_int bytes::count(bytes *s, __ss_int start, __ss_int end) {
    __ss_int count, one = 1;
    size_t i;
    slicenr(7, start, end, one, __len__());

    i = start; count = 0;
    while( ((i = find(s->c_str(), i)) != std::string::npos) && (i <= end-(size_t)len(s)) )
    {
        i += len(s);
        count++;
    }

    return count;
}

__ss_int bytes::count(__ss_int b, __ss_int start) { return count(b, start, __len__()); }
__ss_int bytes::count(__ss_int b, __ss_int start, __ss_int end) {
    __ss_int count, one = 1;
    size_t i;
    slicenr(7, start, end, one, __len__());

    count = 0;
    for(i = start; i < (size_t)end; i++) {
        if((unsigned char)b == unit[i])
            count++;
    }

    return count;
}

bytes *bytes::expandtabs(__ss_int tabsize) {
    size_t i;
    __GC_STRING r = unit;
    while((i = r.find("\t")) != std::string::npos)
        r.replace(i, 1, (new bytes(" "))->__mul__(tabsize-i%tabsize)->unit);
    return new bytes(r, frozen);
}

__ss_bool bytes::__ctype_function(int (*cfunc)(int))
{
  int i, l = size();

  if(!l)
      return False;

  for(i = 0; i < l; i++)
      if(!cfunc((int)unit[i])) return False;

  return True;
}

__ss_bool bytes::islower() { return __ctype_function(&::islower); }
__ss_bool bytes::isupper() { return __ctype_function(&::isupper); }
__ss_bool bytes::isspace() { return __mbool(size() && (unit.find_first_not_of(ws) == std::string::npos)); }
__ss_bool bytes::isdigit() { return __ctype_function(&::isdigit); }
__ss_bool bytes::isalpha() { return __ctype_function(&::isalpha); }
__ss_bool bytes::isalnum() { return __ctype_function(&::isalnum); }

__ss_bool bytes::istitle()
{
    int i, len;

    len = size();
    if(!len)
        return False;

    for(i = 0; i < len; )
    {
        for( ; !::isalpha((int)unit[i]) && i < len; i++) ;
        if(i == len) break;

        if(!::isupper((int)unit[i])) return False;
        i++;

        for( ; ::islower((int)unit[i]) && i < len; i++) ;
        if(i == len) break;

        if(::isalpha((int)unit[i])) return False;
    }

    return True;
}

__ss_bool bytes::__ss_isascii() {
  int i, l = size();

  for(i = 0; i < l; i++) {
      unsigned char elem = unit[i];

      if(elem > 127)
          return False;
  }

  return True;
}

bytes *bytes::upper() {
    if(size() == 1)
        return new bytes(__char_cache[((unsigned char)(::toupper(unit[0])))]->unit, frozen);

    bytes *toReturn = new bytes(this->unit, frozen);
    std::transform(toReturn->unit.begin(), toReturn->unit.end(), toReturn->unit.begin(), toupper);

    return toReturn;
}

bytes *bytes::lower() {
    if(size() == 1)
        return new bytes(__char_cache[((unsigned char)(::tolower(unit[0])))]->unit, frozen);

    bytes *toReturn = new bytes(this->unit, frozen);
    std::transform(toReturn->unit.begin(), toReturn->unit.end(), toReturn->unit.begin(), tolower);

    return toReturn;
}

bytes *bytes::title() {
    bytes *r = new bytes(unit, frozen);
    bool up = true;
    size_t len = this->size();
    for(size_t i=0; i<len; i++) {
        char c = this->unit[i];
        if(!::isalpha(c))
            up = true;
        else if (up) {
            c = ::toupper(c);
            up = false;
        }
        else
            c = ::tolower(c);
        r->unit[i] = c;
    }
    return r;
}

bytes *bytes::capitalize() {
    bytes *r = new bytes(unit, frozen);
    r->unit[0] = ::toupper(r->unit[0]);
    return r;
}

bytes *bytes::replace(bytes *a, bytes *b, __ss_int c) {
    __GC_STRING s = unit;
    size_t i, j, p;
    size_t asize = a->size();
    size_t bsize = b->size();
    size_t c2 = (size_t)c;
    j = p = 0;
    while( ((c2==std::string::npos) || (j++ != c2)) && (i = s.find(a->unit, p)) != std::string::npos ) {
      s.replace(i, asize, b->unit);
      p = i + bsize + (asize?0:1);
    }
    return new bytes(s, frozen);
}

str *bytes::hex(str *sep) {
    str *result = new str();
    size_t l = size();

    for(size_t i=0; i<l; i++) {
        unsigned char low = unit[i] & 0xf;
        unsigned char high = (unit[i] >> 4) & 0xf;

        if(high < 10)
            result->unit += '0' + high;
        else
            result->unit += 'a' - 10 + high;

        if(low < 10)
            result->unit += '0' + low;
        else
            result->unit += 'a' - 10 + low;

        if(sep and i != l-1)
            result->unit += sep->unit;
    }

    return result;
}

bytes *bytes::center(__ss_int width, bytes *fillchar) {
    int len = __len__();
    if(width<=len)
        return this;

    if(!fillchar) fillchar = bsp;
    bytes *r = fillchar->__mul__(width);

    int j = (width-len)/2;
    for(int i=0; i<len; i++)
        r->unit[j+i] = unit[i];

    r->frozen = frozen;
    return r;
}

bytes *bytes::copy() {
    return new bytes(this, frozen);
}

bytes *bytes::zfill(__ss_int width) {
    if(width<=__len__()) return this;
    bytes *r;
    if(__len__() > 0 and (unit[0] == '-' or unit[0] == '+'))
        r = __add__((new bytes("0"))->__mul__(width-__len__()));
    else
        r = (new bytes("0"))->__mul__(width-__len__())->__add__(this);
    r->frozen = frozen;
    return r;
}

bytes *bytes::ljust(__ss_int width, bytes *s) {
    if(width<=__len__()) return this;
    if(!s) s = bsp;
    bytes *r = __add__(s->__mul__(width-__len__()));
    r->frozen = frozen;
    return r;
}

bytes *bytes::rjust(__ss_int width, bytes *s) {
    if(width<=__len__()) return this;
    if(!s) s = bsp;
    bytes *r = s->__mul__(width-__len__())->__add__(this);
    r->frozen = frozen;
    return r;
}

/* extmod glue */

#ifdef __SS_BIND
bytes::bytes(PyObject *p) : hash(-1) {
    __class__ = cl_bytes;

    if(PyBytes_Check(p)) {
        unit = __GC_STRING(PyBytes_AS_STRING(p), PyBytes_Size(p));
	frozen = 1;
    } else if (PyByteArray_Check(p)) {
        unit = __GC_STRING(PyByteArray_AS_STRING(p), PyByteArray_Size(p));
	frozen = 0;
    } else
        throw new TypeError(new str("error in conversion to Shed Skin (bytes/bytearray expected)"));
}

PyObject *bytes::__to_py__() {
    if(frozen)
        return PyBytes_FromStringAndSize(unit.data(), unit.size());
    else
        return PyByteArray_FromStringAndSize(unit.data(), unit.size());
}
#endif

/* bytearray */

void *bytes::clear() {
    unit.clear();
    return NULL;
}

void *bytes::append(__ss_int i) {
    unit += (unsigned char)i;
    return NULL;
}

bytes *bytes::swapcase() {
    bytes *r = new bytes(unit, frozen);
    int len = __len__();
    for(int i = 0; i < len; i++)
        r->unit[i] = __case_swap_cache->unit[(unsigned char)unit[i]];
    return r;
}

void *bytes::__delitem__(__ss_int i) {
    i = __wrap(this, i);
    unit.erase(i, 1);
    return NULL;
}

__ss_int bytes::pop(__ss_int i) {
    i = __wrap(this, i);
    __ss_int result = (unsigned char)unit[i];
    unit.erase(i, 1);
    return result;
}

void *bytes::extend(pyiter<__ss_int> *t) {
    __ss_int e;
    typename pyiter<__ss_int>::for_in_loop __3;
    int __2;
    pyiter<__ss_int> *__1;
    FOR_IN(e,t,1,2,3)
        unit += (unsigned char)e;
    END_FOR
    return NULL;
}

void *bytes::reverse() {
    __GC_STRING s(unit.rbegin(), unit.rend());
    unit = s;
    return NULL;
}

void *bytes::remove(__ss_int i) {
    __ss_int pos = find(i);
    if(pos == -1)
        throw new ValueError(new str("value not found in bytearray"));
    __delitem__(pos);
    return NULL;
}

void *bytes::insert(__ss_int index, __ss_int item) {
    index = __wrap(this, index);
    unit.insert(unit.begin()+index, item);
    return NULL;
}

void *bytes::__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, pyiter<__ss_int> *b) {
    list<__ss_int> *ll = new list<__ss_int>(this);
    ll->__setslice__(x, l, u, s, b);
    __GC_STRING r;
    __ss_int len = ll->__len__();
    for(__ss_int i=0; i<len; i++)
        r += ll->units[i];
    unit = r;
    return NULL;
}

void *bytes::__delete__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    list<__ss_int> *ll = new list<__ss_int>(this);
    ll->__delete__(x, l, u, s);
    __GC_STRING r;
    __ss_int len = ll->__len__();
    for(__ss_int i=0; i<len; i++)
        r += ll->units[i];
    unit = r;
    return NULL;
}

__ss_bool bytes::__contains__(bytes *b) {
    return __mbool(unit.find(b->unit) != std::string::npos);
}
