/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* str methods */

inline str *str::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    return __char_cache[((unsigned char)(unit[i]))];
}

inline str *str::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    return __char_cache[((unsigned char)(unit[i]))];
}

inline __ss_int str::__len__() {
    return (__ss_int)this->unit.size();
}

inline bool str::for_in_has_next(size_t i) {
    return i < this->unit.size(); /* XXX opt end cond */
}

inline str *str::for_in_next(size_t &i) {
    return __char_cache[((unsigned char)(unit[i++]))];
}

template <class U> str *str::join(U *iter) {
    size_t sz, total;
    int __2;
    bool only_ones = true;
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    U *__1;
    __join_cache->units.resize(0);
    total = 0;
    FOR_IN(e,iter,1,2,3)
        __join_cache->units.push_back(e);
        sz = e->unit.size();
        if(sz != 1)
            only_ones = false;
        total += sz;
    END_FOR
    size_t unitsize = this->unit.size();
    int elems = len(__join_cache);
    if(elems==1)
        return __join_cache->units[0];
    str *s = new str();
    if(unitsize == 0 and only_ones) {
        s->unit.resize(total);
        for(int j=0; j<elems; j++)
            s->unit[j] = __join_cache->units[j]->unit[0];
    }
    else if(elems) {
        total += (elems-1)*unitsize;
        s->unit.resize(total);
        size_t tsz;
        size_t k = 0;
        for(int m = 0; m<elems; m++) {
            str *t = __join_cache->units[m];
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

template<class ... Args> str *__add_strs(int n, Args ... args) {
    str *result = new str();
    result->unit = (args->unit + ...); /* XXX need to optimize? */
    return result;
}
