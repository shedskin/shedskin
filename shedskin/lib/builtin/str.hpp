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
    return unit.size();
}

inline bool str::for_in_has_next(size_t i) {
    return i != unit.size(); /* XXX opt end cond */
}

inline str *str::for_in_next(size_t &i) {
    return __char_cache[((unsigned char)(unit[i++]))];
}

template <class U> str *str::join(U *iter) {
    int sz, total, __2;
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
    return __join(__join_cache, only_ones, total);
}
