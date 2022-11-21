/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

/* bytes methods TODO share code with str */

bytes::bytes(int frozen) : hash(-1), frozen(frozen) {
    __class__ = cl_bytes;
}

bytes::bytes(const char *s) : unit(s), hash(-1), frozen(1) {
    __class__ = cl_bytes;
}

bytes::bytes(__GC_STRING s) : unit(s), hash(-1), frozen(1) {
    __class__ = cl_bytes;
}

bytes::bytes(bytes *b, int frozen) : hash(-1), frozen(frozen) {
    __class__ = cl_bytes;
    unit = b->unit;
}

bytes::bytes(const char *s, int size) : unit(s, size), hash(-1), frozen(1) { /* '\0' delimiter in C */
    __class__ = cl_bytes;
}

const char *bytes::c_str() const {
    return this->unit.c_str();
}

const int bytes::size() const {
    return this->unit.size();
}

str *bytes::__str__() {
    return __repr__();
}

const int bytes::find(const char c, int a) const {
    return this->unit.find(c, a);
}

const int bytes::find(const char *c, int a) const {
    return this->unit.find(c, a);
}

int bytes::__fixstart(int a, int b) {
    if(a == -1) return a;
    return a+b;
}

int bytes::find(bytes *s, int a) { return __fixstart(unit.substr(a, size()-a).find(s->unit), a); }
int bytes::find(bytes *s, int a, int b) { return __fixstart(unit.substr(a, b-a).find(s->unit), a); }

str *bytes::__repr__() {
    std::stringstream ss;
    __GC_STRING sep = "\\\n\r\t";
    __GC_STRING let = "\\nrt";

    const char *quote = "'";
    int hasq = find('\'');
    int hasd = find('\"');

    if (hasq != -1 && hasd != -1) {
        sep += "'"; let += "'";
    }
    if (hasq != -1 && hasd == -1)
        quote = "\"";

    if(frozen == 0)
        ss << "bytearray(";

    ss << 'b';
    ss << quote;
    for(unsigned int i=0; i<size(); i++)
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
    if(frozen == 0)
        ss << ')';

    return new str(ss.str().c_str());
}

long bytes::__hash__() {
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
    bytes *s = new bytes();

    s->unit.reserve(size()+b->size());
    s->unit.append(unit);
    s->unit.append(b->unit);

    return s;
}

bytes *bytes::__iadd__(bytes *b) {
    return __add__(b);
}

bytes *bytes::__mul__(__ss_int n) { /* optimize */
    bytes *r = new bytes();
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
        b = new bytes(unit.data()+l, u-l);
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
        b = new bytes(r);
    }
    b->frozen = 1;
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
    int last = unit.find_last_not_of(remove);
    if( last == -1 )
        return new bytes();
    return new bytes(unit.substr(0,last+1));
}

bytes *bytes::lstrip(bytes *chars) {
    __GC_STRING remove;
    if(chars) remove = chars->unit;
    else remove = ws;
    int first = unit.find_first_not_of(remove);
    if( first == -1 )
        return new bytes();
    return new bytes(unit.substr(first,size()-first));
}

bytes *bytes::strip(bytes *chars) {
    return lstrip(chars)->rstrip(chars);
}

list<bytes *> *bytes::split(bytes *sp, int max_splits) {
    __GC_STRING s = unit;
    int num_splits = 0;
    int sep_iter = 0, tmp, chunk_iter = 0;
    list<bytes *> *result = new list<bytes *>();
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
            result->append(new bytes(s.substr(chunk_iter, sep_iter - chunk_iter)));
            if((tmp = skip_separator(sep_iter)) == -1) {
                chunk_iter = sep_iter;
                break;
            } else
                chunk_iter = tmp;
            ++num_splits;
        }
        if(not (max_splits < 0 or num_splits < max_splits))
            result->append(new bytes(s.substr(chunk_iter, s.size()-chunk_iter)));
        else if(sep_iter == -1)
            result->append(new bytes(s.substr(chunk_iter, s.size()-chunk_iter)));

#undef next_separator
#undef skip_separator

    } else { /* given separator (slightly different algorithm required)
              * (python is very inconsistent in this respect) */
        const char *sep = sp->c_str();
        int sep_size = sp->size();

#define next_separator(iter) s.find(sep, (iter))
#define skip_separator(iter) ((iter + sep_size) > s.size()? -1 : (iter + sep_size))

        if (max_splits == 0) {
            result->append(this);
            return result;
        }
        if(next_separator(chunk_iter) == 0) {
            chunk_iter = skip_separator(chunk_iter);
            result->append(new bytes());
            ++num_splits;
        }
        while((max_splits < 0 or num_splits < max_splits)
              and (sep_iter = next_separator(chunk_iter)) != -1)
        {
            result->append(new bytes(s.substr(chunk_iter, sep_iter - chunk_iter)));
            if((tmp = skip_separator(sep_iter)) == -1) {
                chunk_iter = sep_iter;
                break;
            } else
                chunk_iter = tmp;
            ++num_splits;
        }
        if(not (max_splits < 0 or num_splits < max_splits))
            result->append(new bytes(s.substr(chunk_iter, s.size()-chunk_iter)));
        else if(sep_iter == -1)
            result->append(new bytes(s.substr(chunk_iter, s.size()-chunk_iter)));


#undef next_separator
#undef skip_separator

    }

    return result;
}
