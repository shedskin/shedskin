/* Copyright 2005-2026 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE) */

/* strict utf-8/ascii/latin-1 codecs, see unicode.hpp.

   when included from builtin.cpp this file may use the full runtime
   (exceptions, str); the core functions below use nothing outside
   <cstddef>/<cstdio> so they also build standalone for unit testing
   (with -D__SS_UNICODE_STANDALONE, see tests/cpp/test_unicode.cpp). */

#ifdef __SS_UNICODE_STANDALONE
#include "unicode.hpp"
#include <cstdio>
namespace __shedskin__ {
#endif

static const char *ERR_START = "invalid start byte";
static const char *ERR_CONT = "invalid continuation byte";
static const char *ERR_TRUNC = "unexpected end of data";
static const char *ERR_SURROGATE = "surrogates not allowed";
static const char *ERR_RANGE = "code point out of range";
static const char *ERR_ASCII = "ordinal not in range(128)";
static const char *ERR_LATIN1 = "ordinal not in range(256)";

static inline __codec_result __codec_ok(size_t units) {
    __codec_result r;
    r.ok = true;
    r.units = units;
    r.errpos = 0;
    r.errmsg = 0;
    return r;
}

static inline __codec_result __codec_err(size_t units, size_t errpos, const char *errmsg) {
    __codec_result r;
    r.ok = false;
    r.units = units;
    r.errpos = errpos;
    r.errmsg = errmsg;
    return r;
}

/* strict utf-8 decoder. valid sequences (inclusive byte ranges):

     00..7f
     c2..df  80..bf
     e0      a0..bf  80..bf     (a0 lower bound rejects overlong)
     e1..ec  80..bf  80..bf
     ed      80..9f  80..bf     (9f upper bound rejects surrogates)
     ee..ef  80..bf  80..bf
     f0      90..bf  80..bf  80..bf   (90 lower bound rejects overlong)
     f1..f3  80..bf  80..bf  80..bf
     f4      80..8f  80..bf  80..bf   (8f upper bound rejects > U+10FFFF)

   errpos is the index of the offending byte (the start byte itself for
   an invalid start byte, the first bad continuation byte otherwise),
   except for truncated input, where it is the index of the sequence's
   start byte, matching the position range CPython reports. */
__codec_result __utf8_decode(const char *src, size_t len, __ss_char *dst) {
    size_t pos = 0;
    size_t units = 0;

    while (pos < len) {
        unsigned char b0 = (unsigned char)src[pos];
        size_t nfollow;
        unsigned char lo = 0x80, hi = 0xbf; /* allowed range for first continuation byte */
        __ss_char cp;

        if (b0 < 0x80) {
            if (dst)
                dst[units] = (__ss_char)b0;
            units++;
            pos++;
            continue;
        } else if (b0 < 0xc2) { /* continuation byte or overlong c0/c1 start */
            return __codec_err(units, pos, ERR_START);
        } else if (b0 < 0xe0) {
            nfollow = 1;
            cp = (__ss_char)(b0 & 0x1fu);
        } else if (b0 < 0xf0) {
            nfollow = 2;
            cp = (__ss_char)(b0 & 0x0fu);
            if (b0 == 0xe0)
                lo = 0xa0;
            else if (b0 == 0xed)
                hi = 0x9f;
        } else if (b0 < 0xf5) {
            nfollow = 3;
            cp = (__ss_char)(b0 & 0x07u);
            if (b0 == 0xf0)
                lo = 0x90;
            else if (b0 == 0xf4)
                hi = 0x8f;
        } else {
            return __codec_err(units, pos, ERR_START);
        }

        for (size_t k = 1; k <= nfollow; k++) {
            if (pos + k == len) /* truncated: errpos = start of the incomplete sequence */
                return __codec_err(units, pos, ERR_TRUNC);
            unsigned char b = (unsigned char)src[pos + k];
            if (b < lo || b > hi)
                return __codec_err(units, pos + k, ERR_CONT);
            lo = 0x80;
            hi = 0xbf;
            cp = (cp << 6) | (__ss_char)(b & 0x3fu);
        }

        if (dst)
            dst[units] = cp;
        units++;
        pos += nfollow + 1;
    }
    return __codec_ok(units);
}

size_t __utf8_decode_one(const char *src, size_t len, size_t pos, __ss_char *cp) {
    /* same validity rules as __utf8_decode above */
    if (pos >= len)
        return 0;
    unsigned char b0 = (unsigned char)src[pos];
    if (b0 < 0x80) {
        *cp = (__ss_char)b0;
        return 1;
    }
    size_t nfollow;
    unsigned char lo = 0x80, hi = 0xbf;
    __ss_char out;
    if (b0 < 0xc2) {
        return 0;
    } else if (b0 < 0xe0) {
        nfollow = 1;
        out = (__ss_char)(b0 & 0x1fu);
    } else if (b0 < 0xf0) {
        nfollow = 2;
        out = (__ss_char)(b0 & 0x0fu);
        if (b0 == 0xe0)
            lo = 0xa0;
        else if (b0 == 0xed)
            hi = 0x9f;
    } else if (b0 < 0xf5) {
        nfollow = 3;
        out = (__ss_char)(b0 & 0x07u);
        if (b0 == 0xf0)
            lo = 0x90;
        else if (b0 == 0xf4)
            hi = 0x8f;
    } else {
        return 0;
    }
    if (pos + nfollow >= len)
        return 0;
    for (size_t k = 1; k <= nfollow; k++) {
        unsigned char b = (unsigned char)src[pos + k];
        if (b < lo || b > hi)
            return 0;
        lo = 0x80;
        hi = 0xbf;
        out = (out << 6) | (__ss_char)(b & 0x3fu);
    }
    *cp = out;
    return nfollow + 1;
}

__codec_result __utf8_encode(const __ss_char *src, size_t len, char *dst) {
    size_t units = 0;

    for (size_t pos = 0; pos < len; pos++) {
        __ss_char cp = src[pos];

        if (cp < 0x80) {
            if (dst)
                dst[units] = (char)(unsigned char)cp;
            units += 1;
        } else if (cp < 0x800) {
            if (dst) {
                dst[units] = (char)(unsigned char)(0xc0u | (cp >> 6));
                dst[units + 1] = (char)(unsigned char)(0x80u | (cp & 0x3fu));
            }
            units += 2;
        } else if (cp < 0x10000) {
            if (cp >= 0xd800 && cp <= 0xdfff)
                return __codec_err(units, pos, ERR_SURROGATE);
            if (dst) {
                dst[units] = (char)(unsigned char)(0xe0u | (cp >> 12));
                dst[units + 1] = (char)(unsigned char)(0x80u | ((cp >> 6) & 0x3fu));
                dst[units + 2] = (char)(unsigned char)(0x80u | (cp & 0x3fu));
            }
            units += 3;
        } else if (cp <= __MAX_CODEPOINT) {
            if (dst) {
                dst[units] = (char)(unsigned char)(0xf0u | (cp >> 18));
                dst[units + 1] = (char)(unsigned char)(0x80u | ((cp >> 12) & 0x3fu));
                dst[units + 2] = (char)(unsigned char)(0x80u | ((cp >> 6) & 0x3fu));
                dst[units + 3] = (char)(unsigned char)(0x80u | (cp & 0x3fu));
            }
            units += 4;
        } else {
            return __codec_err(units, pos, ERR_RANGE);
        }
    }
    return __codec_ok(units);
}

__codec_result __ascii_decode(const char *src, size_t len, __ss_char *dst) {
    for (size_t pos = 0; pos < len; pos++) {
        unsigned char b = (unsigned char)src[pos];
        if (b >= 0x80)
            return __codec_err(pos, pos, ERR_ASCII);
        if (dst)
            dst[pos] = (__ss_char)b;
    }
    return __codec_ok(len);
}

__codec_result __ascii_encode(const __ss_char *src, size_t len, char *dst) {
    for (size_t pos = 0; pos < len; pos++) {
        __ss_char cp = src[pos];
        if (cp >= 0x80)
            return __codec_err(pos, pos, ERR_ASCII);
        if (dst)
            dst[pos] = (char)(unsigned char)cp;
    }
    return __codec_ok(len);
}

__codec_result __latin1_decode(const char *src, size_t len, __ss_char *dst) {
    if (dst)
        for (size_t pos = 0; pos < len; pos++)
            dst[pos] = (__ss_char)(unsigned char)src[pos];
    return __codec_ok(len);
}

__codec_result __latin1_encode(const __ss_char *src, size_t len, char *dst) {
    for (size_t pos = 0; pos < len; pos++) {
        __ss_char cp = src[pos];
        if (cp >= 0x100)
            return __codec_err(pos, pos, ERR_LATIN1);
        if (dst)
            dst[pos] = (char)(unsigned char)cp;
    }
    return __codec_ok(len);
}

#ifndef __SS_UNICODE_STANDALONE

void __throw_decode_error(const char *codec, unsigned char b, size_t pos, const char *msg) {
    char buf[128];
    snprintf(buf, sizeof(buf), "'%s' codec can't decode byte 0x%02x in position %zu: %s", codec, b, pos, msg);
    throw new ValueError(new str(buf));
}

void __throw_encode_error(const char *codec, __ss_char cp, size_t pos, const char *msg) {
    char crepr[16];
    char buf[128];
    if (cp < 0x100) /* character repr as CPython formats it */
        snprintf(crepr, sizeof(crepr), "\\x%02x", (unsigned int)cp);
    else if (cp < 0x10000)
        snprintf(crepr, sizeof(crepr), "\\u%04x", (unsigned int)cp);
    else
        snprintf(crepr, sizeof(crepr), "\\U%08x", (unsigned int)cp);
    snprintf(buf, sizeof(buf), "'%s' codec can't encode character '%s' in position %zu: %s", codec, crepr, pos, msg);
    throw new ValueError(new str(buf));
}

size_t __utf8_decode_checked(const char *src, size_t len, __ss_char *dst) {
    __codec_result r = __utf8_decode(src, len, dst);
    if (!r.ok) {
        if (r.errmsg == ERR_TRUNC) { /* errpos = start of the incomplete sequence */
            char buf[128];
            snprintf(buf, sizeof(buf), "'utf-8' codec can't decode bytes in position %zu-%zu: %s", r.errpos, len - 1, r.errmsg);
            throw new ValueError(new str(buf));
        }
        __throw_decode_error("utf-8", (unsigned char)src[r.errpos], r.errpos, r.errmsg);
    }
    return r.units;
}

size_t __utf8_encode_checked(const __ss_char *src, size_t len, char *dst) {
    __codec_result r = __utf8_encode(src, len, dst);
    if (!r.ok)
        __throw_encode_error("utf-8", src[r.errpos], r.errpos, r.errmsg);
    return r.units;
}

__ss_encoding __lookup_encoding(str *encoding) {
    if (!encoding)
        return __SS_ENC_UTF8;
    __GC_BYTES norm;
    for (__ss_char ch : encoding->unit) {
        if (ch >= 'A' && ch <= 'Z')
            ch = ch + ('a' - 'A');
        if (ch == '_' || ch == ' ')
            ch = '-';
        if (ch > 127) { /* no non-ascii encoding names */
            norm += '?';
            continue;
        }
        norm += (char)(unsigned char)ch;
    }
    if (norm == "utf-8" || norm == "utf8" || norm == "utf" || norm == "u8" || norm == "cp65001")
        return __SS_ENC_UTF8;
    if (norm == "ascii" || norm == "us-ascii" || norm == "646")
        return __SS_ENC_ASCII;
    if (norm == "latin-1" || norm == "latin1" || norm == "latin" || norm == "l1" ||
        norm == "iso-8859-1" || norm == "iso8859-1" || norm == "8859" || norm == "cp819")
        return __SS_ENC_LATIN1;
    char buf[128];
    snprintf(buf, sizeof(buf), "unknown encoding: %s", __to_utf8(encoding->unit).c_str());
    throw new LookupError(new str(buf));
}

void __check_errors_arg(str *errors) {
    if (!errors || errors->unit == U"strict")
        return;
    char buf[128];
    snprintf(buf, sizeof(buf), "error handler '%s' is not supported by shedskin (only 'strict')", __to_utf8(errors->unit).c_str());
    throw new ValueError(new str(buf));
}

__GC_STR __from_utf8(const char *s, size_t len) {
    __GC_STR out;
    out.reserve(len);
    size_t pos = 0;
    while (pos < len) {
        __ss_char cp;
        size_t n = __utf8_decode_one(s, len, pos, &cp);
        if (n == 0) { /* lenient: invalid byte becomes one code point */
            cp = (__ss_char)(unsigned char)s[pos];
            n = 1;
        }
        out += cp;
        pos += n;
    }
    return out;
}

__GC_STR __from_utf8(const __GC_BYTES &b) {
    return __from_utf8(b.data(), b.size());
}

__GC_BYTES __to_utf8(const __ss_char *s, size_t len) {
    __GC_BYTES out;
    out.reserve(len);
    for (size_t pos = 0; pos < len; pos++) {
        __ss_char cp = s[pos];
        if (cp > __MAX_CODEPOINT) /* cannot normally happen */
            cp = 0xfffd;
        if (cp < 0x80)
            out += (char)(unsigned char)cp;
        else if (cp < 0x800) {
            out += (char)(unsigned char)(0xc0u | (cp >> 6));
            out += (char)(unsigned char)(0x80u | (cp & 0x3fu));
        } else if (cp < 0x10000) { /* note: surrogates pass through (wtf-8) */
            out += (char)(unsigned char)(0xe0u | (cp >> 12));
            out += (char)(unsigned char)(0x80u | ((cp >> 6) & 0x3fu));
            out += (char)(unsigned char)(0x80u | (cp & 0x3fu));
        } else {
            out += (char)(unsigned char)(0xf0u | (cp >> 18));
            out += (char)(unsigned char)(0x80u | ((cp >> 12) & 0x3fu));
            out += (char)(unsigned char)(0x80u | ((cp >> 6) & 0x3fu));
            out += (char)(unsigned char)(0x80u | (cp & 0x3fu));
        }
    }
    return out;
}

__GC_BYTES __to_utf8(const __GC_STR &u) {
    return __to_utf8(u.data(), u.size());
}

__GC_STR __gcs(const char *s) {
    __GC_STR out;
    while (*s)
        out += (__ss_char)(unsigned char)*s++;
    return out;
}

__GC_STR __gcs(const std::string &s) {
    __GC_STR out;
    out.reserve(s.size());
    for (char c : s)
        out += (__ss_char)(unsigned char)c;
    return out;
}

__GC_STR __widen(const __GC_BYTES &b) {
    __GC_STR out;
    out.reserve(b.size());
    for (char c : b)
        out += (__ss_char)(unsigned char)c;
    return out;
}

__GC_BYTES __narrow(const __GC_STR &u) {
    __GC_BYTES out;
    out.reserve(u.size());
    for (__ss_char cp : u)
        out += (cp < 0x100) ? (char)(unsigned char)cp : '?';
    return out;
}

std::string __narrow_std(const __GC_STR &u) {
    std::string out;
    out.reserve(u.size());
    for (__ss_char cp : u)
        out += (cp < 0x100) ? (char)(unsigned char)cp : '?';
    return out;
}

str *__char_str(__ss_char cp) {
    if (cp < 256)
        return __char_cache[cp];
    return new str(__GC_STR(1, cp));
}

#endif /* !__SS_UNICODE_STANDALONE */

#ifdef __SS_UNICODE_STANDALONE
} // namespace __shedskin__
#endif
