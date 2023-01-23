/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* str methods */

str::str() : hash(-1), charcache(0) {
    __class__ = cl_str_;
}

str::str(const char *s) : unit(s), hash(-1), charcache(0) {
    __class__ = cl_str_;
}

str::str(__GC_STRING s) : unit(s), hash(-1), charcache(0) {
    __class__ = cl_str_;
}

str::str(const char *s, int size) : unit(s, size), hash(-1), charcache(0) { /* '\0' delimiter in C */
    __class__ = cl_str_;
}

str *str::__str__() {
    return this;
}

const char *str::c_str() const {
    return this->unit.c_str();
}

const size_t str::size() const {
    return this->unit.size();
}

const __ss_int str::find(const char c, __ss_int a) const {
    return this->unit.find(c, a);
}

const __ss_int str::find(const char *c, __ss_int a) const {
    return this->unit.find(c, a);
}

str *str::__repr__() {
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

    return new str(ss.str().c_str());
}

__ss_int str::__int__() {
    return __int(this);
}

__ss_bool str::__contains__(str *s) {
    if(s->charcache)
        return __mbool(unit.find(s->unit[0]) != std::string::npos);
    return __mbool(unit.find(s->unit) != std::string::npos);
}

str *str::operator+ (const char *rhs) {
    str *ret = new str(this->unit + rhs);
    return ret;
}

str *str::operator+ (const char &rhs) {
    str *ret = new str(this->unit + rhs);
    return ret;
}

void str::operator+= (const char *rhs) {
    this->unit += rhs;
}

void str::operator+= (const char &rhs) {
    this->unit += rhs;
}

__ss_bool str::__ctype_function(int (*cfunc)(int))
{
  int i, l = size();

  if(!l)
      return False;

  for(i = 0; i < l; i++)
      if(!cfunc((int)unit[i])) return False;

  return True;
}

__ss_bool str::isspace() { return __mbool(size() && (unit.find_first_not_of(ws) == std::string::npos)); }
__ss_bool str::isdigit() { return __ctype_function(&::isdigit); }
__ss_bool str::isalpha() { return __ctype_function(&::isalpha); }
__ss_bool str::isalnum() { return __ctype_function(&::isalnum); }
__ss_bool str::islower() { return __ctype_function(&::islower); }
__ss_bool str::isupper() { return __ctype_function(&::isupper); }

__ss_bool str::isprintable() {
  int i, l = size();

  for(i = 0; i < l; i++) {
      unsigned char elem = unit[i];

      if((0 <= elem and elem <= 31) or (127 <= elem and elem <= 160) or elem == 173)
          return False;
  }

  return True;
}

__ss_bool str::__ss_isascii() {
  int i, l = size();

  for(i = 0; i < l; i++) {
      unsigned char elem = unit[i];

      if(elem > 127)
          return False;
  }

  return True;
}

__ss_bool str::isdecimal() {
  int i, l = size();

  if(!l)
      return False;

  for(i = 0; i < l; i++) {
      unsigned char elem = unit[i];

      if(elem < 48 or elem > 57)
          return False;
  }

  return True;
}

__ss_bool str::isnumeric() {
  int i, l = size();

  if(!l)
      return False;

  for(i = 0; i < l; i++) {
      unsigned char elem = unit[i];

      if(elem < 48 or (elem > 57 and elem < 178) or (elem > 179 and elem < 185) or (elem > 185 and elem < 188) or elem > 190)
          return False;
  }

  return True;
}

str *str::ljust(__ss_int width, str *s) {
    if(width<=__len__()) return this;
    if(!s) s = sp;
    return __add__(s->__mul__(width-__len__()));
}

str *str::rjust(__ss_int width, str *s) {
    if(width<=__len__()) return this;
    if(!s) s = sp;
    return s->__mul__(width-__len__())->__add__(this);
}

str *str::zfill(__ss_int width) {
    if(width<=__len__()) return this;
    if(__len__() > 0 and (unit[0] == '-' or unit[0] == '+'))
        return __add__((new str("0"))->__mul__(width-__len__()));
    else
        return (new str("0"))->__mul__(width-__len__())->__add__(this);
}

str *str::expandtabs(__ss_int tabsize) {
    size_t i;
    __GC_STRING r = unit;
    while((i = r.find("\t")) != std::string::npos)
        r.replace(i, 1, (new str(" "))->__mul__(tabsize-i%tabsize)->unit);
    return new str(r);
}

str *str::strip(str *chars) {
    return lstrip(chars)->rstrip(chars);
}

