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
__codec_result __utf8_decode(const char *src, size_t len, char32_t *dst) {
    size_t pos = 0;
    size_t units = 0;

    while (pos < len) {
        unsigned char b0 = (unsigned char)src[pos];
        size_t nfollow;
        unsigned char lo = 0x80, hi = 0xbf; /* allowed range for first continuation byte */
        char32_t cp;

        if (b0 < 0x80) {
            if (dst)
                dst[units] = (char32_t)b0;
            units++;
            pos++;
            continue;
        } else if (b0 < 0xc2) { /* continuation byte or overlong c0/c1 start */
            return __codec_err(units, pos, ERR_START);
        } else if (b0 < 0xe0) {
            nfollow = 1;
            cp = (char32_t)(b0 & 0x1fu);
        } else if (b0 < 0xf0) {
            nfollow = 2;
            cp = (char32_t)(b0 & 0x0fu);
            if (b0 == 0xe0)
                lo = 0xa0;
            else if (b0 == 0xed)
                hi = 0x9f;
        } else if (b0 < 0xf5) {
            nfollow = 3;
            cp = (char32_t)(b0 & 0x07u);
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
            cp = (cp << 6) | (char32_t)(b & 0x3fu);
        }

        if (dst)
            dst[units] = cp;
        units++;
        pos += nfollow + 1;
    }
    return __codec_ok(units);
}

__codec_result __utf8_encode(const char32_t *src, size_t len, char *dst) {
    size_t units = 0;

    for (size_t pos = 0; pos < len; pos++) {
        char32_t cp = src[pos];

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

__codec_result __ascii_decode(const char *src, size_t len, char32_t *dst) {
    for (size_t pos = 0; pos < len; pos++) {
        unsigned char b = (unsigned char)src[pos];
        if (b >= 0x80)
            return __codec_err(pos, pos, ERR_ASCII);
        if (dst)
            dst[pos] = (char32_t)b;
    }
    return __codec_ok(len);
}

__codec_result __ascii_encode(const char32_t *src, size_t len, char *dst) {
    for (size_t pos = 0; pos < len; pos++) {
        char32_t cp = src[pos];
        if (cp >= 0x80)
            return __codec_err(pos, pos, ERR_ASCII);
        if (dst)
            dst[pos] = (char)(unsigned char)cp;
    }
    return __codec_ok(len);
}

__codec_result __latin1_decode(const char *src, size_t len, char32_t *dst) {
    if (dst)
        for (size_t pos = 0; pos < len; pos++)
            dst[pos] = (char32_t)(unsigned char)src[pos];
    return __codec_ok(len);
}

__codec_result __latin1_encode(const char32_t *src, size_t len, char *dst) {
    for (size_t pos = 0; pos < len; pos++) {
        char32_t cp = src[pos];
        if (cp >= 0x100)
            return __codec_err(pos, pos, ERR_LATIN1);
        if (dst)
            dst[pos] = (char)(unsigned char)cp;
    }
    return __codec_ok(len);
}

#ifndef __SS_UNICODE_STANDALONE

size_t __utf8_decode_checked(const char *src, size_t len, char32_t *dst) {
    __codec_result r = __utf8_decode(src, len, dst);
    if (!r.ok) {
        char buf[128];
        if (r.errmsg == ERR_TRUNC) /* errpos = start of the incomplete sequence */
            snprintf(buf, sizeof(buf), "'utf-8' codec can't decode bytes in position %zu-%zu: %s", r.errpos, len - 1, r.errmsg);
        else
            snprintf(buf, sizeof(buf), "'utf-8' codec can't decode byte 0x%02x in position %zu: %s", (unsigned char)src[r.errpos], r.errpos, r.errmsg);
        throw new ValueError(new str(buf));
    }
    return r.units;
}

size_t __utf8_encode_checked(const char32_t *src, size_t len, char *dst) {
    __codec_result r = __utf8_encode(src, len, dst);
    if (!r.ok) {
        char buf[128];
        snprintf(buf, sizeof(buf), "'utf-8' codec can't encode character '\\U%08x' in position %zu: %s", (unsigned int)src[r.errpos], r.errpos, r.errmsg);
        throw new ValueError(new str(buf));
    }
    return r.units;
}

#endif

#ifdef __SS_UNICODE_STANDALONE
} // namespace __shedskin__
#endif
