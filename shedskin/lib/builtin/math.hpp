/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef SS_MATH_HPP
#define SS_MATH_HPP

#include "function.hpp"

/* pow */

inline __ss_float __power(__ss_int a, __ss_float b) { return pow(a,b); }
inline __ss_float __power(__ss_float a, __ss_int b) { 
    if(b==2) return a*a;
    else if(b==3) return a*a*a;
    else return pow(a,b); 
}

template<class A> A __power(A a, A b);
template<> inline __ss_float __power(__ss_float a, __ss_float b) { return pow(a,b); }

template<> inline __ss_int __power(__ss_int a, __ss_int b) {
    switch(b) {
        case 2: return a*a;
        case 3: return a*a*a;
        case 4: return a*a*a*a;
        case 5: return a*a*a*a*a;
        case 6: return a*a*a*a*a*a;
        case 7: return a*a*a*a*a*a*a;
        case 8: return a*a*a*a*a*a*a*a;
        case 9: return a*a*a*a*a*a*a*a*a;
        case 10: return a*a*a*a*a*a*a*a*a*a;
    }
    __ss_int res, tmp;

    res = 1;
    tmp = a;

    while((b>0)) {
        if ((b%2)) {
            res = (res*tmp);
        }
        tmp = (tmp*tmp);
        b = (b/2);
    }
    return res;
}

#ifdef __SS_LONG
inline __ss_int __power(__ss_int a, __ss_int b, __ss_int c) {
    __ss_int res, tmp;

    res = 1;
    tmp = a;

    while((b>0)) {
        if ((b%2)) {
            res = ((res*tmp)%c);
        }
        tmp = ((tmp*tmp)%c);
        b = (b/2);
    }
    return res;
}
#endif

inline int __power(int a, int b, int c) {
    long long res, tmp;

    res = 1;
    tmp = a;

    while((b>0)) {
        if ((b%2)) {
            res = ((res*tmp)%c);
        }
        tmp = ((tmp*tmp)%c);
        b = (b/2);
    }
    return (int)res;
}

/* division */

template<class A> A __divs(A a, A b);
template<> inline __ss_float __divs(__ss_float a, __ss_float b) { return a/b; }
#ifdef __SS_LONG
template<> inline __ss_int __divs(__ss_int a, __ss_int b) {
    if(a<0 && b>0) return (a-b+1)/b;
    else if(b<0 && a>0) return (a-b-1)/b;
    else return a/b;
}
#endif

template<class A, class B> __ss_float __divs(A a, B b);
template<> inline __ss_float __divs(__ss_int a, __ss_float b) { return (__ss_float)a/b; }
template<> inline __ss_float __divs(__ss_float a, __ss_int b) { return a/((__ss_float)b); }

inline __ss_float __divs(__ss_int a, __ss_int b) { return a/((__ss_float)b); }

template<class A> inline A __floordiv(A a, A b) { return a->__floordiv__(b); }
template<> inline __ss_float __floordiv(__ss_float a, __ss_float b) { return floor(a/b); }

#ifdef __SS_LONG /* XXX */
template<> inline __ss_int __floordiv(__ss_int a, __ss_int b) { return (__ss_int)floor((__ss_float)a/b); } /* XXX */
#endif
template<> inline int __floordiv(int a, int b) { return (int)floor((__ss_float)a/b); } /* XXX */

inline __ss_float __floordiv(__ss_int a, __ss_float b) { return floor((__ss_float)a/b); }
inline __ss_float __floordiv(__ss_float a, __ss_int b) { return floor(a/((__ss_float)b)); }

/* modulo */

template<class A> A __mods(A a, A b);
#ifdef __SS_LONG /* XXX */
template<> inline __ss_int __mods(__ss_int a, __ss_int b) {
    int m = a%b;
    if((m<0 && b>0)||(m>0 && b<0)) m+=b;
    return m;
}
#endif
template<> inline int __mods(int a, int b) {
    int m = a%b;
    if((m<0 && b>0)||(m>0 && b<0)) m+=b;
    return m;
}
template<> inline __ss_float __mods(__ss_float a, __ss_float b) {
    __ss_float f = fmod(a,b);
    if((f<0 && b>0)||(f>0 && b<0)) f+=b;
    return f;
}

template<class A, class B> __ss_float __mods(A a, B b);
#ifdef __SS_LONG
template<> inline __ss_float __mods(__ss_int a, __ss_float b) { return __mods((__ss_float)a, b); }
template<> inline __ss_float __mods(__ss_float a, __ss_int b) { return __mods(a, (__ss_float)b); }
#endif
template<> inline __ss_float __mods(int a, __ss_float b) { return __mods((__ss_float)a, b); }
template<> inline __ss_float __mods(__ss_float a, int b) { return __mods(a, (__ss_float)b); }

/* divmod */