str *str::lstrip(str *chars) {
    __GC_STRING remove;
    if(chars) remove = chars->unit;
    else remove = ws;
    size_t first = unit.find_first_not_of(remove);
    if( first == std::string::npos )
        return new str("");
    return new str(unit.substr(first,size()-first));
}

tuple2<str *, str *> *str::partition(str *sep)
{
    size_t i;

    i = find(sep->c_str());
    if(i != std::string::npos)
        return new tuple2<str *, str *>(3, new str(unit.substr(0, i)), new str(sep->unit), new str(unit.substr(i + sep->unit.length())));
    else
        return new tuple2<str *, str *>(3, new str(unit), new str(""), new str(""));
}

tuple2<str *, str *> *str::rpartition(str *sep)
{
    size_t i;

    i = unit.rfind(sep->unit);
    if(i != std::string::npos)
        return new tuple2<str *, str *>(3, new str(unit.substr(0, i)), new str(sep->unit), new str(unit.substr(i + sep->unit.length())));
    else
        return new tuple2<str *, str *>(3, new str(unit), new str(""), new str(""));
}

list<str *> *str::rsplit(str *sep, __ss_int maxsep)
{
    __GC_STRING ts;
    list<str *> *r = new list<str *>();
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

            r->append(new str(unit.substr(i + 1, j - i)));
            curi++;
        }

        //thus we only bother about extra stuff here if we *have* found more whitespace
        if(i != std::string::npos && j != std::string::npos && (j = unit.find_last_not_of(ws, i)) != std::string::npos)
            r->append(new str(unit.substr(0, j)));
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

            r->append(new str(unit.substr(i + tslen, j - i - tslen)));

            curi++;
        }

        //either left over (beyond max) or very last match (see loop break)
        if(i != std::string::npos)
            r->append(new str(unit.substr(0, i)));
    }

    r->reverse();

    return r;
}

__ss_bool str::istitle()
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

__ss_bool str::isidentifier() {
    int i, len;

    len = size();
    if(!len)
        return False;
    if('0' <= unit[0] and unit[0] <= '9')
        return False;

    for(i = 0; i < len; i++)
        if(not (('a' <= unit[i] and unit[i] <= 'z') or ('A' <= unit[i] and unit[i] <= 'Z') or (unit[i] == '_')))
            return False;

    return True;
}

list<str *> *str::splitlines(__ss_int keepends)
{
    list<str *> *r = new list<str *>();
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

        r->append(new str(unit.substr(j, i - j + (keepends ? endlen : 0))));
    }
    while(i >= 0);

    if(j != size()) r->append(new str(unit.substr(j)));

    return r;
}

str *str::rstrip(str *chars) {
    __GC_STRING remove;
    if(chars) remove = chars->unit;
    else remove = ws;
    size_t last = unit.find_last_not_of(remove);
    if( last == std::string::npos )
        return new str("");
    return new str(unit.substr(0,last+1));
}

list<str *> *str::split(str *sp, __ss_int max_splits) {
    __GC_STRING s = unit;
    int num_splits = 0;
    size_t sep_iter = 0, tmp, chunk_iter = 0;
    list<str *> *result = new list<str *>();
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
            result->append(new str(s.substr(chunk_iter, sep_iter - chunk_iter)));
            if((tmp = skip_separator(sep_iter)) == std::string::npos) {
                chunk_iter = sep_iter;
                break;
            } else
                chunk_iter = tmp;
            ++num_splits;
        }
        if(not (max_splits < 0 or num_splits < max_splits))
            result->append(new str(s.substr(chunk_iter, s.size()-chunk_iter)));
        else if(sep_iter == std::string::npos)
            result->append(new str(s.substr(chunk_iter, s.size()-chunk_iter)));

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
            result->append(new str());
            ++num_splits;
        }
        while((max_splits < 0 or num_splits < max_splits)
              and (sep_iter = next_separator(chunk_iter)) != std::string::npos)
        {
            result->append(new str(s.substr(chunk_iter, sep_iter - chunk_iter)));
            if((tmp = skip_separator(sep_iter)) == std::string::npos) {
                chunk_iter = sep_iter;
                break;
            } else
                chunk_iter = tmp;
            ++num_splits;
        }
        if(not (max_splits < 0 or num_splits < max_splits))
            result->append(new str(s.substr(chunk_iter, s.size()-chunk_iter)));
        else if(sep_iter == std::string::npos)
            result->append(new str(s.substr(chunk_iter, s.size()-chunk_iter)));


