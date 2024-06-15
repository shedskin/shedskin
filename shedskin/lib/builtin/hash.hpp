/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

/* hashing */

static inline long hash_combine(long seed, long other) {
    return seed ^ (other + 0x9e3779b9 + (seed << 6) + (seed >> 2));
}

template<class T> inline long hasher(T t) {
    if(t == NULL) return 0;
    return t->__hash__();
}
#ifdef __SS_LONG
template<> inline long hasher(__ss_int a) { return (a==-1)?-2:a; }
#endif
template<> inline long hasher(int a) { return (a==-1)?-2:a; }
template<> inline long hasher(__ss_bool a) { return a.value; }
template<> inline long hasher(void *a) { return (intptr_t)a; }
template<> inline long hasher(__ss_float v) { return std::hash<__ss_float>{}(v); }

template<class T> class ss_hash {
    public:
        long operator()(const T t) const {
            return hasher<T>(t);
        }

};

