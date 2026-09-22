/* Copyright 2005-2023 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "struct.hpp"
#include <stdio.h>
#include <string.h>

namespace __struct__ {

void *buffy;
class_ *cl_error;
bool little_endian;


unsigned int get_itemsize(char order, char c) {
    if(order == '@') {
        switch(c) {
            case 'b': return sizeof(signed char);
            case 'B': return sizeof(unsigned char);
            case 'h': return sizeof(short);
            case 'H': return sizeof(unsigned short);
            case 'i': return sizeof(int);
            case 'I': return sizeof(unsigned int);
            case 'l': return sizeof(long);
            case 'L': return sizeof(unsigned long);
            case 'q': return sizeof(long long);
            case 'Q': return sizeof(unsigned long long);
            case 'f': return sizeof(float);
            case 'd': return sizeof(double);
//            case 'n': return sizeof(ssize_t); MSVC?
            case 'N': return sizeof(size_t);
        }
    } else {
        switch(c) {
            case 'b': return 1;
            case 'B': return 1;
            case 'h': return 2;
            case 'H': return 2;
            case 'i': return 4;
            case 'I': return 4;
            case 'l': return 4;
            case 'L': return 4;
            case 'q': return 8;
            case 'Q': return 8;
            case 'f': return 4;
            case 'd': return 8;
        }
    }
    return 0;
}

__ss_int padding(char o, __ss_int pos, unsigned int itemsize) {
    unsigned int upos = (unsigned int)pos;

    if(sizeof(void *) == 4) {
#ifndef WIN32
        if(itemsize == 8)
            itemsize = 4;
#endif
    }
    if(o == '@' and upos % itemsize)
        return (__ss_int)(itemsize - (upos % itemsize));
    return 0;
}

__ss_int unpack_int(char o, char c, unsigned int d, bytes *data, __ss_int base, __ss_int *pos) {
    unsigned long long result;
    unsigned int itemsize = get_itemsize(o, c);
    *pos += padding(o, *pos-base, itemsize);
    if(d==0)
        return 0;
    result = 0;
    for(unsigned int i=0; i<itemsize; i++) {
        unsigned long long c2 = (unsigned char)(data->unit[(size_t)(*pos+(__ss_int)i)]);
        if(is_big_endian_order(o))
            result |= (c2 << 8*(itemsize-i-1));
        else
            result |= (c2 << 8*i);
    }
    *pos += (__ss_int)itemsize;

    /* sign-extend for signed format codes narrower than 8 bytes; without
       this, e.g. unpacking 'b' (signed char) returns a positive value for
       negative input, and 'i'/'l' break the same way whenever __ss_int is
       wider than the format's native itemsize (as with --int64). */
    switch(c) {
        case 'b':
        case 'h':
        case 'i':
        case 'l':
        case 'q':
            if(itemsize < 8 and (result & (1ULL << (8*itemsize - 1))))
                result |= (~0ULL << (8*itemsize));
            break;
        default:
            ;
    }

    return (__ss_int)result;
}

bytes *unpack_bytes(char, char c, unsigned int d, bytes *data, __ss_int, __ss_int *pos) {
    bytes *result = 0;
    unsigned int len;
    switch(c) {
        case 'c':
             result = new bytes(__GC_BYTES(1, (char)data->unit[(size_t)(*pos)]));
             break;
        case 's':
             result = new bytes();
             for(unsigned int i=0; i<d; i++)
                 result->unit += data->unit[(size_t)(*pos+(__ss_int)i)];
             break;
        case 'p':
             result = new bytes();
             if(d == 0) /* '0p' unpacks to b'' (as of CPython 3.15) */
                 len = 0;
             else {
                 len = (unsigned char)data->unit[(size_t)(*pos)];
                 if(len > d-1)
                     len = d-1;
             }
             for(unsigned i=0; i<len; i++)
                 result->unit += data->unit[(size_t)(*pos+(__ss_int)i+1)];
             break;
    }
    *pos += (__ss_int)d;
    result->frozen = 1;
    return result;
}

__ss_bool unpack_bool(char, char, unsigned int d, bytes *data, __ss_int, __ss_int *pos) {
    __ss_bool result;
    if(data->unit[(size_t)(*pos)] == '\x00')
        result = False;
    else
        result = True;
    if(d!=0)
        *pos += 1;
    return result;
}

double unpack_float(char o, char c, unsigned int d, bytes *data, __ss_int base, __ss_int *pos) {
    double result;
    unsigned int itemsize = get_itemsize(o, c);
    *pos += padding(o, *pos-base, itemsize);
    if(d==0)
        return 0;
    if(swap_endian(o))
        for(unsigned int i=0; i<itemsize; i++)
            ((char *)buffy)[itemsize-i-1] = data->unit[(size_t)(*pos+(__ss_int)i)];
    else
        for(unsigned int i=0; i<itemsize; i++)
            ((char *)buffy)[i] = data->unit[(size_t)(*pos+(__ss_int)i)];
    if(c == 'f')
        result = *((float *)(buffy));
    else
        result = *((double *)(buffy));
    *pos += (__ss_int)itemsize;
    return result;
}