#undef next_separator
#undef skip_separator

    }

    return result;
}

str *str::translate(str *table, str *delchars) {
    if(len(table) != 256)
        throw new ValueError(new str("translation table must be 256 characters long"));

    str *newstr = new str();

    size_t self_size = size();
    for(size_t i = 0; i < self_size; i++) {
        char c = unit[i];
        if(!delchars || delchars->unit.find(c) == std::string::npos)
            *newstr += table->unit[(unsigned char)c];
    }

    return newstr;
}

str *str::swapcase() {
    str *r = new str(unit);
    int len = __len__();
    for(int i = 0; i < len; i++)
        r->unit[i] = __case_swap_cache->unit[(unsigned char)unit[i]];
    return r;
}

str *str::center(__ss_int width, str *fillchar) {
    int len = __len__();
    if(width<=len)
        return this;

    if(!fillchar) fillchar = sp;
    str *r = fillchar->__mul__(width);

    int j = (width-len)/2;
    for(int i=0; i<len; i++)
        r->unit[j+i] = unit[i];

    return r;
}

__ss_int str::__cmp__(pyobj *p) {
    if (!p) return 1;
    str *b = (str *)p;
    int r = unit.compare(b->unit);
    if( r < 0 ) return -1;
    else if( r > 0 ) return 1;
    return 0;
}

__ss_bool str::__eq__(pyobj *p) {
    str *q = (str *)p;
    size_t len = size();
    if(len != q->size() or (hash != -1 and q->hash != -1 and hash != q->hash))
        return False;
    return __mbool(memcmp(unit.data(), q->unit.data(), len) == 0);
}

str *str::__mul__(__ss_int n) { /* optimize */
    str *r = new str();
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
str *str::__imul__(__ss_int n) {
    return __mul__(n);
}

long str::__hash__() {
    if (hash != -1)
        return hash;

    hash = std::hash<std::string>{}(unit.c_str());

    return hash; 
}

str *str::__add__(str *b) {
    str *s = new str();

    s->unit.reserve(size()+b->size());
    s->unit.append(unit);
    s->unit.append(b->unit);

    return s;
}
str *str::__iadd__(str *b) {
    return __add__(b);
}

str *__add_strs(int, str *a, str *b, str *c) {
    str *result = new str();
    int asize = a->size();
    int bsize = b->size();
    int csize = c->size();
    if(asize == 1 && bsize == 1 && csize == 1) {
        result->unit.resize(3);
        result->unit[0] = a->unit[0];
        result->unit[1] = b->unit[0];
        result->unit[2] = c->unit[0];
    }
    else {
        result->unit.resize(asize+bsize+csize);
        memcpy((void *)(result->unit.data()), a->unit.data(), asize);
        int pos = asize;
        memcpy((void *)(result->unit.data()+pos), b->unit.data(), bsize);
        pos += bsize;
        memcpy((void *)(result->unit.data()+pos), c->unit.data(), csize);
    }
    return result;
}

str *__add_strs(int, str *a, str *b, str *c, str *d) {
    str *result = new str();
    int asize = a->size();
    int bsize = b->size();
    int csize = c->size();
    int dsize = d->size();
    if(asize == 1 && bsize == 1 && csize == 1 && dsize == 1) {
        result->unit.resize(4);
        result->unit[0] = a->unit[0];
        result->unit[1] = b->unit[0];
        result->unit[2] = c->unit[0];
        result->unit[3] = d->unit[0];
    }
    else {
        result->unit.resize(asize+bsize+csize+dsize);
        memcpy((void *)(result->unit.data()), a->unit.data(), asize);
        int pos = asize;
        memcpy((void *)(result->unit.data()+pos), b->unit.data(), bsize);
        pos += bsize;
        memcpy((void *)(result->unit.data()+pos), c->unit.data(), csize);
        pos += csize;
        memcpy((void *)(result->unit.data()+pos), d->unit.data(), dsize);
    }
    return result;
}

str *__add_strs(int, str *a, str *b, str *c, str *d, str *e) {
    str *result = new str();
    int asize = a->size();
    int bsize = b->size();
    int csize = c->size();
    int dsize = d->size();
    int esize = e->size();
    if(asize == 1 && bsize == 1 && csize == 1 && dsize == 1 && esize == 1) {
        result->unit.resize(5);
        result->unit[0] = a->unit[0];
        result->unit[1] = b->unit[0];
        result->unit[2] = c->unit[0];
        result->unit[3] = d->unit[0];
        result->unit[4] = e->unit[0];
    }
    else {
        result->unit.resize(asize+bsize+csize+dsize+esize);
        memcpy((void *)(result->unit.data()), a->unit.data(), asize);
        int pos = asize;
        memcpy((void *)(result->unit.data()+pos), b->unit.data(), bsize);
        pos += bsize;
        memcpy((void *)(result->unit.data()+pos), c->unit.data(), csize);
        pos += csize;
        memcpy((void *)(result->unit.data()+pos), d->unit.data(), dsize);
        pos += dsize;
        memcpy((void *)(result->unit.data()+pos), e->unit.data(), esize);
    }
    return result;
}

str *__add_strs(int n, ...) {
    va_list ap;
    va_start(ap, n);

    int size;
    str *result = new str();

    size = 0;
    for(int i=0; i<n; i++) {
        size += len(va_arg(ap, str *));
    }
    va_end(ap);

    result->unit.resize(size);

    va_start(ap, n);
    size = 0;
    int pos = 0;
    for(int i=0; i<n; i++) {
        str *s = va_arg(ap, str *);

        memcpy((void *)(result->unit.data()+pos), s->unit.data(), s->size());
        pos += s->size();
    }
    va_end(ap);

    return result;
}

str *str::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    int len = size();
    slicenr(x, l, u, s, len);
    if(s == 1)
        return new str(unit.data()+l, u-l);
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
        return new str(r);
    }
}

