/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifdef SS_DECL

class __ss_bool {
public:
    uint8_t value;
    inline __ss_int operator+(__ss_bool b);
    inline __ss_bool operator==(__ss_bool b);
    inline __ss_bool operator&(__ss_bool b);
    inline __ss_bool operator|(__ss_bool b);
    inline __ss_bool operator^(__ss_bool b);
    inline bool operator!();
    inline operator bool();
};

#else

#ifndef SS_BOOL_HPP
#define SS_BOOL_HPP

inline __ss_int __ss_bool::operator+(__ss_bool b) { return value+b.value; }
inline __ss_bool __ss_bool::operator==(__ss_bool b) { __ss_bool c; c.value=value==b.value; return c; }
inline __ss_bool __ss_bool::operator&(__ss_bool b) { __ss_bool c; c.value=value&b.value; return c; }
inline __ss_bool __ss_bool::operator|(__ss_bool b) { __ss_bool c; c.value=value|b.value; return c; }
inline __ss_bool __ss_bool::operator^(__ss_bool b) { __ss_bool c; c.value=value^b.value; return c; }
inline bool __ss_bool::operator!() { return !value; }
inline __ss_bool::operator bool() { return bool(value); }

inline __ss_bool ___bool() { return __mbool(false); }

template<class T> inline __ss_bool ___bool(T x) { return __mbool(x && x->__nonzero__()); }
template<> inline __ss_bool ___bool(str *s) { return __mbool(s && s->unit.size() > 0); }
template<> inline __ss_bool ___bool(int32_t x) { return __mbool(x!=0); }
template<> inline __ss_bool ___bool(int64_t x) { return __mbool(x!=0); }
#ifdef __SS_INT128
template<> inline __ss_bool ___bool(__int128 x) { return __mbool(x!=0); }
#endif
#ifdef __APPLE__
template<> inline __ss_bool ___bool(long x) { return __mbool(x!=0); }
#endif
template<> inline __ss_bool ___bool(bool x) { return __mbool(x); }
template<> inline __ss_bool ___bool(__ss_bool x) { return x; }
template<> inline __ss_bool ___bool(__ss_float x) { return __mbool(x!=0); }
template<> inline __ss_bool ___bool(void *) { return False; }

template<class T> inline __ss_bool ___bool(list<T> *x) { return __mbool(x && (x->units.size() != 0)); } /* XXX more general solution */

#endif
#endif
