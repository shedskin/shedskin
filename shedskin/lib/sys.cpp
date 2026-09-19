/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "sys.hpp"
#include <stdio.h>
#include <climits>
#include <limits>
#include <cfloat>

namespace __sys__ {

list<str *> *argv, *orig_argv;
str *version, *float_repr_style;

class_ *cl_float_info, *cl_implementation, *cl_flags, *cl_int_info, *cl_hash_info;
__float_info *float_info;
__implementation *implementation;
__flags *flags;
__int_info *int_info;
__hash_info *hash_info;

tuple2<__ss_int, __ss_int> *version_info;
str *__name__, *copyright, *platform, *byteorder;
__ss_int hexversion, maxsize, maxunicode;
str *executable;
file *__ss_stdin, *__ss_stdout, *__ss_stderr;
file *__stdin__, *__stdout__, *__stderr__;

void __init(int c, char **v) {
    argv = new list<str *>();

#if defined( _MSC_VER )
    version = new str("Shed Skin Python-to-C++ Compiler 0.9.13\n[MSVC ");
    version = version->__add__(__str(_MSC_VER))->__add__(new str("]"));
#else
    version = new str("Shed Skin Python-to-C++ Compiler 0.9.13\n[GCC ");
    version = version->__add__(new str(__VERSION__))->__add__(new str("]"));
#endif
    version_info = new tuple2<__ss_int, __ss_int>(5, (__ss_int)3, (__ss_int)14, (__ss_int)0, (__ss_int)0, (__ss_int)0);
    hexversion = 0x030e00f0;

    copyright = new str("Copyright (c) Mark Dufour 2005-2026.\nAll Rights Reserved.");

    platform = new str("unknown");
#ifdef __linux__
    platform = new str("linux");
#endif
#ifdef __APPLE__
    platform = new str("darwin");
#endif
#ifdef WIN32
    platform = new str("win32");
#endif

    maxsize = std::numeric_limits<__ss_int>::max();
    maxunicode = 0x10ffff; /* str holds full unicode code points; chr()/ord() cover range(0x110000) */

    /* a compiled binary has no interpreter options in front of the
       program arguments, so orig_argv equals argv here */
    orig_argv = new list<str *>();
    for(int i=0; i<c; i++) {
        argv->append(new str(v[i]));
        orig_argv->append(new str(v[i]));
    }

    float_repr_style = new str("short");

    cl_float_info = new class_("float_info");
    cl_implementation = new class_("implementation");
    cl_flags = new class_("flags");
    cl_int_info = new class_("int_info");
    cl_hash_info = new class_("hash_info");
    float_info = new __float_info();
    implementation = new __implementation();
    flags = new __flags();
    int_info = new __int_info();
    hash_info = new __hash_info();

    executable = (c > 0) ? new str(v[0]) : new str("");

    __ss_stdin = __shedskin__::__ss_stdin;
    __ss_stdout = __shedskin__::__ss_stdout;
    __ss_stderr = __shedskin__::__ss_stderr;
    __stdin__ = __ss_stdin;
    __stdout__ = __ss_stdout;
    __stderr__ = __ss_stderr;

    int num = 1;
    if (*(char *)&num == 1)
        byteorder = new str("little");
    else
        byteorder = new str("big");
}

void __ss_exit() {
    throw new SystemExit((__ss_int)0);
}

__ss_int __recursionlimit = 1000; /* CPython's default */

void *setrecursionlimit(__ss_int limit) {
    if (limit < 1)
        throw new ValueError(new str("recursion limit must be greater or equal than 1"));
    __recursionlimit = limit;
    return NULL;
}

__ss_int getrecursionlimit() {
    return __recursionlimit;
}

str *intern(str *s) {
    return s; /* interning is a pure perf hint in CPython; identity is spec-compliant */
}

__ss_bool is_finalizing() {
    return False; /* no interpreter teardown phase in a compiled binary */
}

str *getdefaultencoding() {
    return new str("utf-8");
}

str *getfilesystemencoding() {
    return new str("utf-8");
}

str *getfilesystemencodeerrors() {
#ifdef WIN32
    return new str("surrogatepass");
#else
    return new str("surrogateescape");
#endif
}

__float_info::__float_info() {
    typedef std::numeric_limits<__ss_float> lim;
    this->__class__ = cl_float_info;
    this->max = lim::max();
    this->max_exp = lim::max_exponent;
    this->max_10_exp = lim::max_exponent10;
    this->min = lim::min();
    this->min_exp = lim::min_exponent;
    this->min_10_exp = lim::min_exponent10;
    this->dig = lim::digits10;
    this->mant_dig = lim::digits;
    this->epsilon = lim::epsilon();
    this->radix = lim::radix;
    this->rounds = FLT_ROUNDS;
}

str *__float_info::__repr__() {
    return __mod6(new str("sys.float_info(max=%s, max_exp=%d, max_10_exp=%d, min=%s, min_exp=%d, min_10_exp=%d, dig=%d, mant_dig=%d, epsilon=%s, radix=%d, rounds=%d)"), 11,
        repr(this->max), this->max_exp, this->max_10_exp,
        repr(this->min), this->min_exp, this->min_10_exp,
        this->dig, this->mant_dig, repr(this->epsilon),
        this->radix, this->rounds);
}

__implementation::__implementation() {
    this->__class__ = cl_implementation;
    this->name = new str("shedskin");
    this->version = version_info;
    this->hexversion = __sys__::hexversion;
}

str *__implementation::__repr__() {
    return __mod6(new str("namespace(name=%s, version=%s, hexversion=%d)"), 3,
        repr(this->name), repr(this->version), this->hexversion);
}

__flags::__flags() {
    this->__class__ = cl_flags;
    debug = inspect = interactive = dont_write_bytecode = 0;
    no_user_site = no_site = ignore_environment = verbose = 0;
    bytes_warning = quiet = isolated = warn_default_encoding = 0;
    thread_inherit_context = context_aware_warnings = 0;
#ifdef __SS_NOASSERT
    optimize = 1; /* like 'python -O': assert statements are compiled out */
#else
    optimize = 0;
#endif
    hash_randomization = 0; /* str/bytes hashes are not seeded */
    utf8_mode = 1; /* utf-8 is used for file names and I/O, independent of the locale */
    int_max_str_digits = 0; /* no int/str conversion limit */
    gil = 1; /* not a free-threaded build */
    dev_mode = False;
    safe_path = False;
}

str *__flags::__repr__() {
    return __mod6(new str("sys.flags(debug=%d, inspect=%d, interactive=%d, optimize=%d, dont_write_bytecode=%d, no_user_site=%d, no_site=%d, ignore_environment=%d, verbose=%d, bytes_warning=%d, quiet=%d, hash_randomization=%d, isolated=%d, dev_mode=%s, utf8_mode=%d, warn_default_encoding=%d, safe_path=%s, int_max_str_digits=%d, gil=%d, thread_inherit_context=%d, context_aware_warnings=%d)"), 21,
        debug, inspect, interactive, optimize, dont_write_bytecode,
        no_user_site, no_site, ignore_environment, verbose, bytes_warning,
        quiet, hash_randomization, isolated, repr(dev_mode), utf8_mode,
        warn_default_encoding, repr(safe_path), int_max_str_digits, gil,
        thread_inherit_context, context_aware_warnings);
}

__int_info::__int_info() {
    this->__class__ = cl_int_info;
    bits_per_digit = (__ss_int)(sizeof(__ss_int) * CHAR_BIT - 1); /* value bits, excluding the sign */
    sizeof_digit = (__ss_int)sizeof(__ss_int);
    default_max_str_digits = 0; /* no limit, see flags.int_max_str_digits */
    str_digits_check_threshold = 640; /* CPython's lowest non-zero limit */
}

str *__int_info::__repr__() {
    return __mod6(new str("sys.int_info(bits_per_digit=%d, sizeof_digit=%d, default_max_str_digits=%d, str_digits_check_threshold=%d)"), 4,
        bits_per_digit, sizeof_digit, default_max_str_digits, str_digits_check_threshold);
}

__hash_info::__hash_info() {
    this->__class__ = cl_hash_info;
    width = (__ss_int)(sizeof(__ss_int) * CHAR_BIT);
    modulus = 0; /* numeric hashes are not reduced modulo a prime */
    inf = hasher<__ss_float>(std::numeric_limits<__ss_float>::infinity());
    nan = 0; /* no longer used (as in CPython) */
    imag = 1000003; /* see complex::__hash__ */
    /* str/bytes are hashed with the C++ library's std::hash */
#if defined(_MSC_VER)
    algorithm = new str("fnv");
#elif defined(_LIBCPP_VERSION)
    algorithm = new str("cityhash");
#else
    algorithm = new str("murmur2");
#endif
    hash_bits = (__ss_int)(sizeof(size_t) * CHAR_BIT);
    seed_bits = 0; /* not seeded, see flags.hash_randomization */
    cutoff = 0; /* no small-string optimization */
}

str *__hash_info::__repr__() {
    return __mod6(new str("sys.hash_info(width=%d, modulus=%d, inf=%d, nan=%d, imag=%d, algorithm=%s, hash_bits=%d, seed_bits=%d, cutoff=%d)"), 9,
        width, modulus, inf, nan, imag, repr(algorithm), hash_bits, seed_bits, cutoff);
}

} // module namespace

