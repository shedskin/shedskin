/* Copyright 2005-2026 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE) */

#ifndef SS_UNICODE_HPP
#define SS_UNICODE_HPP

/* codec primitives for unicode support: utf-8, ascii, latin-1 (utf-8-sig
   and the cp125x code pages are layered on top, see __decode_into/
   __encode_into and str::encode/bytes::decode).

   these translate between raw bytes (char) and unicode code points
   (__ss_char), with strict validation matching CPython (overlong
   sequences, surrogates and code points beyond U+10FFFF are rejected).

   they are deliberately independent of the str representation and of
   __SS_UNICODE, so they can be built and tested with or without that
   flag; nothing else in the runtime uses them yet. */

/* like the other headers in builtin/, this file is normally included
   from builtin.hpp *inside* namespace __shedskin__; the guard below only
   exists for the standalone unit test (tests/cpp/test_unicode.cpp). */
#ifdef __SS_UNICODE_STANDALONE
#include <cstddef>
namespace __shedskin__ {
typedef char32_t __ss_char;
#endif

const __ss_char __MAX_CODEPOINT = 0x10FFFF;

/* printability, as used by repr() and str.isprintable(): a code point is
   non-printable when its unicode general category is Cc, Cf, Cs, Co, Zl,
   Zp or Zs -- with the space character itself as the one exception.

   CPython also treats Cn (unassigned) as non-printable. that is left out
   here on purpose: Cn accounts for ~700 of the ~730 ranges involved (the
   table below is 28), and it shifts with every unicode release, so
   CPython's own output for those code points changes between versions
   anyway. the visible difference is that repr() of a currently
   unassigned code point shows it raw instead of escaped. */
bool __ss_char_printable_nonascii(__ss_char c); /* c >= 0x80, see unicode.cpp */

inline bool __ss_char_printable(__ss_char c) {
    if (c < 0x80) /* no table lookup for the common case */
        return c >= 0x20 && c != 0x7f;
    return __ss_char_printable_nonascii(c);
}

struct __codec_result {
    bool ok;
    size_t units;       /* units produced (or that would be, if dst==NULL):
                           code points for decode, bytes for encode */
    size_t errpos;      /* on error: index in src of the offending unit */
    const char *errmsg; /* on error: static description (CPython wording) */
};

/* decode: bytes -> code points. dst may be NULL to validate/measure only. */
__codec_result __utf8_decode(const char *src, size_t len, __ss_char *dst);

/* decode a single utf-8 sequence starting at src[pos]; returns the number
   of bytes consumed and stores the code point in *cp, or returns 0 if
   there is no valid sequence at pos (invalid/truncated/overlong/..) */
size_t __utf8_decode_one(const char *src, size_t len, size_t pos, __ss_char *cp);

/* encode: code points -> bytes. dst may be NULL to measure only. */
__codec_result __utf8_encode(const __ss_char *src, size_t len, char *dst);

/* ascii: code points < 0x80; latin-1: code points < 0x100
   (latin-1 decode cannot fail) */
__codec_result __ascii_decode(const char *src, size_t len, __ss_char *dst);
__codec_result __ascii_encode(const __ss_char *src, size_t len, char *dst);
__codec_result __latin1_decode(const char *src, size_t len, __ss_char *dst);
__codec_result __latin1_encode(const __ss_char *src, size_t len, char *dst);

#ifndef __SS_UNICODE_STANDALONE
/* supported encodings for str.encode/bytes.decode */
enum __ss_encoding {
    __SS_ENC_UTF8,
    __SS_ENC_ASCII,
    __SS_ENC_LATIN1,
    __SS_ENC_UTF8_SIG, /* utf-8 with a byte order mark (skipped/added) */
    /* single-byte windows code pages ('charmap' codecs in CPython) */
    __SS_ENC_CP1250, /* central european */
    __SS_ENC_CP1251, /* cyrillic */
    __SS_ENC_CP1252, /* western: latin-1 with 0x80-0x9f remapped */
};

inline bool __ss_charmap(__ss_encoding enc) {
    return enc == __SS_ENC_CP1250 || enc == __SS_ENC_CP1251 || enc == __SS_ENC_CP1252;
}

/* wrappers that raise UnicodeDecodeError/UnicodeEncodeError (with
   CPython's message, start/end range and attributes) on failure. return
   the number of units produced. */
size_t __utf8_decode_checked(bytes *b, __ss_char *dst);
size_t __utf8_encode_checked(str *s, char *dst);

/* raise a UnicodeDecodeError for b[start:end] */
void __throw_decode_error(const char *codec, bytes *b, size_t start, size_t end, const char *msg);
/* raise a UnicodeEncodeError for the run of unencodable code points
   starting at s[start] (CPython reports consecutive bad characters as
   one range) */
void __throw_encode_error(__ss_encoding enc, str *s, size_t start, const char *msg);

/* normalize an encoding name (0 means the default, utf-8) to an
   __ss_encoding; raises LookupError for anything unsupported */
__ss_encoding __lookup_encoding(str *encoding);


/* internal conversions between the utf-8 boundary representation and
   the __ss_char code point representation used inside str. these never
   throw: like CPython's filesystem encoding (utf-8 + surrogateescape,
   PEP 383), an invalid utf-8 byte b decodes as the lone surrogate
   U+DC00+b, and those surrogates encode back to the original byte, so
   argv, environment and path bytes survive a round trip. other surrogate
   code points round-trip as normal 3-byte sequences (wtf-8). trusted
   internal sources (number formatting, literals) are unaffected. */
__GC_STR __from_utf8(const char *s, size_t len);
__GC_STR __from_utf8(const __GC_BYTES &b);
__GC_BYTES __to_utf8(const __ss_char *s, size_t len);
__GC_BYTES __to_utf8(const __GC_STR &u);

/* code points <-> utf-16 (native wide strings on Windows). like CPython
   on Windows (surrogatepass), lone surrogates are kept as single units in
   both directions, so file names that are not valid utf-16 still round
   trip; only a proper high+low pair combines into one code point. these
   are templates on the unit type so they work with wchar_t (Windows) as
   well as char16_t (tests elsewhere). */
template<class W> std::basic_string<W> __to_utf16(const __GC_STR &u) {
    std::basic_string<W> out;
    out.reserve(u.size());
    for (__ss_char cp : u) {
        if (cp >= 0x10000 && cp <= __MAX_CODEPOINT) {
            cp -= 0x10000;
            out += (W)(0xd800 + (cp >> 10));
            out += (W)(0xdc00 + (cp & 0x3ff));
        } else
            out += (W)(cp > __MAX_CODEPOINT ? 0xfffd : cp);
    }
    return out;
}

template<class W> __GC_STR __from_utf16(const W *w, size_t len) {
    __GC_STR out;
    out.reserve(len);
    for (size_t i = 0; i < len; i++) {
        __ss_char c = (__ss_char)(unsigned)w[i] & 0xffff;
        if (c >= 0xd800 && c < 0xdc00 && i + 1 < len) {
            __ss_char d = (__ss_char)(unsigned)w[i + 1] & 0xffff;
            if (d >= 0xdc00 && d < 0xe000) {
                out += (__ss_char)(0x10000 + ((c - 0xd800) << 10) + (d - 0xdc00));
                i++;
                continue;
            }
        }
        out += c;
    }
    return out;
}

/* error handlers supported for encode/decode and text files */
enum __ss_errors {
    __SS_ERR_STRICT,
    __SS_ERR_SURROGATEESCAPE,
    __SS_ERR_IGNORE,
    __SS_ERR_REPLACE,
};

/* normalize an errors= argument (0 means 'strict'); raises ValueError for
   anything unsupported */
__ss_errors __lookup_errors(str *errors);

/* generic (error-handler aware) codecs, appending to out. decode errors
   with __SS_ERR_STRICT raise UnicodeDecodeError, reporting positions
   relative to src; replace follows CPython (one U+FFFD per maximal
   subpart of an ill-formed utf-8 sequence; '?' when encoding). */
void __decode_into(__GC_STR &out, const char *src, size_t len, __ss_encoding enc, __ss_errors err);
void __encode_into(__GC_BYTES &out, str *s, __ss_encoding enc, __ss_errors err);

/* widen an ascii c-string / std::string to __GC_STR (repr building etc.) */
__GC_STR __gcs(const char *s);
__GC_STR __gcs(const std::string &s);

/* 1:1 (latin-1 style) conversions between bytes and code points, for
   internal reuse of str machinery on bytes (%-formatting); __narrow
   replaces code points above 0xff with '?' */
__GC_STR __widen(const __GC_BYTES &b);
__GC_BYTES __narrow(const __GC_STR &u);
std::string __narrow_std(const __GC_STR &u);

/* single-character str for a code point (cached below 256) */
str *__char_str(__ss_char cp);

/* character database for the str methods: character classes and full
   case mappings, generated from CPython's own str methods by
   scripts/gen_unicode_db.py (see there to regenerate for a newer unicode
   version). a record holds the flags below plus the upper, lower, title
   and casefold mappings of a code point, each either a delta to add to the
   code point, or, for records with __SS_CHAR_EXTENDED_CASE set (the
   mapping of one or more of the four is not a single code point, as in
   '\xdf'.upper() == 'SS'), (length << 24) | offset into
   __ss_char_ext_case. the decimal digit value is kept for int()/float(). */
struct __ss_char_record {
    int map[4];
    unsigned short flags;
    signed char decimal; /* decimal digit value, or -1 */
};

enum {
    __SS_CHAR_UPPER_MAP = 0,
    __SS_CHAR_LOWER_MAP = 1,
    __SS_CHAR_TITLE_MAP = 2,
    __SS_CHAR_FOLD_MAP = 3,
};

#define __SS_CHAR_ALPHA          0x0001
#define __SS_CHAR_DECIMAL        0x0002
#define __SS_CHAR_DIGIT          0x0004
#define __SS_CHAR_NUMERIC        0x0008
#define __SS_CHAR_LOWER          0x0010
#define __SS_CHAR_UPPER          0x0020
#define __SS_CHAR_TITLE          0x0040
#define __SS_CHAR_CASED          0x0080
#define __SS_CHAR_CASE_IGNORABLE 0x0100
#define __SS_CHAR_SPACE          0x0200
#define __SS_CHAR_XID_START      0x0400
#define __SS_CHAR_XID_CONTINUE   0x0800
#define __SS_CHAR_EXTENDED_CASE  0x1000

#include "unicode_db.hpp"

/* three-level table lookup (the generator picks the shifts) */
inline const __ss_char_record *__ss_char_rec(__ss_char c) {
    if (c > __MAX_CODEPOINT) /* not a code point, so like an unassigned one */
        c = 0x10ffff;
    const size_t mid = __SS_UCD_SHIFT1 - __SS_UCD_SHIFT2;
    size_t i = __ss_char_index1[c >> __SS_UCD_SHIFT1];
    i = __ss_char_index2[(i << mid) + ((c >> __SS_UCD_SHIFT2) & ((1u << mid) - 1))];
    return &__ss_char_records[__ss_char_index3[(i << __SS_UCD_SHIFT2) + (c & ((1u << __SS_UCD_SHIFT2) - 1))]];
}

inline bool __ss_char_has(__ss_char c, unsigned short flags) {
    return (__ss_char_rec(c)->flags & flags) != 0;
}

/* whitespace as in str.isspace/split/strip (includes \x1c-\x1f) */
inline bool __ss_char_space(__ss_char c) {
    if (c < 0x80)
        return c == ' ' || (c >= '\t' && c <= '\r') || (c >= 0x1c && c <= 0x1f);
    return __ss_char_has(c, __SS_CHAR_SPACE);
}

/* the ascii text int() and float() parse, as CPython's
   _PyUnicode_TransformDecimalAndSpaceToASCII: unicode whitespace becomes a
   space, decimal digits of any script their ascii digit, any other
   non-ascii character (and NUL, so it cannot end the parse early) '?' */
__GC_STRING __ss_ascii_numeric(str *s);

/* append the full (possibly multi-character) case mapping of c */
inline void __ss_char_map_to(__GC_STR &out, __ss_char c, int which) {
    const __ss_char_record *r = __ss_char_rec(c);
    int v = r->map[which];
    if (!(r->flags & __SS_CHAR_EXTENDED_CASE))
        out += (__ss_char)((int)c + v);
    else
        out.append(__ss_char_ext_case + (v & 0xffffff), (size_t)(v >> 24));
}
#endif

#ifdef __SS_UNICODE_STANDALONE
} // namespace __shedskin__
#endif

#endif
