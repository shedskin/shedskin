/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

/* hashing */

static inline long hash_combine(long seed, long other) {
    return seed ^ (other + 0x9e3779b9 + (seed << 6) + (seed >> 2));
}

template<class T> inline long hasher(T t) {
    if(t == NULL) return 0;
    return t->__hash__();
}

#if defined(__SS_INT64)
    template<> inline long hasher(__ss_int a) { return (long)std::hash<__ss_int>{}(a); }
#elif defined(__SS_INT128)
    template<> inline long hasher(__ss_int a) { return hash_combine(std::hash<int64_t>{}((int64_t)a), std::hash<int64_t>{}((int64_t)(a>>64))); }
#endif

template<> inline long hasher(int a) { return (long)std::hash<int>{}(a); } // TODO avoid by updating lib code with __ss_int
template<> inline long hasher(__ss_float a) { return (long)std::hash<__ss_float>{}(a); }
template<> inline long hasher(__ss_bool a) { return (long)std::hash<uint8_t>{}(a.value); }
template<> inline long hasher(void *v) { return (long)std::hash<void *>{}(v); }

template<class T> class ss_hash {
    public:
        long operator()(const T t) const {
            return hasher<T>(t);
        }

};