void unpack_pad(char, char, unsigned int d, bytes *, __ss_int, __ss_int *pos) {
    *pos += (__ss_int)d;
}

template<class S> static __ss_int calcsize_impl(const S &fmt, size_t fmtlen) {
    __ss_int result = 0;
    char order = '@';
    unsigned int itemsize;
    __ss_int n = 0;
    __ss_int ndigits = -1;

    for(size_t i=0; i<fmtlen; i++) {
        __ss_char c = (__ss_char)fmt[i];
        switch(c) {
            case '@':
            case '=':
            case '<':
            case '>':
            case '!':
                /* a byte-order character is only meaningful as the very
                   first character of the format string, matching CPython;
                   elsewhere it's a bad char (this also stops 'N'/'n' from
                   silently picking up a stray non-native order further
                   along the string) */
                if(i != 0)
                    throw new error(new str("bad char in struct format"));
                order = (char)c;
                break;
            case '0':
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
            case '6':
            case '7':
            case '8':
            case '9':
                n = (__ss_int)(c - '0');
                if(ndigits == -1)
                    ndigits = n;
                else
                    ndigits = 10*ndigits+n;
                break;
            case 'b':
            case 'B':
            case 'h':
            case 'H':
            case 'i':
            case 'I':
            case 'l':
            case 'L':
            case 'q':
            case 'Q':
            case 'd':
            case 'f':
//            case 'n':
            case 'N':
                itemsize = get_itemsize(order, (char)c);
                if(itemsize == 0)
                    /* e.g. 'N' (size_t) is only valid with the native '@'
                       byte order, matching CPython */
                    throw new error(new str("bad char in struct format"));
                if(ndigits == -1)
                    ndigits = 1;
                result += ndigits * (__ss_int)itemsize;
                ndigits = -1;
                result += padding(order, result, itemsize);
                break;
            case 'c':
            case 's':
            case 'p':
            case '?':
            case 'x':
                if(ndigits == -1)
                    ndigits = 1;
                result += ndigits;
                ndigits = -1;
                break;
            case ' ':
            case '\t':
            case '\n':
            case '\r':
            case '\x0b':
            case '\x0c':
                break;
            case 'P':
                throw new error(new str("unsupported 'P' char in struct format"));
            default:
                throw new error(new str("bad char in struct format"));
        }
    }
    return result;
}

__ss_int calcsize(str *fmt) {
    return calcsize_impl(fmt->unit, (size_t)len(fmt));
}

__ss_int calcsize(const char *fmt) {
    return calcsize_impl(fmt, strlen(fmt));
}

/* buffer size checks for (inlined) unpack/unpack_from, same messages as CPython;
   return the (wrapped) start position */

__ss_int unpack_pos(const char *fmt, bytes *data) {
    __ss_int size = calcsize(fmt);
    __ss_int buflen = len(data);
    if(buflen != size)
        throw new error(__mod6(new str("unpack requires a buffer of %d bytes"), 1, size));
    return 0;
}

__ss_int unpack_from_pos(const char *fmt, bytes *data, __ss_int offset) {
    __ss_int size = calcsize(fmt);
    __ss_int buflen = len(data);
    if(offset < 0) {
        if(offset + buflen < 0)
            throw new error(__mod6(new str("offset %d out of range for %d-byte buffer"), 2, offset, buflen));
        offset += buflen;
    }
    if(buflen - offset < size)
        throw new error(__mod6(new str("unpack_from requires a buffer of at least %d bytes for unpacking %d bytes at offset %d (actual buffer size is %d)"), 4, size+offset, size, offset, buflen));
    return offset;
}

__ss_int calcitems(str *fmt) {
    __ss_int result = 0;
    __ss_int n = 0;
    __ss_int ndigits = -1;

    for(unsigned int i=0; i<(unsigned int)len(fmt); i++) {
        __ss_char c = fmt->unit[i];
        switch(c) {
            case '@':
            case '=':
            case '<':
            case '>':
            case '!':
                if(i != 0)
                    throw new error(new str("bad char in struct format"));
                break;
            case '0':
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
            case '6':
            case '7':
            case '8':
            case '9':
                n = (__ss_int)(c - '0');
                if(ndigits == -1)
                    ndigits = n;
                else
                    ndigits = 10*ndigits+n;
                break;
            case 'b':
            case 'B':
            case 'h':
            case 'H':
            case 'i':
            case 'I':
            case 'l':
            case 'L':
            case 'q':
            case 'Q':
            case 'd':
            case 'f':
//            case 'n':
            case 'N':
            case 'c':
            case '?':
                if(ndigits == -1)
                    ndigits = 1;
                result += ndigits;
                ndigits = -1;
                break;
            case 's':
            case 'p':
                result += 1;
                ndigits = -1;
                break;
            case ' ':
            case '\t':
            case '\n':
            case '\r':
            case '\x0b':
            case '\x0c':
                break;
            case 'x':
                ndigits = -1;
                break;
            case 'P':
                throw new error(new str("unsupported 'P' char in struct format"));
            default:
                throw new error(new str("bad char in struct format"));
        }
    }
    return result;
}

