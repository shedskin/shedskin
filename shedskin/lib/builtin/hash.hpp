/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

/* hash combiner (TODO only used for tuples? move there/check cpython?) */

typedef std::make_unsigned<__ss_int>::type __ss_uint_hash_t;

static inline __ss_int hash_combine(__ss_int seed, __ss_int other) {
    __ss_uint_hash_t s = (__ss_uint_hash_t)seed, o = (__ss_uint_hash_t)other;
    return (__ss_int)(s ^ (o + 0x9e3779b9 + (s << 6) + (s >> 2)));
}

/* bit shuffler */

static inline __ss_int hash_shuffle_bits(__ss_int h)
{
    __ss_uint_hash_t u = (__ss_uint_hash_t)h;
    return (__ss_int)(((u ^ 89869747UL) ^ (u << 16)) * 3644798167UL);
}

template<class T> inline __ss_int hasher(T t) {
    if(t == NULL) return 0;
    return t->__hash__();
}

#if defined(__SS_INT64)
    template<> inline __ss_int hasher(__ss_int a) { return (__ss_int)std::hash<__ss_int>{}(a); }
#elif defined(__SS_INT128)
    template<> inline __ss_int hasher(__ss_int a) { return hash_combine((__ss_int)std::hash<int64_t>{}((int64_t)a), (__ss_int)std::hash<int64_t>{}((int64_t)(a>>64))); }
#endif

template<> inline __ss_int hasher(int a) { return (__ss_int)std::hash<int>{}(a); } // TODO avoid by updating lib code with __ss_int
template<> inline __ss_int hasher(__ss_float a) { return (__ss_int)std::hash<__ss_float>{}(a); }
template<> inline __ss_int hasher(__ss_bool a) { return (__ss_int)std::hash<uint8_t>{}(a.value); }
template<> inline __ss_int hasher(void *v) { return (__ss_int)std::hash<void *>{}(v); }

template<class T> class ss_hash {
    public:
        __ss_int operator()(const T t) const {
            return hasher<T>(t);
        }

};