template<class A> inline tuple2<A, A> *divmod(A a, A b) { return a->__divmod__(b); }
template<> inline tuple2<__ss_float, __ss_float> *divmod(__ss_float a, __ss_float b) {
    return new tuple2<__ss_float, __ss_float>(2, __floordiv(a,b), __mods(a,b));
}
#ifdef __SS_LONG
template<> inline tuple2<__ss_int, __ss_int> *divmod(__ss_int a, __ss_int b) {
    return new tuple2<__ss_int, __ss_int>(2, __floordiv(a,b), __mods(a,b));
}
#endif
template<> inline tuple2<int, int> *divmod(int a, int b) {
    return new tuple2<int, int>(2, __floordiv(a,b), __mods(a,b));
}

inline tuple2<__ss_float, __ss_float> *divmod(__ss_float a, __ss_int b) { return divmod(a, (__ss_float)b); }
inline tuple2<__ss_float, __ss_float> *divmod(__ss_int a, __ss_float b) { return divmod((__ss_float)a, b); }

/* add */

template<class T> inline T __add(T a, T b) { return a->__add__(b); }
#ifdef __SS_LONG
template<> inline __ss_int __add(__ss_int a, __ss_int b) { return a + b; }
#endif
template<> inline int __add(int a, int b) { return a + b; }
template<> inline __ss_float __add(__ss_float a, __ss_float b) { return a + b; }

/* reverse */

template<class U> U __add2(__ss_float a, U b) { return b->__add__(a); }
template<class U> U __sub2(__ss_float a, U b) { return b->__rsub__(a); }
template<class T> T __mul2(__ss_int n, T a) { return a->__mul__(n); }
template<class T> T __mul2(__ss_bool n, T a) { return a->__mul__(n.value); }
template<class T> T __mul2(__ss_float n, T a) { return a->__mul__(n); }
template<class T> T __div2(__ss_int n, T a) { return a->__rdiv__(n); }
template<class T> T __div2(__ss_float n, T a) { return a->__rdiv__(n); }

/* {int, float}.is_integer */

inline __ss_bool __ss_is_integer(__ss_int i) {
    return True;
}

inline __ss_bool __ss_is_integer(__ss_float d) {
    return __mbool((long long)d == d);
}

/* int.{bit_count, bit_length */

namespace __int___ {
    inline __ss_int bit_count(__ss_int i) {
#ifdef __SS_LONG
        return (__ss_int)std::bitset<std::numeric_limits<unsigned long long>::digits>((unsigned long long)i).count(); // TODO hard-coded types
#else
        return (__ss_int)std::bitset<std::numeric_limits<unsigned int>::digits>((unsigned int)i).count();
#endif
    }

    inline __ss_int bit_length(__ss_int i) {
        if(i == 0)
            return 0;
        return (__ss_int)(std::floor(std::log2(std::abs(i)))) + 1;
        //return (__ss_int)std::bit_width(i); // TODO available from C++20
    }

/*    inline tuple<__ss_int> *as_integer_ratio(__ss_int i) {
        return new tuple<__ss_int>(2, i, 1);
    } */

}

inline __ss_int __ss_bit_count(__ss_int i) {
    return __int___::bit_count(i);
}
inline __ss_int __ss_bit_length(__ss_int i) {
    return __int___::bit_length(i);
}

inline bytes *__ss_to_bytes(__ss_int n, __ss_int length=1, str *byteorder=0, __ss_bool __ss_signed=False) {
    __ss_int inc = 0;
    __ss_int start_index = 0;
    __ss_int end_index = 0;
    __ss_int extension = 0;
    __ss_int actual_size = 0;
    unsigned char sign_ext = 0xff;
    unsigned char zero_ext = 0x00;
    unsigned char sign_bit = 0x80;

    bytes *b = new bytes();
    b->unit.resize(length);

    /* endianness */
    if(!byteorder || __eq(byteorder, byteorder_big)) {
        start_index = length-1;
        end_index = 0;
        inc = -1;
    } else {
        start_index = 0;
        end_index = length-1;
        inc = 1;
    }

    /* check sign bit */
    if(__ss_signed)
        __ss_signed = __mbool(n < 0);

    /* count extending 0x00/0xff bytes */
    for(__ss_int i=sizeof(__ss_int)-1; i>0; i--) {
        if((__ss_signed && (((n >> (8*i)) & sign_ext) == sign_ext)) ||
           (!__ss_signed && (((n >> (8*i)) & sign_ext) == zero_ext)))
            extension += 1;
        else
            break;
    }

    /* check overflow */
    actual_size = sizeof(__ss_int) - extension;
    if(__ss_signed && !(n & (sign_bit << (8*(actual_size-1))))) /* sign bit fell off the bus */
        actual_size += 1;
    if(actual_size > length)
        throw new OverflowError(new str("int too big to convert"));

    /* copy non-extending bytes */
    __ss_int i = start_index;
    for(__ss_int j = 0; j < actual_size; j++) {
        b->unit[i] = (unsigned char)((n >> (8*j)) & sign_ext);
        i += inc;
    }

    /* extend sign bit */
    if(__ss_signed) {
        for(__ss_int j = 0; j < length-actual_size; j++) {
            b->unit[i] = sign_ext;
            i += inc;
        }
    }

    return b;
}

