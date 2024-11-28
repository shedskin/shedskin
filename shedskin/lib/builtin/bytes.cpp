/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

/* bytes methods TODO share code with str */

bytes::bytes(int frozen_) : hash(-1), frozen(frozen_) {
    __class__ = cl_bytes;
}

bytes::bytes(const char *s) : unit(s), hash(-1), frozen(1) {
    __class__ = cl_bytes;
}

bytes::bytes(__GC_STRING s, int frozen_) : unit(s), hash(-1), frozen(frozen_) {
    __class__ = cl_bytes;
}

bytes::bytes(bytes *b, int frozen_) : hash(-1), frozen(frozen_) {
    __class__ = cl_bytes;
    unit = b->unit;
}

bytes::bytes(const char *s, int size, int frozen_) : unit(s, (size_t)size), hash(-1), frozen(frozen_) { /* '\0' delimiter in C */
    __class__ = cl_bytes;
}

char *bytes::c_str() const {
    return (char *)this->unit.c_str();
}

str *bytes::__str__() {
    return __repr__();
}

__ss_int bytes::__fixstart(size_t a, __ss_int b) {
    if(a == std::string::npos) return -1;
    return (__ss_int)a+b;
}

__ss_int bytes::find(bytes *s, __ss_int a) {
    __ss_int step = 1;
    __ss_int b = this->__len__();
    slicenr(3, a, b, step, this->__len__());
    return __fixstart(unit.substr((size_t)a, this->unit.size()-(size_t)a).find(s->unit), a);
}

__ss_int bytes::find(bytes *s, __ss_int a, __ss_int b) {
    __ss_int step = 1;
    slicenr(3, a, b, step, this->__len__());
    return __fixstart(unit.substr((size_t)a, (size_t)(b-a)).find(s->unit), a);
}

__ss_int bytes::find(__ss_int i, __ss_int a) {
    return find(i, a, this->__len__());
}

__ss_int bytes::find(__ss_int i, __ss_int a, __ss_int b) {
    __ss_int step = 1;
    slicenr(3, a, b, step, this->__len__());
    for(__ss_int j=a; j<b; j++) {
        if(unit[(size_t)j] == i)
            return j;
    }
    return -1;
}

__ss_int bytes::rfind(bytes *s, __ss_int a) {
    __ss_int step = 1;
    __ss_int b = this->__len__();
    slicenr(3, a, b, step, this->__len__());
    return __fixstart(unit.substr((size_t)a, this->unit.size()-(size_t)a).rfind(s->unit), a);
}

__ss_int bytes::rfind(bytes *s, __ss_int a, __ss_int b) {
    __ss_int step = 1;
    slicenr(3, a, b, step, this->__len__());
    return __fixstart(unit.substr((size_t)a, (size_t)(b-a)).rfind(s->unit), a);
}

__ss_int bytes::rfind(__ss_int i, __ss_int a) {
    return rfind(i, a, this->__len__());

}

__ss_int bytes::rfind(__ss_int i, __ss_int a, __ss_int b) {
    __ss_int step = 1;
    slicenr(3, a, b, step, this->__len__());
    for(__ss_int j=b-1; j>=a; j--) {
        if(unit[(size_t)j] == i)
            return j;
    }
    return -1;
}

__ss_int bytes::__checkneg(__ss_int i) {
    if(i == -1)
        throw new ValueError(new str("subsection not found"));
    return i;
}

__ss_int bytes::index(bytes *s, __ss_int a) { return __checkneg(find(s, a)); }
__ss_int bytes::index(bytes *s, __ss_int a, __ss_int b) { return __checkneg(find(s, a, b)); }
__ss_int bytes::index(__ss_int i, __ss_int a) { return __checkneg(find(i, a)); }
__ss_int bytes::index(__ss_int i, __ss_int a, __ss_int b) { return __checkneg(find(i, a, b)); }

