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

/* classify a utf-8 start byte b0 >= 0x80: the number of continuation bytes,
   the payload bits of b0, and the allowed range for the *first* continuation
   byte (see the table below). false for an invalid start byte. shared by
   __utf8_decode, __utf8_decode_one and __utf8_maximal_subpart. */
static inline bool __utf8_lead(unsigned char b0, size_t *nfollow, __ss_char *bits,
                               unsigned char *lo, unsigned char *hi) {
    *lo = 0x80;
    *hi = 0xbf;
    if (b0 < 0xc2) /* continuation byte or overlong c0/c1 start */
        return false;
    if (b0 < 0xe0) {
        *nfollow = 1;
        *bits = (__ss_char)(b0 & 0x1fu);
    } else if (b0 < 0xf0) {
        *nfollow = 2;
        *bits = (__ss_char)(b0 & 0x0fu);
        if (b0 == 0xe0)
            *lo = 0xa0;
        else if (b0 == 0xed)
            *hi = 0x9f;
    } else if (b0 < 0xf5) {
        *nfollow = 3;
        *bits = (__ss_char)(b0 & 0x07u);
        if (b0 == 0xf0)
            *lo = 0x90;
        else if (b0 == 0xf4)
            *hi = 0x8f;
    } else
        return false;
    return true;
}

/* write the utf-8 encoding of cp (no checks) to dst, returning its length.
   shared by __utf8_encode, __utf8_append and __to_utf8. */
static inline size_t __utf8_put(char *dst, __ss_char cp) {
    if (cp < 0x80) {
        dst[0] = (char)(unsigned char)cp;
        return 1;
    } else if (cp < 0x800) {
        dst[0] = (char)(unsigned char)(0xc0u | (cp >> 6));
        dst[1] = (char)(unsigned char)(0x80u | (cp & 0x3fu));
        return 2;
    } else if (cp < 0x10000) {
        dst[0] = (char)(unsigned char)(0xe0u | (cp >> 12));
        dst[1] = (char)(unsigned char)(0x80u | ((cp >> 6) & 0x3fu));
        dst[2] = (char)(unsigned char)(0x80u | (cp & 0x3fu));
        return 3;
    }
    dst[0] = (char)(unsigned char)(0xf0u | (cp >> 18));
    dst[1] = (char)(unsigned char)(0x80u | ((cp >> 12) & 0x3fu));
    dst[2] = (char)(unsigned char)(0x80u | ((cp >> 6) & 0x3fu));
    dst[3] = (char)(unsigned char)(0x80u | (cp & 0x3fu));
    return 4;
}