__ss_int str::__fixstart(__ss_int a, __ss_int b) {
    if(a == -1) return a;
    return a+b;
}

__ss_int str::find(str *s, __ss_int a) { return __fixstart(unit.substr(a, size()-a).find(s->unit), a); }
__ss_int str::find(str *s, __ss_int a, __ss_int b) { return __fixstart(unit.substr(a, b-a).find(s->unit), a); }

__ss_int str::rfind(str *s, __ss_int a) { return __fixstart(unit.substr(a, size()-a).rfind(s->unit), a); }
__ss_int str::rfind(str *s, __ss_int a, __ss_int b) { return __fixstart(unit.substr(a, b-a).rfind(s->unit), a); }

__ss_int str::__checkneg(__ss_int i) {
    if(i == -1)
        throw new ValueError(new str("substring not found"));
    return i;
}

__ss_int str::index(str *s, __ss_int a) { return __checkneg(find(s, a)); }
__ss_int str::index(str *s, __ss_int a, __ss_int b) { return __checkneg(find(s, a, b)); }

__ss_int str::rindex(str *s, __ss_int a) { return __checkneg(find(s, a)); }
__ss_int str::rindex(str *s, __ss_int a, __ss_int b) { return __checkneg(find(s, a, b)); }

__ss_int str::count(str *s, __ss_int start) { return count(s, start, __len__()); }
__ss_int str::count(str *s, __ss_int start, __ss_int end) {
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

__ss_bool str::startswith(str *s, __ss_int start) { return startswith(s, start, __len__()); }
__ss_bool str::startswith(str *s, __ss_int start, __ss_int end) {
    __ss_int i, j, one = 1;
    slicenr(7, start, end, one, __len__());

    for(i = start, j = 0; i < end && j < len(s); )
        if (unit[i++] != s->unit[j++])
            return False;

    return __mbool(j == len(s));
}

__ss_bool str::endswith(str *s, __ss_int start) { return endswith(s, start, __len__()); }
__ss_bool str::endswith(str *s, __ss_int start, __ss_int end) {
    __ss_int i, j, one = 1;
    slicenr(7, start, end, one, __len__());

    for(i = end, j = len(s); i > start && j > 0; )
        if (unit[--i] != s->unit[--j])
            return False;

    return __mbool(j == 0);
}

str *str::replace(str *a, str *b, __ss_int c) {
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
    return new str(s);
}

str *str::upper() {
    if(size() == 1)
        return __char_cache[((unsigned char)(::toupper(unit[0])))];

    str *toReturn = new str(*this);
    std::transform(toReturn->unit.begin(), toReturn->unit.end(), toReturn->unit.begin(), toupper);

    return toReturn;
}

str *str::lower() {
    if(size() == 1)
        return __char_cache[((unsigned char)(::tolower(unit[0])))];

    str *toReturn = new str(*this);
    std::transform(toReturn->unit.begin(), toReturn->unit.end(), toReturn->unit.begin(), tolower);

    return toReturn;
}

str *str::title() {
    str *r = new str(unit);
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

str *str::casefold() {
    str *r = new str();
    size_t len = this->size();

    for(size_t i=0; i<len; i++) {
        unsigned char c = unit[i];

        if(65 >= c and c <= 90)
            c += 32;
        else if(192 >= c and c <= 214)
            c += 32;
        else if(216 >= c and c <= 222)
            c += 32;

        r->unit += c;
    }

    return r;
}

str *str::capitalize() {
    str *r = new str(unit);
    r->unit[0] = ::toupper(r->unit[0]);
    return r;
}

#ifdef __SS_BIND
str::str(PyObject *p) : hash(-1) {
    // if(!PyBytes_Check(p))
    if(!PyUnicode_Check(p))
    // if(!PyString_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (string expected)"));

    __class__ = cl_str_;
    Py_ssize_t sz;
    const char *data = PyUnicode_AsUTF8AndSize(p, &sz);
    unit = __GC_STRING(data, sz);

    // unit = __GC_STRING(PyUnicode_AsUTF8(p), PyUnicode_GET_SIZE(p));
    // unit = __GC_STRING(PyString_AsString(p), PyString_Size(p));
    // unit = __GC_STRING(PyBytes_AS_STRING(p), PyBytes_Size(p));
}

PyObject *str::__to_py__() {
//    return PyBytes_FromStringAndSize("bla", 3);
    // return PyString_FromStringAndSize(c_str(), size());
    // return PyBytes_FromStringAndSize(c_str(), size());
    return PyUnicode_DecodeLatin1(c_str(), size(), "");
}
#endif

#ifdef __SS_LONG
str *__str(__ss_int i, __ss_int base) {
    if(i<10 && i>=0 && base==10)
        return __char_cache[((unsigned char)('0'+i))];
    char buf[70];
    char *psz = buf+69;
/*    if(i==INT_MIN)
        return new str("-2147483648"); */
    int neg = i<0;
    *psz = 0;
    if(neg) i = -i;
    if(base == 10) {
        int pos;
        while(i > 999) {
            pos = 4*(i%1000);
            i = i/1000;
            *(--psz) = __str_cache[pos];
            *(--psz) = __str_cache[pos+1];
            *(--psz) = __str_cache[pos+2];
        }
        pos = 4*i;
        if(i>99) {
            *(--psz) = __str_cache[pos];
            *(--psz) = __str_cache[pos+1];
            *(--psz) = __str_cache[pos+2];
        }
        else if(i>9) {
            *(--psz) = __str_cache[pos];
            *(--psz) = __str_cache[pos+1];
        }
        else
            *(--psz) = __str_cache[pos];
    }
    else do {
        *(--psz) = "0123456789abcdefghijklmnopqrstuvwxyz"[i%base];
        i = i/base;
    } while(i);
    if(neg) *(--psz) = '-';
    return new str(psz, buf+69-psz);
}
#endif

str *__str(int i, int base) {
    if(base==10 && i<10 && i>=0)
        return __char_cache[((unsigned char)('0'+i))];

    char buf[70];
    char *psz = buf+69;
    if(base==10 and i==INT_MIN)
        return new str("-2147483648");
    int neg = i<0;
    *psz = 0;
    if(neg) i = -i;
    if(base == 10) {
        int pos;
        while(i > 999) {
            pos = 4*(i%1000);
            i = i/1000;
            *(--psz) = __str_cache[pos];
            *(--psz) = __str_cache[pos+1];
            *(--psz) = __str_cache[pos+2];
        }
        pos = 4*i;
        if(i>99) {
            *(--psz) = __str_cache[pos];
            *(--psz) = __str_cache[pos+1];
            *(--psz) = __str_cache[pos+2];
        }
        else if(i>9) {
            *(--psz) = __str_cache[pos];
            *(--psz) = __str_cache[pos+1];
        }
        else
            *(--psz) = __str_cache[pos];
    }
    else do {
        *(--psz) = "0123456789abcdefghijklmnopqrstuvwxyz"[i%base];
        i = i/base;
    } while(i);
    if(neg) *(--psz) = '-';
    return new str(psz, buf+69-psz);
}

str *__str(__ss_bool b) {
    if(b) return new str("True");
    return new str("False");
}

str *__str() { return new str(""); } /* XXX optimize */

template<> str *__str(__ss_float t) {
    std::stringstream ss;
    ss.precision(12);
    ss << std::showpoint << t;
    __GC_STRING s = ss.str().c_str();
    if(s.find('e') == std::string::npos)
    {
        unsigned int j = s.find_last_not_of("0");
        if( s[j] == '.') j++;
        s = s.substr(0, j+1);
    }
    return new str(s);
}