/* CPython's _struct range-checks every integer field before packing it;
   without this, out-of-range values are silently truncated to the format's
   width (e.g. struct.pack('<b', 200) -> b'\xc8' instead of an error, and
   struct.pack('<i', 2**40) -> four zero bytes: total data loss) */
static void check_int_range(char c, __ss_int t, unsigned int itemsize) {
    bool is_signed;
    bool ok;

    if(itemsize == 0) /* e.g. 'N' under a non-native order; reported elsewhere */
        return;

    switch(c) {
        case 'b':
        case 'h':
        case 'i':
        case 'l':
        case 'q':
            is_signed = true;
            break;
        default: /* 'B', 'H', 'I', 'L', 'Q', 'N' */
            is_signed = false;
    }

    if(is_signed) {
        /* a format at least as wide as __ss_int cannot overflow */
        if(itemsize >= sizeof(__ss_int))
            return;
        __ss_int hi = ((__ss_int)1 << (8*itemsize - 1)) - 1;
        ok = (t >= -hi - 1 and t <= hi);
    } else {
        /* an unsigned format at least as wide as __ss_int can't be checked:
           shedskin ints are signed, so a negative value is indistinguishable
           from the large unsigned one CPython would accept (struct.pack('<Q',
           2**64-1) arrives here as -1, and unpack('<Q') hands back -1 too) */
        if(itemsize >= sizeof(__ss_int))
            return;
        __ss_int hi = ((__ss_int)1 << (8*itemsize)) - 1;
        ok = (t >= 0 and t <= hi);
    }
    if(ok)
        return;

    /* CPython spells out the bounds for the codes narrower than 8 bytes and
       falls back to a generic message for the rest. 'I'/'L' are the odd ones
       out: a negative value fails in their PyLong_AsUnsignedLong conversion
       before the width check, so it gets the generic message too. */
    switch(c) {
        case 'b':
            throw new error(new str("byte format requires -128 <= number <= 127"));
        case 'B':
            throw new error(new str("ubyte format requires 0 <= number <= 255"));
        case 'h':
            throw new error(new str("short format requires -32768 <= number <= 32767"));
        case 'H':
            throw new error(new str("ushort format requires 0 <= number <= 65535"));
        case 'i':
            throw new error(new str("'i' format requires -2147483648 <= number <= 2147483647"));
        case 'l':
            throw new error(new str("'l' format requires -2147483648 <= number <= 2147483647"));
        case 'I':
            if(t >= 0)
                throw new error(new str("'I' format requires 0 <= number <= 4294967295"));
            break;
        case 'L':
            if(t >= 0)
                throw new error(new str("'L' format requires 0 <= number <= 4294967295"));
            break;
        default:
            ;
    }
    throw new error(new str("argument out of range"));
}

void fillbuf_int(char c, __ss_int t, char order, unsigned int itemsize) {
    check_int_range(c, t, itemsize);

    if(order == '@') {
        switch(c) {
            case 'b': *((signed char *)buffy) = (signed char)t; break;
            case 'B': *((unsigned char *)buffy) = (unsigned char)t; break;
            case 'h': *((short *)buffy) = (short)t; break;
            case 'H': *((unsigned short *)buffy) = (unsigned short)t; break;
            case 'i': *((int *)buffy) = (int)t; break;
            case 'I': *((unsigned int *)buffy) = (unsigned int)t; break;
            case 'l': *((long *)buffy) = (long)t; break;
            case 'L': *((unsigned long *)buffy) = (unsigned long)t; break;
            case 'q': *((long long *)buffy) = (long long)t; break;
            case 'Q': *((unsigned long long *)buffy) = (unsigned long long)t; break;
//            case 'n': *((ssize_t *)buffy) = t; break;
            case 'N': *((size_t *)buffy) = (size_t)t; break;
        }
    } else {
        if(is_big_endian_order(order)) {
            for(int i=(int)itemsize-1; i>=0; i--) {
                ((char *)buffy)[(size_t)i] = (char)(t & 0xff);
                t >>= 8;
            }
        } else {
            for(unsigned int i=0; i<itemsize; i++) {
                ((char *)buffy)[i] = (char)(t & 0xff);
                t >>= 8;
            }
        }
    }
}

void fillbuf_float(char c, __ss_float t, char, unsigned int) {
    switch(c) {
        case 'f': *((float *)buffy) = (float)t; break;
        case 'd': *((double *)buffy) = (double)t; break;
    }
}

void __init() {
    cl_error = new class_("error");
    int num = 1;
    little_endian = (*(char *)&num == 1);
    buffy = malloc(8);
}

} // module namespace

