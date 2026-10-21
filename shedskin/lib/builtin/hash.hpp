/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

typedef std::make_unsigned<__ss_int>::type __ss_uint_hash_t;

/* hash combiner (tuples, datetime): an xxHash round, as in CPython's tuple
   hash. the old boost-style combiner gave only ~65K distinct hashes for the
   1M tuples (x, y) with x, y in range(1000) */

static inline __ss_int hash_combine(__ss_int seed, __ss_int other) {
#if defined(__SS_INT32)
    uint32_t s = (uint32_t)seed, o = (uint32_t)other;
    s += o * 2246822519U;
    s = (s << 13) | (s >> 19);
    s *= 2654435761U;
    return (__ss_int)s;
#else
    uint64_t s = (uint64_t)seed, o = (uint64_t)other;
    s += o * 14029467366897019727ULL;
    s = (s << 31) | (s >> 33);
    s *= 11400714785074694791ULL;
    return (__ss_int)(int64_t)s;
#endif
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

/* integers hash to themselves, as in CPython (std::hash is the identity for
   integers with libstdc++/libc++, but not with MSVC, which uses FNV-1a) */

#if defined(__SS_INT64)
    template<> inline __ss_int hasher(__ss_int a) { return a; }
#elif defined(__SS_INT128)
    template<> inline __ss_int hasher(__ss_int a) {
        if ((__ss_int)(int64_t)a == a)
            return a;
        return hash_combine((__ss_int)(int64_t)a, (__ss_int)(int64_t)(a>>64));
    }
#endif

template<> inline __ss_int hasher(int a) { return (__ss_int)a; } // TODO avoid by updating lib code with __ss_int
template<> inline __ss_int hasher(__ss_float a) { return (__ss_int)std::hash<__ss_float>{}(a); }
template<> inline __ss_int hasher(__ss_bool a) { return (__ss_int)a.value; }
template<> inline __ss_int hasher(void *v) { return (__ss_int)std::hash<void *>{}(v); }

/* hash() builtin: like CPython, never return -1 (in CPython, -1 signals an
   error in the C API), so for example hash(-1) == -2 */

template<class T> inline __ss_int ___hash(T t) {
    __ss_int h = hasher<T>(t);
    return h == -1 ? -2 : h;
}

template<class T> class ss_hash {
    public:
        __ss_int operator()(const T t) const {
            return hasher<T>(t);
        }

};