static inline size_t __utf8_len(__ss_char cp) {
    return cp < 0x80 ? 1 : cp < 0x800 ? 2 : cp < 0x10000 ? 3 : 4;
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
        unsigned char lo, hi; /* allowed range for first continuation byte */
        __ss_char cp;

        if (b0 < 0x80) {
            if (dst)
                dst[units] = (__ss_char)b0;
            units++;
            pos++;
            continue;
        }
        if (!__utf8_lead(b0, &nfollow, &cp, &lo, &hi))
            return __codec_err(units, pos, ERR_START);

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
    unsigned char lo, hi;
    __ss_char out;
    if (!__utf8_lead(b0, &nfollow, &out, &lo, &hi))
        return 0;
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
        if (cp > __MAX_CODEPOINT)
            return __codec_err(units, pos, ERR_RANGE);
        if (cp >= 0xd800 && cp <= 0xdfff)
            return __codec_err(units, pos, ERR_SURROGATE);
        units += dst ? __utf8_put(dst + units, cp) : __utf8_len(cp);
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

/* non-printable code points >= 0x80: general category Cc, Cf, Cs, Co,
   Zl, Zp or Zs, as sorted non-overlapping ranges (unicode 15.0.0). see
   __ss_char_printable in unicode.hpp for what is deliberately not here. */
static const struct { __ss_char lo, hi; } __nonprintable[] = {
    {0x00000, 0x0001F},  /* Cc */
    {0x0007F, 0x000A0},  /* Cc/Zs */
    {0x000AD, 0x000AD},  /* Cf */
    {0x00600, 0x00605},  /* Cf */
    {0x0061C, 0x0061C},  /* Cf */
    {0x006DD, 0x006DD},  /* Cf */
    {0x0070F, 0x0070F},  /* Cf */
    {0x00890, 0x00891},  /* Cf */
    {0x008E2, 0x008E2},  /* Cf */
    {0x01680, 0x01680},  /* Zs */
    {0x0180E, 0x0180E},  /* Cf */
    {0x02000, 0x0200F},  /* Zs/Cf */
    {0x02028, 0x0202F},  /* Zl/Zp/Cf/Zs */
    {0x0205F, 0x02064},  /* Zs/Cf */
    {0x02066, 0x0206F},  /* Cf */
    {0x03000, 0x03000},  /* Zs */
    {0x0D800, 0x0F8FF},  /* Cs/Co */
    {0x0FEFF, 0x0FEFF},  /* Cf */
    {0x0FFF9, 0x0FFFB},  /* Cf */
    {0x110BD, 0x110BD},  /* Cf */
    {0x110CD, 0x110CD},  /* Cf */
    {0x13430, 0x1343F},  /* Cf */
    {0x1BCA0, 0x1BCA3},  /* Cf */
    {0x1D173, 0x1D17A},  /* Cf */
    {0xE0001, 0xE0001},  /* Cf */
    {0xE0020, 0xE007F},  /* Cf */
    {0xF0000, 0xFFFFD},  /* Co */
    {0x100000, 0x10FFFD},  /* Co */
};

bool __ss_char_printable_nonascii(__ss_char c) {
    size_t lo = 0, hi = sizeof(__nonprintable) / sizeof(__nonprintable[0]);

    while (lo < hi) { /* at most 5 steps for 28 ranges */
        size_t mid = lo + (hi - lo) / 2;
        if (c < __nonprintable[mid].lo)
            hi = mid;
        else if (c > __nonprintable[mid].hi)
            lo = mid + 1;
        else
            return false;
    }

    return true;
}

#ifndef __SS_UNICODE_STANDALONE

#include "unicode_db.cpp"

__GC_STRING __ss_ascii_numeric(str *s) {
    size_t len = s->unit.size();
    __GC_STRING r;
    r.reserve(len);
    for (size_t i = 0; i < len; i++) {
        __ss_char c = s->unit[i];
        if (c == 0)
            r += '?';
        else if (c < 0x80)
            r += (char)c;
        else if (__ss_char_space(c))
            r += ' ';
        else {
            int d = __ss_char_rec(c)->decimal;
            r += (d >= 0) ? (char)('0' + d) : '?';
        }
    }
    return r;
}

void __throw_decode_error(const char *codec, bytes *b, size_t start, size_t end, const char *msg) {
    throw new UnicodeDecodeError(new str(codec), b, (__ss_int)start, (__ss_int)end, new str(msg));
}

/* single-byte windows code pages: code points for bytes 0x80-0xff (0:
   undefined, as in CPython), generated from CPython's own codecs */
static const unsigned short __cp1250_hi[128] = {
    0x20ac, 0, 0x201a, 0, 0x201e, 0x2026, 0x2020, 0x2021, 0, 0x2030, 0x0160, 0x2039, 0x015a, 0x0164, 0x017d, 0x0179,
    0, 0x2018, 0x2019, 0x201c, 0x201d, 0x2022, 0x2013, 0x2014, 0, 0x2122, 0x0161, 0x203a, 0x015b, 0x0165, 0x017e, 0x017a,
    0x00a0, 0x02c7, 0x02d8, 0x0141, 0x00a4, 0x0104, 0x00a6, 0x00a7, 0x00a8, 0x00a9, 0x015e, 0x00ab, 0x00ac, 0x00ad, 0x00ae, 0x017b,
    0x00b0, 0x00b1, 0x02db, 0x0142, 0x00b4, 0x00b5, 0x00b6, 0x00b7, 0x00b8, 0x0105, 0x015f, 0x00bb, 0x013d, 0x02dd, 0x013e, 0x017c,
    0x0154, 0x00c1, 0x00c2, 0x0102, 0x00c4, 0x0139, 0x0106, 0x00c7, 0x010c, 0x00c9, 0x0118, 0x00cb, 0x011a, 0x00cd, 0x00ce, 0x010e,
    0x0110, 0x0143, 0x0147, 0x00d3, 0x00d4, 0x0150, 0x00d6, 0x00d7, 0x0158, 0x016e, 0x00da, 0x0170, 0x00dc, 0x00dd, 0x0162, 0x00df,
    0x0155, 0x00e1, 0x00e2, 0x0103, 0x00e4, 0x013a, 0x0107, 0x00e7, 0x010d, 0x00e9, 0x0119, 0x00eb, 0x011b, 0x00ed, 0x00ee, 0x010f,
    0x0111, 0x0144, 0x0148, 0x00f3, 0x00f4, 0x0151, 0x00f6, 0x00f7, 0x0159, 0x016f, 0x00fa, 0x0171, 0x00fc, 0x00fd, 0x0163, 0x02d9,
};
static const unsigned short __cp1251_hi[128] = {
    0x0402, 0x0403, 0x201a, 0x0453, 0x201e, 0x2026, 0x2020, 0x2021, 0x20ac, 0x2030, 0x0409, 0x2039, 0x040a, 0x040c, 0x040b, 0x040f,
    0x0452, 0x2018, 0x2019, 0x201c, 0x201d, 0x2022, 0x2013, 0x2014, 0, 0x2122, 0x0459, 0x203a, 0x045a, 0x045c, 0x045b, 0x045f,
    0x00a0, 0x040e, 0x045e, 0x0408, 0x00a4, 0x0490, 0x00a6, 0x00a7, 0x0401, 0x00a9, 0x0404, 0x00ab, 0x00ac, 0x00ad, 0x00ae, 0x0407,
    0x00b0, 0x00b1, 0x0406, 0x0456, 0x0491, 0x00b5, 0x00b6, 0x00b7, 0x0451, 0x2116, 0x0454, 0x00bb, 0x0458, 0x0405, 0x0455, 0x0457,
    0x0410, 0x0411, 0x0412, 0x0413, 0x0414, 0x0415, 0x0416, 0x0417, 0x0418, 0x0419, 0x041a, 0x041b, 0x041c, 0x041d, 0x041e, 0x041f,
    0x0420, 0x0421, 0x0422, 0x0423, 0x0424, 0x0425, 0x0426, 0x0427, 0x0428, 0x0429, 0x042a, 0x042b, 0x042c, 0x042d, 0x042e, 0x042f,
    0x0430, 0x0431, 0x0432, 0x0433, 0x0434, 0x0435, 0x0436, 0x0437, 0x0438, 0x0439, 0x043a, 0x043b, 0x043c, 0x043d, 0x043e, 0x043f,
    0x0440, 0x0441, 0x0442, 0x0443, 0x0444, 0x0445, 0x0446, 0x0447, 0x0448, 0x0449, 0x044a, 0x044b, 0x044c, 0x044d, 0x044e, 0x044f,
};
static const unsigned short __cp1252_hi[128] = {
    0x20ac, 0, 0x201a, 0x0192, 0x201e, 0x2026, 0x2020, 0x2021, 0x02c6, 0x2030, 0x0160, 0x2039, 0x0152, 0, 0x017d, 0,
    0, 0x2018, 0x2019, 0x201c, 0x201d, 0x2022, 0x2013, 0x2014, 0x02dc, 0x2122, 0x0161, 0x203a, 0x0153, 0, 0x017e, 0x0178,
    0x00a0, 0x00a1, 0x00a2, 0x00a3, 0x00a4, 0x00a5, 0x00a6, 0x00a7, 0x00a8, 0x00a9, 0x00aa, 0x00ab, 0x00ac, 0x00ad, 0x00ae, 0x00af,
    0x00b0, 0x00b1, 0x00b2, 0x00b3, 0x00b4, 0x00b5, 0x00b6, 0x00b7, 0x00b8, 0x00b9, 0x00ba, 0x00bb, 0x00bc, 0x00bd, 0x00be, 0x00bf,
    0x00c0, 0x00c1, 0x00c2, 0x00c3, 0x00c4, 0x00c5, 0x00c6, 0x00c7, 0x00c8, 0x00c9, 0x00ca, 0x00cb, 0x00cc, 0x00cd, 0x00ce, 0x00cf,
    0x00d0, 0x00d1, 0x00d2, 0x00d3, 0x00d4, 0x00d5, 0x00d6, 0x00d7, 0x00d8, 0x00d9, 0x00da, 0x00db, 0x00dc, 0x00dd, 0x00de, 0x00df,
    0x00e0, 0x00e1, 0x00e2, 0x00e3, 0x00e4, 0x00e5, 0x00e6, 0x00e7, 0x00e8, 0x00e9, 0x00ea, 0x00eb, 0x00ec, 0x00ed, 0x00ee, 0x00ef,
    0x00f0, 0x00f1, 0x00f2, 0x00f3, 0x00f4, 0x00f5, 0x00f6, 0x00f7, 0x00f8, 0x00f9, 0x00fa, 0x00fb, 0x00fc, 0x00fd, 0x00fe, 0x00ff,
};
static const char *ERR_CHARMAP = "character maps to <undefined>";

static inline const unsigned short *__charmap_table(__ss_encoding enc) {
    return enc == __SS_ENC_CP1250 ? __cp1250_hi : enc == __SS_ENC_CP1251 ? __cp1251_hi : __cp1252_hi;
}

/* code point for byte b, or 0 if undefined (when b != 0) */
static inline __ss_char __charmap_decode(const unsigned short *table, unsigned char b) {
    return b < 0x80 ? b : table[b - 0x80];
}

/* byte for code point cp, or -1 if it cannot be encoded */
static inline int __charmap_encode(const unsigned short *table, __ss_char cp) {
    if (cp < 0x80)
        return (int)cp;
    for (int i = 0; i < 128; i++)
        if (table[i] && table[i] == cp)
            return 0x80 + i;
    return -1;
}

static inline bool __encodable(__ss_encoding enc, __ss_char cp) {
    switch (enc) {
        case __SS_ENC_ASCII: return cp < 0x80;
        case __SS_ENC_LATIN1: return cp < 0x100;
        case __SS_ENC_CP1250:
        case __SS_ENC_CP1251:
        case __SS_ENC_CP1252: return __charmap_encode(__charmap_table(enc), cp) >= 0;
        default: return !(cp >= 0xd800 && cp <= 0xdfff) && cp <= __MAX_CODEPOINT;
    }
}

void __throw_encode_error(__ss_encoding enc, str *s, size_t start, const char *msg) {
    const char *codec = enc == __SS_ENC_UTF8 ? "utf-8" : enc == __SS_ENC_ASCII ? "ascii" : enc == __SS_ENC_LATIN1 ? "latin-1" : "charmap";
    size_t end = start + 1;
    while (end < s->unit.size() && !__encodable(enc, s->unit[end]))
        end++;
    throw new UnicodeEncodeError(new str(codec), s, (__ss_int)start, (__ss_int)end, new str(msg));
}

size_t __utf8_decode_checked(bytes *b, __ss_char *dst) {
    const char *src = b->unit.data();
    size_t len = b->unit.size();
    __codec_result r = __utf8_decode(src, len, dst);
    if (!r.ok) {
        size_t start = r.errpos, end = r.errpos + 1;
        if (r.errmsg == ERR_TRUNC) { /* errpos = start of the incomplete sequence */
            end = len;
        } else if (r.errmsg == ERR_CONT) { /* errpos = first bad continuation byte: back up over
                                              the valid continuation bytes to the start byte */
            end = r.errpos;
            start = r.errpos - 1;
            while (start > 0 && ((unsigned char)src[start] & 0xc0) == 0x80)
                start--;
        }
        __throw_decode_error("utf-8", b, start, end, r.errmsg);
    }
    return r.units;
}

size_t __utf8_encode_checked(str *s, char *dst) {
    __codec_result r = __utf8_encode(s->unit.data(), s->unit.size(), dst);
    if (!r.ok)
        __throw_encode_error(__SS_ENC_UTF8, s, r.errpos, r.errmsg);
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
    if (norm == "utf-8-sig")
        return __SS_ENC_UTF8_SIG;
    if (norm == "cp1250" || norm == "windows-1250" || norm == "1250")
        return __SS_ENC_CP1250;
    if (norm == "cp1251" || norm == "windows-1251" || norm == "1251")
        return __SS_ENC_CP1251;
    if (norm == "cp1252" || norm == "windows-1252" || norm == "1252")
        return __SS_ENC_CP1252;
    char buf[128];
    snprintf(buf, sizeof(buf), "unknown encoding: %s", __to_utf8(encoding->unit).c_str());
    throw new LookupError(new str(buf));
}

__ss_errors __lookup_errors(str *errors) {
    if (!errors || errors->unit == U"strict")
        return __SS_ERR_STRICT;
    if (errors->unit == U"surrogateescape")
        return __SS_ERR_SURROGATEESCAPE;
    if (errors->unit == U"ignore")
        return __SS_ERR_IGNORE;
    if (errors->unit == U"replace")
        return __SS_ERR_REPLACE;
    char buf[192];
    snprintf(buf, sizeof(buf), "error handler '%s' is not supported by shedskin (only 'strict', 'surrogateescape', 'ignore' and 'replace')", __to_utf8(errors->unit).c_str());
    throw new ValueError(new str(buf));
}

/* length of the maximal subpart of the ill-formed utf-8 sequence at
   src[pos] (unicode ch. 3, 'U+FFFD substitution of maximal subparts', as
   CPython's 'replace' handler): the longest prefix that could still start
   a valid sequence, or 1 */
static size_t __utf8_maximal_subpart(const char *src, size_t len, size_t pos) {
    size_t nfollow;
    __ss_char bits;
    unsigned char lo, hi; /* valid range for the second byte */
    if (!__utf8_lead((unsigned char)src[pos], &nfollow, &bits, &lo, &hi))
        return 1;
    size_t n = nfollow + 1;
    size_t k = 1;
    while (k < n && pos + k < len) {
        unsigned b = (unsigned char)src[pos + k];
        if (k == 1 ? (b < lo || b > hi) : ((b & 0xc0) != 0x80))
            break;
        k++;
    }
    return k;
}

void __decode_into(__GC_STR &out, const char *src, size_t len, __ss_encoding enc, __ss_errors err) {
    if (enc == __SS_ENC_UTF8_SIG) /* (the bom is up to the caller) */
        enc = __SS_ENC_UTF8;
    if (enc == __SS_ENC_LATIN1) { /* cannot fail */
        size_t base = out.size();
        out.resize(base + len);
        __latin1_decode(src, len, &out[base]);
        return;
    }
    if (err == __SS_ERR_STRICT && !__ss_charmap(enc)) {
        size_t base = out.size();
        out.resize(base + len); /* upper bound: at most one code point per byte */
        __codec_result r = (enc == __SS_ENC_UTF8) ?
            __utf8_decode(src, len, &out[base]) :
            __ascii_decode(src, len, &out[base]);
        if (!r.ok) {
            out.resize(base);
            bytes *b = new bytes(src, len);
            if (enc == __SS_ENC_UTF8)
                __utf8_decode_checked(b, 0); /* throws, with CPython's range */
            __throw_decode_error("ascii", b, r.errpos, r.errpos + 1, r.errmsg);
        }
        out.resize(base + r.units);
        return;
    }
    out.reserve(out.size() + len);
    size_t pos = 0;
    while (pos < len) {
        __ss_char cp;
        size_t n;
        if (enc == __SS_ENC_UTF8)
            n = __utf8_decode_one(src, len, pos, &cp);
        else if (__ss_charmap(enc)) {
            cp = __charmap_decode(__charmap_table(enc), (unsigned char)src[pos]);
            n = (cp || !src[pos]) ? 1 : 0;
        } else {
            cp = (unsigned char)src[pos];
            n = cp < 0x80 ? 1 : 0;
        }
        if (n) {
            out += cp;
            pos += n;
            continue;
        }
        if (err == __SS_ERR_STRICT) /* (charmaps only, see above) */
            __throw_decode_error("charmap", new bytes(src, len), pos, pos + 1, ERR_CHARMAP);
        if (err == __SS_ERR_SURROGATEESCAPE) /* each bad byte on its own */
            out += (__ss_char)(0xdc00u | (unsigned char)src[pos]);
        else if (err == __SS_ERR_REPLACE) {
            out += (__ss_char)0xfffd;
            if (enc == __SS_ENC_UTF8) {
                pos += __utf8_maximal_subpart(src, len, pos);
                continue;
            }
        } /* else ignore */
        pos++;
    }
}

static inline void __utf8_append(__GC_BYTES &out, __ss_char cp) {
    char buf[4];
    out.append(buf, __utf8_put(buf, cp));
}

void __encode_into(__GC_BYTES &out, str *s, __ss_encoding enc, __ss_errors err) {
    if (enc == __SS_ENC_UTF8_SIG)
        enc = __SS_ENC_UTF8;
    const __GC_STR &u = s->unit;
    size_t len = u.size();
    out.reserve(out.size() + len);
    for (size_t i = 0; i < len; i++) {
        __ss_char cp = u[i];
        if (__encodable(enc, cp)) {
            if (enc == __SS_ENC_UTF8)
                __utf8_append(out, cp);
            else if (__ss_charmap(enc))
                out += (char)(unsigned char)__charmap_encode(__charmap_table(enc), cp);
            else
                out += (char)(unsigned char)cp;
            continue;
        }
        if (err == __SS_ERR_SURROGATEESCAPE && cp >= 0xdc80 && cp <= 0xdcff)
            out += (char)(unsigned char)(cp & 0xffu);
        else if (err == __SS_ERR_REPLACE)
            out += '?';
        else if (err == __SS_ERR_STRICT || err == __SS_ERR_SURROGATEESCAPE)
            __throw_encode_error(enc, s, i, enc == __SS_ENC_UTF8 ? ERR_SURROGATE : enc == __SS_ENC_ASCII ? ERR_ASCII : enc == __SS_ENC_LATIN1 ? ERR_LATIN1 : ERR_CHARMAP);
        /* else ignore */
    }
}

__GC_STR __from_utf8(const char *s, size_t len) {
    __GC_STR out;
    out.reserve(len);
    size_t pos = 0;
    while (pos < len) {
        __ss_char cp;
        size_t n = __utf8_decode_one(s, len, pos, &cp);
        if (n == 0) {
            unsigned char b0 = (unsigned char)s[pos];
            if (b0 == 0xed && pos + 2 < len && /* wtf-8 surrogate (ed a0..bf 80..bf), as __to_utf8 emits */
                ((unsigned char)s[pos + 1] & 0xe0) == 0xa0 && ((unsigned char)s[pos + 2] & 0xc0) == 0x80) {
                cp = 0xd000 | (((__ss_char)(unsigned char)s[pos + 1] & 0x3fu) << 6) | ((__ss_char)(unsigned char)s[pos + 2] & 0x3fu);
                n = 3;
            } else { /* lenient: invalid byte escapes to U+DC80..U+DCFF (PEP 383 surrogateescape) */
                cp = (__ss_char)(0xdc00u | b0);
                n = 1;
            }
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
        else if (cp >= 0xdc80 && cp <= 0xdcff) /* surrogateescape: back to the original byte */
            out += (char)(unsigned char)(cp & 0xffu);
        else { /* note: other surrogates pass through (wtf-8) */
            char buf[4];
            out.append(buf, __utf8_put(buf, cp));
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