inline str *__ss_hex(__ss_float f) {
    char buf[64];
    std::sprintf(buf, "%a", f);
    return new str(buf);
}

namespace __int___ {
    inline __ss_int from_bytes(bytes *b, str* byteorder=0, __ss_bool __ss_signed=False) {
        __ss_int blen = len(b);
        __ss_int inc = 0;
        __ss_int start_index = 0;
        __ss_int end_index = 0;
        __ss_int extension = 0;
        __ss_int actual_size = 0;
        unsigned char sign_ext = 0xff;
        unsigned char zero_ext = 0x00;
        unsigned char sign_bit = 0x80;

        if(!blen)
            return 0;

        /* endianness */
        if(!byteorder || __eq(byteorder, byteorder_big)) {
            start_index = blen-1;
            end_index = 0;
            inc = -1;
        } else {
            start_index = 0;
            end_index = blen-1;
            inc = 1;
        }

        /* check sign bit */
        if(__ss_signed)
            __ss_signed = __mbool((b->unit[end_index] & 0x80) == 0x80);

        /* count extending 0x00/0xff bytes */
        for(__ss_int i=end_index; ; i-= inc) {
            if((__ss_signed && ((unsigned char)(b->unit[i])) == sign_ext) ||
               (!__ss_signed && ((unsigned char)(b->unit[i])) == zero_ext))
                extension += 1;
            else
                break;
            if(i == start_index)
                break;
        }

        /* check overflow */
        actual_size = blen - extension;
        if(__ss_signed && !(b->unit[start_index + (actual_size-1) * inc] & sign_bit)) /* sign bit fell off the bus */
            actual_size += 1;

        if(actual_size > sizeof(__ss_int))
            throw new OverflowError(new str("int too big to convert"));

        /* copy non-extending bytes */
        __ss_int n = 0;
        __ss_int i = start_index;
        for(__ss_int j = 0; j < actual_size; j++) {
            n |= ((unsigned char)(b->unit[i])) << (8*j);
            i += inc;
        }

        /* extend sign bit */
        if(__ss_signed) {
            for(__ss_int j = actual_size; j < sizeof(__ss_int); j++) {
                n |= sign_ext << (8*j);
            }
        }

        return n;
    }

    inline __ss_int from_bytes(pyiter<__ss_int> *p, str* byteorder=0, __ss_bool __ss_signed=False) {
        return from_bytes(__bytes(p), byteorder, __ss_signed);
    }

}

namespace __bytes___ {
    static signed char table_a2b_hex[] = { // TODO merge with binascii.. or use C++ function?
        -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
        -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
        -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
         0, 1, 2, 3,  4, 5, 6, 7,  8, 9,-1,-1, -1,-1,-1,-1,
        -1,10,11,12, 13,14,15,-1, -1,-1,-1,-1, -1,-1,-1,-1,
        -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
        -1,10,11,12, 13,14,15,-1, -1,-1,-1,-1, -1,-1,-1,-1,
        -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
        -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
        -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,

        -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
        -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
        -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
        -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
        -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
        -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
    };

    inline bytes *fromhex(void *, str *s) { // merge with binascii.unhexlify? which does not ignore whitespace
        __GC_STRING separator = " \n\r\t";
        bytes *result = new bytes();
        size_t count = 0;
        unsigned char high, low;
        size_t i=0;
        for(; i < s->unit.size(); i++) {
            char c = s->unit[i];
            if(separator.find_first_of(c) != std::string::npos) {
                if(count == 1)
                    throw new ValueError(__add(new str("non-hexadecimal number found in fromhex() arg at position "), __str(i)));
            }
            else {
                if(count == 0) {
                    high = table_a2b_hex[(unsigned char)c];
                    count += 1;
                } else {
                    result->unit += (char)((high << 4) | table_a2b_hex[(unsigned char)c]);
                    count = 0;
                }
            }
        }
        if(count == 1) // TODO bug in cpython?
            throw new ValueError(__add(new str("non-hexadecimal number found in fromhex() arg at position "), __str(i)));
        return result;
    }
}

namespace __bytearray__ {
    inline bytes *fromhex(void *, str *s) {
        bytes *b = __bytes___::fromhex(NULL, s);
        b->frozen = 0;
        return b;
    }
}

namespace __float___ {
    template<class T> __ss_float from_number(void *, T t) {
        return __float(t);
    }

    inline __ss_float fromhex(void *, str *s) {
        const char *start = s->unit.c_str();
        char *end;
        double f = std::strtod(start, &end);
        if(start == end)
            throw new ValueError(new str("invalid hexadecimal floating-point string"));
        return f;
    }
}

#endif