__ss_int bytes::rindex(bytes *s, __ss_int a) { return __checkneg(rfind(s, a)); }
__ss_int bytes::rindex(bytes *s, __ss_int a, __ss_int b) { return __checkneg(rfind(s, a, b)); }
__ss_int bytes::rindex(__ss_int i, __ss_int a) { return __checkneg(rfind(i, a)); }
__ss_int bytes::rindex(__ss_int i, __ss_int a, __ss_int b) { return __checkneg(rfind(i, a, b)); }

str *bytes::__repr__() {
    std::stringstream ss;
    __GC_STRING separator = "\\\n\r\t";
    __GC_STRING let = "\\nrt";

    const char *quote = "'";
    size_t hasq = this->unit.find('\'');
    size_t hasd = this->unit.find('\"');

    if (hasq != std::string::npos && hasd != std::string::npos) {
        separator += "'"; let += "'";
    }
    if (hasq != std::string::npos && hasd == std::string::npos)
        quote = "\"";

    if(frozen == 0)
        ss << "bytearray(";

    ss << 'b';
    ss << quote;
    for(unsigned int i=0; i<this->unit.size(); i++)
    {
        char c = unit[i];
        size_t k;

        if((k = separator.find_first_of(c)) != std::string::npos)
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

    hash = (long)std::hash<std::string>{}(unit.c_str());

    return hash;
}

__ss_bool bytes::__eq__(pyobj *p) {
    bytes *q = (bytes *)p;
    size_t len = this->unit.size();
    if(len != q->unit.size() or (hash != -1 and q->hash != -1 and hash != q->hash))
        return False;
    return __mbool(memcmp(unit.data(), q->unit.data(), len) == 0);
}

bytes *bytes::__add__(bytes *b) {
    bytes *s = new bytes(frozen);

    s->unit.reserve(this->unit.size()+b->unit.size());
    s->unit.append(unit);
    s->unit.append(b->unit);

    return s;
}

bytes *bytes::__iadd__(bytes *b) {
    if (frozen)
        return __add__(b);
    else
        unit += b->unit;
    return this;
}

bytes *bytes::__imul__(__ss_int n) {
    if (frozen)
        return __mul__(n);
    else {
        __GC_STRING s = unit;
        for(__ss_int i=0; i<n-1; i++)
            unit += s;
        return this;
    }
}

bytes *bytes::__mul__(__ss_int n) { /* optimize */
    bytes *r = new bytes(frozen);
    if(n<=0) return r;
    size_t ns = (size_t)n;

    __GC_STRING &s = r->unit;
    size_t ulen = this->unit.size();

    if(ulen == 1)
        r->unit = __GC_STRING(ns, unit[0]);
    else {
        s.resize(ulen*ns);

        for(size_t i=0; i<ulen*ns; i+=ulen)
            s.replace(i, ulen, unit);
    }

    return r;
}

bytes *bytes::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    size_t len = this->unit.size();
    slicenr(x, l, u, s, (__ss_int)len);
    bytes *b;
    if(s == 1)
        b = new bytes(unit.data()+l, u-l, frozen);
    else {
        __GC_STRING r;
        if(!(x&1) && !(x&2) && s==-1) {
            r.resize(len);
            for(size_t i=0; i<len; i++)
                r[i] = unit[len-i-1];
        }
        else if(s > 0)
            for(__ss_int i=l; i<u; i += s)
                r += unit[(size_t)i];
        else
            for(__ss_int i=l; i>u; i += s)
                r += unit[(size_t)i];
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
    return new bytes(unit.substr(first,this->unit.size()-first), frozen);
}

bytes *bytes::strip(bytes *chars) {
    return lstrip(chars)->rstrip(chars);
}

list<bytes *> *bytes::split(bytes *sep_, __ss_int maxsplit) {
    size_t pos_start = 0, pos_end;
    list<bytes *> *result = new list<bytes *>();
    __ss_int splits = 0;

    if(sep_ == NULL) {
        pos_start = unit.find_first_not_of(ws, pos_start);
        if (pos_start == std::string::npos)
            return result;
    }

    while(1) {
        if(sep_ == NULL)
            pos_end = unit.find_first_of(ws, pos_start);
        else
            pos_end = unit.find(sep_->unit, pos_start);

        if(pos_end == std::string::npos || ((maxsplit != -1) && splits >= maxsplit)) {
            result->append(new bytes(unit.substr(pos_start, unit.size()-pos_start)));
            break;
        }

        result->append(new bytes(unit.substr(pos_start, pos_end-pos_start)));
        splits += 1;

        if(sep_ == NULL) {
            pos_start = unit.find_first_not_of(ws, pos_end);
            if(pos_start == std::string::npos)
                break;
        } else {
            pos_start = pos_end + sep_->unit.size();
            if(pos_start == unit.size()) {
                result->append(new bytes(unit.substr(pos_start, unit.size()-pos_start)));
                break;
            }
        }
    }
    return result;
}

list<bytes *> *bytes::rsplit(bytes *separator, __ss_int maxsep)
{
    __GC_STRING ts;
    list<bytes *> *r = new list<bytes *>();
    size_t i, j, curi, tslen;
    size_t maxsep2 = (size_t)maxsep;

    curi = 0;
    i = j = this->unit.size() - 1;

    //split by whitespace
    if(!separator)
    {
        while(i != std::string::npos && j != std::string::npos && (curi < maxsep2 || maxsep2 == std::string::npos))
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
        ts = separator->unit;
        tslen = ts.length();

        i++;
        while(i != std::string::npos && j != std::string::npos && (curi < maxsep2 || maxsep2 == std::string::npos))
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

tuple2<bytes *, bytes *> *bytes::partition(bytes *separator)
{
    size_t i;

    i = this->unit.find(separator->c_str());
    if(i != std::string::npos)
        return new tuple2<bytes *, bytes *>(3, new bytes(unit.substr(0, i), frozen), new bytes(separator->unit, frozen), new bytes(unit.substr(i + separator->unit.length()), frozen));
    else
        return new tuple2<bytes *, bytes *>(3, new bytes(unit, frozen), new bytes(frozen), new bytes(frozen));
}

tuple2<bytes *, bytes *> *bytes::rpartition(bytes *separator)
{
    size_t i;

    i = this->unit.rfind(separator->unit);
    if(i != std::string::npos)
        return new tuple2<bytes *, bytes *>(3, new bytes(unit.substr(0, i), frozen), new bytes(separator->unit, frozen), new bytes(unit.substr(i + separator->unit.length()), frozen));
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
    while(i != std::string::npos);

    if(j != this->unit.size()) r->append(new bytes(unit.substr(j), frozen));

    return r;
}

__ss_bool bytes::startswith(bytes *s, __ss_int start) { return startswith(s, start, __len__()); }
__ss_bool bytes::startswith(bytes *s, __ss_int start, __ss_int end) {
    __ss_int one = 1;

    slicenr(7, start, end, one, __len__());

    size_t i, j;
    for(i = (size_t)start, j = 0; i < (size_t)end && j < s->unit.size(); )
        if (unit[i++] != s->unit[j++])
            return False;

    return __mbool(j == s->unit.size());
}

__ss_bool bytes::endswith(bytes *s, __ss_int start) { return endswith(s, start, __len__()); }
__ss_bool bytes::endswith(bytes *s, __ss_int start, __ss_int end) {
    __ss_int one = 1;
    slicenr(7, start, end, one, __len__());

    size_t i, j;
    for(i = (size_t)end, j = s->unit.size(); i > (size_t)start && j > 0; )
        if (unit[--i] != s->unit[--j])
            return False;

    return __mbool(j == 0);
}


__ss_int bytes::count(bytes *s, __ss_int start) { return count(s, start, __len__()); }
__ss_int bytes::count(bytes *s, __ss_int start, __ss_int end) {
    __ss_int count, one = 1;
    size_t i;
    slicenr(7, start, end, one, __len__());

    i = (size_t)start;
    count = 0;
    while( ((i = this->unit.find(s->c_str(), i)) != std::string::npos) && (i <= (size_t)end-s->unit.size()) )
    {
        i += s->unit.size();
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
    for(i = (size_t)start; i < (size_t)end; i++) {
        if((unsigned char)b == unit[i])
            count++;
    }

    return count;
}

bytes *bytes::expandtabs(__ss_int tabsize) {
    size_t i;
    __GC_STRING r = unit;
    while((i = r.find("\t")) != std::string::npos)
        r.replace(i, 1, (new bytes(" "))->__mul__(tabsize-(__ss_int)i%tabsize)->unit);
    return new bytes(r, frozen);
}

__ss_bool bytes::__ctype_function(int (*cfunc)(int))
{
  size_t i, l = this->unit.size();

  if(!l)
      return False;

  for(i = 0; i < l; i++)
      if(!cfunc((int)unit[i])) return False;

  return True;
}

__ss_bool bytes::islower() { return __ctype_function(&::islower); }
__ss_bool bytes::isupper() { return __ctype_function(&::isupper); }
__ss_bool bytes::isspace() { return __mbool(this->unit.size() && (unit.find_first_not_of(ws) == std::string::npos)); }
__ss_bool bytes::isdigit() { return __ctype_function(&::isdigit); }
__ss_bool bytes::isalpha() { return __ctype_function(&::isalpha); }
__ss_bool bytes::isalnum() { return __ctype_function(&::isalnum); }

__ss_bool bytes::istitle()
{
    size_t i, len;

    len = this->unit.size();
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
  size_t i, l = this->unit.size();

  for(i = 0; i < l; i++) {
      unsigned char elem = (unsigned char)unit[i];

      if(elem > 127)
          return False;
  }

  return True;
}

bytes *bytes::upper() {
    if(this->unit.size() == 1)
        return new bytes(__char_cache[((unsigned char)(::toupper(unit[0])))]->unit, frozen);

    bytes *toReturn = new bytes(this->unit, frozen);
    std::transform(toReturn->unit.begin(), toReturn->unit.end(), toReturn->unit.begin(), toupper);

    return toReturn;
}

bytes *bytes::lower() {
    if(this->unit.size() == 1)
        return new bytes(__char_cache[((unsigned char)(::tolower(unit[0])))]->unit, frozen);

    bytes *toReturn = new bytes(this->unit, frozen);
    std::transform(toReturn->unit.begin(), toReturn->unit.end(), toReturn->unit.begin(), tolower);

    return toReturn;
}

bytes *bytes::title() {
    bytes *r = new bytes(unit, frozen);
    bool up = true;
    size_t len = this->unit.size();
    for(size_t i=0; i<len; i++) {
        char c = this->unit[i];
        if(!::isalpha(c))
            up = true;
        else if (up) {
            c = (char)::toupper(c);
            up = false;
        }
        else
            c = (char)::tolower(c);
        r->unit[i] = c;
    }
    return r;
}

bytes *bytes::capitalize() {
    bytes *r = new bytes(unit, frozen);
    r->unit[0] = (char)::toupper(r->unit[0]);
    return r;
}

bytes *bytes::replace(bytes *a, bytes *b, __ss_int c) {
    __GC_STRING s = unit;
    size_t i, j, p;
    size_t asize = a->unit.size();
    size_t bsize = b->unit.size();
    size_t c2 = (size_t)c;
    j = p = 0;
    while( ((c2==std::string::npos) || (j++ != c2)) && (i = s.find(a->unit, p)) != std::string::npos ) {
      s.replace(i, asize, b->unit);
      p = i + bsize + (asize?0:1);
    }
    return new bytes(s, frozen);
}

str *bytes::hex(str *separator) {
    str *result = new str();
    size_t l = this->unit.size();

    for(size_t i=0; i<l; i++) {
        unsigned char low = unit[i] & 0xf;
        unsigned char high = (unit[i] >> 4) & 0xf;

        if(high < 10)
            result->unit += '0' + (char)high;
        else
            result->unit += 'a' - 10 + (char)high;

        if(low < 10)
            result->unit += '0' + (char)low;
        else
            result->unit += 'a' - 10 + (char)low;

        if(separator and i != l-1)
            result->unit += separator->unit;
    }

    return result;
}

bytes *bytes::center(__ss_int w, bytes *fillchar) {
    size_t width = (size_t)w;
    size_t len = unit.size();
    if(width<=len)
        return this;

    if(!fillchar) fillchar = bsp;
    bytes *r = fillchar->__mul__(w);

    size_t j = (width-len)/2;
    for(size_t i=0; i<len; i++)
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
        unit = __GC_STRING(PyBytes_AS_STRING(p), (size_t)PyBytes_Size(p));
	frozen = 1;
    } else if (PyByteArray_Check(p)) {
        unit = __GC_STRING(PyByteArray_AS_STRING(p), (size_t)PyByteArray_Size(p));
	frozen = 0;
    } else
        throw new TypeError(new str("error in conversion to Shed Skin (bytes/bytearray expected)"));
}

PyObject *bytes::__to_py__() {
    if(frozen)
        return PyBytes_FromStringAndSize(unit.data(), (Py_ssize_t)unit.size());
    else {
        return PyByteArray_FromStringAndSize(unit.data(), (Py_ssize_t)unit.size());
    }
}
#endif

/* bytearray */

void *bytes::clear() {
    unit.clear();
    return NULL;
}

void *bytes::append(__ss_int i) {
    unit += (char)i;
    return NULL;
}

bytes *bytes::swapcase() {
    bytes *r = new bytes(unit, frozen);
    size_t len = unit.size();
    for(size_t i=0; i<len; i++)
        r->unit[i] = __case_swap_cache->unit[(unsigned char)unit[i]];
    return r;
}

void *bytes::__delitem__(__ss_int i) {
    i = __wrap(this, i);
    unit.erase((size_t)i, 1);
    return NULL;
}

__ss_int bytes::pop(__ss_int i) {
    i = __wrap(this, i);
    __ss_int result = (unsigned char)unit[(size_t)i];
    unit.erase((size_t)i, 1);
    return result;
}

void *bytes::extend(pyiter<__ss_int> *t) {
    __ss_int e;
    typename pyiter<__ss_int>::for_in_loop __3;
    int __2;
    pyiter<__ss_int> *__1;
    FOR_IN(e,t,1,2,3)
        unit += (char)e;
    END_FOR
    return NULL;
}

void *bytes::reverse() {
    __GC_STRING s(unit.rbegin(), unit.rend());
    unit = s;
    return NULL;
}

void *bytes::remove(__ss_int i) {
    size_t pos = this->unit.find((char)i);
    if(pos == std::string::npos)
        throw new ValueError(new str("value not found in bytearray"));
    __delitem__((__ss_int)pos);
    return NULL;
}

void *bytes::insert(__ss_int index, __ss_int item) {
    index = __wrap(this, index);
    unit.insert(unit.begin()+index, (char)item);
    return NULL;
}

void *bytes::__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, pyiter<__ss_int> *b) {
    list<__ss_int> *ll = new list<__ss_int>(this);
    ll->__setslice__(x, l, u, s, b);
    __GC_STRING r;
    size_t len = ll->units.size();
    for(size_t i=0; i<len; i++)
        r += (char)ll->units[i];
    unit = r;
    return NULL;
}

void *bytes::__delete__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    list<__ss_int> *ll = new list<__ss_int>(this);
    ll->__delete__(x, l, u, s);
    __GC_STRING r;
    size_t len = ll->units.size();
    for(size_t i=0; i<len; i++)
        r += (char)ll->units[i];
    unit = r;
    return NULL;
}

__ss_bool bytes::__contains__(bytes *b) {
    return __mbool(unit.find(b->unit) != std::string::npos);
}

__ss_bool bytes::__contains__(__ss_int i) {
    size_t len = unit.size();
    for(size_t j=0; j<len; j++) {
        if(unit[j] == i)
            return True;
    }
    return False;
}
