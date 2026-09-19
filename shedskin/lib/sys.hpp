/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __SYS_HPP
#define __SYS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __sys__ {

void __init(int argc, char **argv);

extern list<str *> *argv;
extern str *version;
extern tuple2<__ss_int, __ss_int> *version_info;
extern str *__name__, *copyright, *platform, *byteorder;
extern __ss_int hexversion, maxsize, maxunicode;
extern str *executable;
extern file *__ss_stdin, *__ss_stdout, *__ss_stderr;
extern file *__stdin__, *__stdout__, *__stderr__;

void __ss_exit();
template<class T> void __ss_exit(T x) {
    throw new SystemExit(x);
}

extern __ss_int __recursionlimit;

void *setrecursionlimit(__ss_int limit);
__ss_int getrecursionlimit();

str *intern(str *s);
__ss_bool is_finalizing();
str *getdefaultencoding();
str *getfilesystemencoding();
str *getfilesystemencodeerrors();

extern str *float_repr_style;
extern list<str *> *orig_argv;

extern class_ *cl_float_info, *cl_implementation, *cl_flags, *cl_int_info, *cl_hash_info;

/* describes __ss_float, so it stays honest under --float32 */
class __float_info : public pyobj {
public:
    __ss_float max, min, epsilon;
    __ss_int max_exp, max_10_exp, min_exp, min_10_exp, dig, mant_dig, radix, rounds;

    __float_info();
    str *__repr__();
};

class __implementation : public pyobj {
public:
    str *name;
    tuple2<__ss_int, __ss_int> *version;
    __ss_int hexversion;

    __implementation();
    str *__repr__();
};

/* fixed: a compiled binary takes no interpreter options */
class __flags : public pyobj {
public:
    __ss_int debug, inspect, interactive, optimize, dont_write_bytecode,
        no_user_site, no_site, ignore_environment, verbose, bytes_warning,
        quiet, hash_randomization, isolated, utf8_mode, warn_default_encoding,
        int_max_str_digits, gil, thread_inherit_context, context_aware_warnings;
    __ss_bool dev_mode, safe_path;

    __flags();
    str *__repr__();
};

/* describes __ss_int (one fixed-width 'digit'), so it stays honest
   under --int32/--int128 */
class __int_info : public pyobj {
public:
    __ss_int bits_per_digit, sizeof_digit, default_max_str_digits, str_digits_check_threshold;

    __int_info();
    str *__repr__();
};

class __hash_info : public pyobj {
public:
    __ss_int width, modulus, inf, nan, imag, hash_bits, seed_bits, cutoff;
    str *algorithm;

    __hash_info();
    str *__repr__();
};

extern __float_info *float_info;
extern __implementation *implementation;
extern __flags *flags;
extern __int_info *int_info;
extern __hash_info *hash_info;

/* getsizeof: like CPython, the size of the object itself plus any buffer
   it owns, but not the objects it refers to (elements, keys, values) */

/* number of heap-allocated units behind a vector/string-like container,
   or 0 if its storage is inline (small_vector, short string optimization) */
template<class C> inline size_t __heap_units(const C &c, const void *owner, size_t owner_size) {
    const char *d = (const char *)c.data();
    const char *o = (const char *)owner;
    if (c.capacity() == 0 || (d >= o && d < o + owner_size))
        return 0;
    return c.capacity();
}

template<class C> inline size_t __hash_bytes(const C &c) {
    typedef typename C::value_type V;
    size_t buckets = c.bucket_count();
    if (buckets == 0)
        return 0;
#ifdef __SS_BOOST
    /* boost::unordered_flat_*: one buffer holding the elements and a
       16-byte metadata group per 15 slots (see foa::table_core::buffer_size) */
    size_t groups = (buckets + 1) / 15;
    size_t bytes = sizeof(V) * buckets + 16 * (groups + 1) - 1;
    return ((bytes + sizeof(V) - 1) / sizeof(V)) * sizeof(V);
#else
    /* std::unordered_*: a bucket array, plus one node per element holding
       a next pointer, the element and its cached hash code */
    return buckets * sizeof(void *) + c.size() * (sizeof(void *) + sizeof(V) + sizeof(size_t));
#endif
}

template<class T> inline __ss_int getsizeof(T, __ss_int = 0) { /* unboxed int, float, bool, complex.. */
    return (__ss_int)sizeof(T);
}

template<class T> inline __ss_int getsizeof(T *x, __ss_int = 0) {
    return (__ss_int)sizeof(T);
}

template<class T> inline __ss_int getsizeof(list<T> *x, __ss_int = 0) {
    return (__ss_int)(sizeof(*x) + __heap_units(x->units, x, sizeof(*x)) * sizeof(T));
}

template<class T> inline __ss_int getsizeof(tuple2<T, T> *x, __ss_int = 0) {
    return (__ss_int)(sizeof(*x) + __heap_units(x->units, x, sizeof(*x)) * sizeof(T));
}

inline __ss_int getsizeof(str *x, __ss_int = 0) { /* +1: terminator */
    size_t n = __heap_units(x->unit, x, sizeof(*x));
    return (__ss_int)(sizeof(*x) + (n ? n + 1 : 0) * sizeof(__ss_char));
}

inline __ss_int getsizeof(bytes *x, __ss_int = 0) {
    size_t n = __heap_units(x->unit, x, sizeof(*x));
    return (__ss_int)(sizeof(*x) + (n ? n + 1 : 0));
}

template<class K, class V> inline __ss_int getsizeof(dict<K, V> *x, __ss_int = 0) {
    return (__ss_int)(sizeof(*x) + __hash_bytes(x->gcd));
}

template<class T> inline __ss_int getsizeof(set<T> *x, __ss_int = 0) {
    return (__ss_int)(sizeof(*x) + __hash_bytes(x->gcs));
}

} // module namespace
#endif
