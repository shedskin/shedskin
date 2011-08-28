/* Copyright 2005-2011 Mark Dufour and contributors; License MIT (See LICENSE) */

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

str *str::__str__() { // weg?
    return this;
}

str *str::__repr__() {
    std::stringstream ss;
    __GC_STRING sep = "\\\n\r\t";
    __GC_STRING let = "\\nrt";

    const char *quote = "'";
    int hasq = unit.find("'");
    int hasd = unit.find("\"");

    if (hasq != -1 && hasd != -1) {
        sep += "'"; let += "'";
    }
    if (hasq != -1 && hasd == -1)
        quote = "\"";

    ss << quote;
    for(unsigned int i=0; i<unit.size(); i++)
    {
        char c = unit[i];
        int k;

        if((k = sep.find_first_of(c)) != -1)
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

str *str::__join(pyseq<str *> *l, bool only_ones, int total) {
    int unitsize = unit.size();
    int elems = len(l);
    if(elems==1)
        return l->__getitem__(0);
    str *s = new str();
    if(unitsize == 0 and only_ones) {
        s->unit.resize(total);
        for(int j=0; j<elems; j++)
            s->unit[j] = l->__getitem__(j)->unit[0];
    }
    else if(elems) {
        total += (elems-1)*unitsize;
        s->unit.resize(total);
        int tsz;
        int k = 0;
        for(int m = 0; m<elems; m++) {
            str *t = l->__getitem__(m);
            tsz = t->unit.size();
            if (tsz == 1)
                s->unit[k] = t->unit[0];
            else
                memcpy((void *)(s->unit.data()+k), t->unit.data(), tsz);
            k += tsz;
            if (unitsize && m < elems-1) {
                if (unitsize==1)
                    s->unit[k] = unit[0];
                else
                    memcpy((void *)(s->unit.data()+k), unit.data(), unit.size());
                k += unitsize;
            }
        }
    }
    return s;
}

str * str::join(list<str *> *l) {
    int lsz = len(l);
    if(lsz==1)
        return l->units[0];
    int sz, total;
    bool only_ones = true;
    total = 0;
    for(int i=0; i<lsz; i++) {
        sz = l->units[i]->unit.size();
        if(sz!=1)
            only_ones = false;
        total += sz;
    }
    return __join(l, only_ones, total);
}

str * str::join(tuple2<str *, str *> *l) { /* XXX merge */
    int lsz = len(l);
    int sz, total;
    bool only_ones = true;
    total = 0;
    for(int i=0; i<lsz; i++) {
        sz = l->units[i]->unit.size();
        if(sz!=1)
            only_ones = false;
        total += sz;
    }
    return __join(l, only_ones, total);
}

__ss_int str::__int__() {
    return __int(this);
}

__ss_bool str::__contains__(str *s) {
    return __mbool(unit.find(s->unit) != std::string::npos);
}

__ss_bool str::__ctype_function(int (*cfunc)(int))
{
  int i, l = unit.size();
  if(!l)
      return False;

  for(i = 0; i < l; i++)
      if(!cfunc((int)unit[i])) return False;

  return True;
}

__ss_bool str::isspace() { return __mbool(unit.size() && (unit.find_first_not_of(ws) == std::string::npos)); }
__ss_bool str::isdigit() { return __ctype_function(&::isdigit); }
__ss_bool str::isalpha() { return __ctype_function(&::isalpha); }
__ss_bool str::isalnum() { return __ctype_function(&::isalnum); }
__ss_bool str::islower() { return __ctype_function(&::islower); }
__ss_bool str::isupper() { return __ctype_function(&::isupper); }

str *str::ljust(int width, str *s) {
    if(width<=__len__()) return this;
    if(!s) s = sp;
    return __add__(s->__mul__(width-__len__()));
}

str *str::rjust(int width, str *s) {
    if(width<=__len__()) return this;
    if(!s) s = sp;
    return s->__mul__(width-__len__())->__add__(this);
}

str *str::zfill(int width) {
    if(width<=__len__()) return this;
    return (new str("0"))->__mul__(width-__len__())->__add__(this);
}

str *str::expandtabs(int width) {
    int i;
    __GC_STRING r = unit;
    while((i = r.find("\t")) != -1)
        r.replace(i, 1, (new str(" "))->__mul__(width-i%width)->unit);
    return new str(r);
}

str *str::strip(str *chars) {
    return lstrip(chars)->rstrip(chars);
}

str *str::lstrip(str *chars) {
    __GC_STRING remove;
    if(chars) remove = chars->unit;
    else remove = ws;
    int first = unit.find_first_not_of(remove);
    if( first == -1 )
        return new str("");
    return new str(unit.substr(first,unit.size()-first));
}



tuple2<str *, str *> *str::partition(str *sep)
{
    int i;

    i = unit.find(sep->unit);
    if(i != -1)
        return new tuple2<str *, str *>(3, new str(unit.substr(0, i)), new str(sep->unit), new str(unit.substr(i + sep->unit.length())));
    else
        return new tuple2<str *, str *>(3, new str(unit), new str(""), new str(""));
}

tuple2<str *, str *> *str::rpartition(str *sep)
{
    int i;

    i = unit.rfind(sep->unit);
    if(i != -1)
        return new tuple2<str *, str *>(3, new str(unit.substr(0, i)), new str(sep->unit), new str(unit.substr(i + sep->unit.length())));
    else
        return new tuple2<str *, str *>(3, new str(unit), new str(""), new str(""));
}

list<str *> *str::rsplit(str *sep, int maxsep)
{
    __GC_STRING ts;
    list<str *> *r = new list<str *>();
    int i, j, curi, tslen;

    curi = 0;
    i = j = unit.size() - 1;

    //split by whitespace
    if(!sep)
    {
        while(i > 0 && j > 0 && (curi < maxsep || maxsep < 0))
        {
            j = unit.find_last_not_of(ws, i);
            if(j == -1) break;

            i = unit.find_last_of(ws, j);

            //this works out pretty nicely; i will be -1 if no more is found, and thus i + 1 will be 0th index
            r->append(new str(unit.substr(i + 1, j - i)));
            curi++;
        }

        //thus we only bother about extra stuff here if we *have* found more whitespace
        if(i > 0 && j >= 0 && (j = unit.find_last_not_of(ws, i)) >= 0) r->append(new str(unit.substr(0, j)));
    }

    //split by seperator
    else
    {
        ts = sep->unit;
        tslen = ts.length();

        i++;
        while(i > 0 && j > 0 && (curi < maxsep || maxsep < 0))
        {
            j = i;
            i--;

            i = unit.rfind(ts, i);
            if(i == -1)
            {
                i = j;
                break;
            }

            r->append(new str(unit.substr(i + tslen, j - i - tslen)));

            curi++;
        }

        //either left over (beyond max) or very last match (see loop break)
        if(i >= 0) r->append(new str(unit.substr(0, i)));
    }

    r->reverse();

    return r;
}

__ss_bool str::istitle()
{
    int i, len;

    len = unit.size();
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

list<str *> *str::splitlines(int keepends)
{
    list<str *> *r = new list<str *>();
    int i, endlen;
    unsigned int j;
    const char *ends = "\r\n";

    endlen = i = 0;
    do
    {
        j = i + endlen;
        i = unit.find_first_of(ends, j);
        if(i == -1) break;

        //for all we know the character sequence could change mid-way...
        if(unit[i] == '\r' && unit[i + 1] == '\n') endlen = 2;
        else endlen = 1;

        r->append(new str(unit.substr(j, i - j + (keepends ? endlen : 0))));
    }
    while(i >= 0);

    if(j != unit.size()) r->append(new str(unit.substr(j)));

    return r;
}

str *str::rstrip(str *chars) {
    __GC_STRING remove;
    if(chars) remove = chars->unit;
    else remove = ws;
    int last = unit.find_last_not_of(remove);
    if( last == -1 )
        return new str("");
    return new str(unit.substr(0,last+1));
}

list<str *> *str::split(str *sp, int max_splits) {
    __GC_STRING s = unit;
    int num_splits = 0;
    int sep_iter = 0, tmp, chunk_iter = 0;
    list<str *> *result = new list<str *>();
    if (sp == NULL)
    {
#define next_separator(iter) (s.find_first_of(ws, (iter)))
#define skip_separator(iter) (s.find_first_not_of(ws, (iter)))

        if(skip_separator(chunk_iter) == -1) /* XXX */
            return result;
        if(next_separator(chunk_iter) == 0)
            chunk_iter = skip_separator(chunk_iter);
        while((max_splits < 0 or num_splits < max_splits)
              and ((sep_iter = next_separator(chunk_iter)) != -1))
        {
            result->append(new str(s.substr(chunk_iter, sep_iter - chunk_iter)));
            if((tmp = skip_separator(sep_iter)) == -1) {
                chunk_iter = sep_iter;
                break;
            } else
                chunk_iter = tmp;
            ++num_splits;
        }
        if(not (max_splits < 0 or num_splits < max_splits))
            result->append(new str(s.substr(chunk_iter, s.size()-chunk_iter)));
        else if(sep_iter == -1)
            result->append(new str(s.substr(chunk_iter, s.size()-chunk_iter)));

#undef next_separator
#undef skip_separator

    } else { /* given separator (slightly different algorithm required)
              * (python is very inconsistent in this respect) */
        const char *sep = sp->unit.c_str();
        int sep_size = sp->unit.size();

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
              and (sep_iter = next_separator(chunk_iter)) != -1)
        {
            result->append(new str(s.substr(chunk_iter, sep_iter - chunk_iter)));
            if((tmp = skip_separator(sep_iter)) == -1) {
                chunk_iter = sep_iter;
                break;
            } else
                chunk_iter = tmp;
            ++num_splits;
        }
        if(not (max_splits < 0 or num_splits < max_splits))
            result->append(new str(s.substr(chunk_iter, s.size()-chunk_iter)));
        else if(sep_iter == -1)
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

    int self_size = unit.size();
    for(int i = 0; i < self_size; i++) {
        char c = unit[i];
        if(!delchars || delchars->unit.find(c) == std::string::npos)
            newstr->unit.push_back(table->unit[(unsigned char)c]);
    }

    return newstr;
}

str *str::swapcase() {
    str *r = new str(unit);
    int len = __len__();

    for(int i = 0; i < len; i++) {
        char c = unit[i];
        if( c >= 'a' && c <= 'z' )
            r->unit[i] = ::toupper(c);
        else if( c >= 'A' && c <= 'Z' )
            r->unit[i] = ::tolower(c);
    }

    return r;
}

str *str::center(int w, str *fill) {
    int len = __len__();
    if(w<=len)
        return this;

    if(!fill) fill = sp;
    str *r = fill->__mul__(w);

    int j = (w-len)/2;
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
    size_t len = unit.size();
    if(len != q->unit.size() or (hash != -1 and q->hash != -1 and hash != q->hash))
        return False;
    return __mbool(memcmp(unit.data(), q->unit.data(), len) == 0);
}

str *str::__mul__(__ss_int n) { /* optimize */
    str *r = new str();
    if(n<=0) return r;
    __GC_STRING &s = r->unit;
    __ss_int ulen = unit.size();

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
    if(hash != -1)
        return hash;
    long x;
    const unsigned char *data = (unsigned char *)unit.data();
    int len = __len__();
#ifdef __SS_FASTHASH
//-----------------------------------------------------------------------------
// MurmurHash2, by Austin Appleby
// http://sites.google.com/site/murmurhash/

// All code is released to the public domain. 
// For business purposes, Murmurhash is under the MIT license. 

// Note - This code makes a few assumptions about how your machine behaves -

// 1. We can read a 4-byte value from any address without crashing
// 2. sizeof(int) == 4

// And it has a few limitations -

// 1. It will not work incrementally.
// 2. It will not produce the same results on little-endian and big-endian
//    machines.

// 'm' and 'r' are mixing constants generated offline.
// They're not really 'magic', they just happen to work well.
    unsigned int seed = 12345678; /* XXX */
	const unsigned int m = 0x5bd1e995;
	const int r = 24;

	// Initialize the hash to a 'random' value

	x = seed ^ len;

	// Mix 4 bytes at a time into the hash

	while(len >= 4)
	{
		unsigned int k = *(unsigned int *)data;

		k *= m; 
		k ^= k >> r; 
		k *= m; 
		
		x *= m; 
		x ^= k;

		data += 4;
		len -= 4;
	}
	
	// Handle the last few bytes of the input array

	switch(len)
	{
        case 3: x ^= data[2] << 16;
        case 2: x ^= data[1] << 8;
        case 1: x ^= data[0];
                x *= m;
	};

	// Do a few final mixes of the hash to ensure the last few
	// bytes are well-incorporated.

	x ^= x >> 13;
	x *= m;
	x ^= x >> 15;
#else
    /* modified from CPython */
    x = *data << 7;
    while (--len >= 0)
        x = (1000003*x) ^ *data++;
    x ^= __len__();
    if (x == -1)
        x = -2;
#endif
    hash = x;
    return x; 
}

str *str::__add__(str *b) {
    str *s = new str();

    s->unit.reserve(unit.size()+b->unit.size());
    s->unit.append(unit);
    s->unit.append(b->unit);

    return s;
}
str *str::__iadd__(str *b) {
    return __add__(b);
}

str *__add_strs(int, str *a, str *b, str *c) {
    str *result = new str();
    int asize = a->unit.size();
    int bsize = b->unit.size();
    int csize = c->unit.size();
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
    int asize = a->unit.size();
    int bsize = b->unit.size();
    int csize = c->unit.size();
    int dsize = d->unit.size();
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
    int asize = a->unit.size();
    int bsize = b->unit.size();
    int csize = c->unit.size();
    int dsize = d->unit.size();
    int esize = e->unit.size();
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

        memcpy((void *)(result->unit.data()+pos), s->unit.data(), s->unit.size());
        pos += s->unit.size();
    }
    va_end(ap);

    return result;
}

str *str::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    int len = unit.size();
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

int str::__fixstart(int a, int b) {
    if(a == -1) return a;
    return a+b;
}

int str::find(str *s, int a) { return __fixstart(unit.substr(a, unit.size()-a).find(s->unit), a); }
int str::find(str *s, int a, int b) { return __fixstart(unit.substr(a, b-a).find(s->unit), a); }

int str::rfind(str *s, int a) { return __fixstart(unit.substr(a, unit.size()-a).rfind(s->unit), a); }
int str::rfind(str *s, int a, int b) { return __fixstart(unit.substr(a, b-a).rfind(s->unit), a); }

int str::__checkneg(int i) {
    if(i == -1)
        throw new ValueError(new str("substring not found"));
    return i;
}

int str::index(str *s, int a) { return __checkneg(find(s, a)); }
int str::index(str *s, int a, int b) { return __checkneg(find(s, a, b)); }

int str::rindex(str *s, int a) { return __checkneg(find(s, a)); }
int str::rindex(str *s, int a, int b) { return __checkneg(find(s, a, b)); }

__ss_int str::count(str *s, __ss_int start) { return count(s, start, __len__()); }
__ss_int str::count(str *s, __ss_int start, __ss_int end) {
    __ss_int i, count, one = 1;
    slicenr(7, start, end, one, __len__());

    i = start; count = 0;
    while( ((i = unit.find(s->unit, i)) != -1) && (i <= end-len(s)) )
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

    return True;
}

str *str::replace(str *a, str *b, int c) {
    __GC_STRING s = unit;
    int i, j, p;
    int asize = a->unit.size();
    int bsize = b->unit.size();
    j = p = 0;
    while( ((c==-1) || (j++ != c)) && (i = s.find(a->unit, p)) != -1 ) {
      s.replace(i, asize, b->unit);
      p = i + bsize + (asize?0:1);
    }
    return new str(s);
}

str *str::upper() {
    if(unit.size() == 1)
        return __char_cache[((unsigned char)(::toupper(unit[0])))];

    str *toReturn = new str(*this);
    std::transform(toReturn->unit.begin(), toReturn->unit.end(), toReturn->unit.begin(), toupper);

    return toReturn;
}

str *str::lower() {
    if(unit.size() == 1)
        return __char_cache[((unsigned char)(::tolower(unit[0])))];

    str *toReturn = new str(*this);
    std::transform(toReturn->unit.begin(), toReturn->unit.end(), toReturn->unit.begin(), tolower);

    return toReturn;
}

str *str::title() {
    str *r = new str(unit);
    bool up = true;
    size_t len = this->unit.size();
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

str *str::capitalize() {
    str *r = new str(unit);
    r->unit[0] = ::toupper(r->unit[0]);
    return r;
}

#ifdef __SS_BIND
str::str(PyObject *p) : hash(-1) {
    if(!PyString_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (string expected)"));

    __class__ = cl_str_;
    unit = __GC_STRING(PyString_AsString(p), PyString_Size(p));
}

PyObject *str::__to_py__() {
    return PyString_FromStringAndSize(unit.c_str(), unit.size());
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

template<> str *__str(double t) {
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
