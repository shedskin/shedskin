/* Copyright 2005-2012 Mark Dufour and contributors; License Expat (See LICENSE) */

/* bytes methods */

inline __ss_int bytes::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    return (unsigned char)(unit[i]);
}

inline __ss_int bytes::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    return (unsigned char)(unit[i]);
}

inline void *bytes::__setitem__(__ss_int i, __ss_int e) {
    i = __wrap(this, i);
    unit[i] = (unsigned char)e;

    return NULL;
}

inline __ss_int bytes::__len__() {
    return (__ss_int)this->unit.size();
}

inline bool bytes::for_in_has_next(size_t i) {
    return i < this->unit.size(); /* XXX opt end cond */
}

inline __ss_int bytes::for_in_next(size_t &i) {
    return (unsigned char)(unit[i++]);
}

template <class U> bytes *bytes::join(U *iter) {
    size_t sz, total;
    int __2;
    bool only_ones = true;
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    U *__1;
    __join_cache_bin->units.resize(0);
    total = 0;
    FOR_IN(e,iter,1,2,3)
        __join_cache_bin->units.push_back(e);
        sz = e->unit.size();
        if(sz != 1)
            only_ones = false;
        total += sz;
    END_FOR
    size_t unitsize = this->unit.size();
    int elems = len(__join_cache_bin);
    if(elems==1)
        return __join_cache_bin->units[0];
    bytes *s = new bytes(frozen);
    if(unitsize == 0 and only_ones) {
        s->unit.resize(total);
        for(int j=0; j<elems; j++)
            s->unit[j] = __join_cache_bin->units[j]->unit[0];
    }
    else if(elems) {
        total += (elems-1)*unitsize;
        s->unit.resize(total);
        size_t tsz;
        size_t k = 0;
        for(int m = 0; m<elems; m++) {
            bytes *t = __join_cache_bin->units[m];
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
                    memcpy((void *)(s->unit.data()+k), unit.data(), this->unit.size());
                k += unitsize;
            }
        }
    }
    return s;
}
