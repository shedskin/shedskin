/* Copyright 2005-2026 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE) */

#ifndef SS_UNICODE_HPP
#define SS_UNICODE_HPP

/* codec primitives for unicode support: utf-8, ascii, latin-1.

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
/* wrappers that raise ValueError with a CPython-style message (to become
   UnicodeDecodeError/UnicodeEncodeError, which subclass ValueError, once
   those exist). return the number of units produced. */
size_t __utf8_decode_checked(const char *src, size_t len, __ss_char *dst);
size_t __utf8_encode_checked(const __ss_char *src, size_t len, char *dst);

void __throw_decode_error(const char *codec, unsigned char b, size_t pos, const char *msg);
void __throw_encode_error(const char *codec, __ss_char cp, size_t pos, const char *msg);

/* supported encodings for str.encode/bytes.decode */
enum __ss_encoding {
    __SS_ENC_UTF8,
    __SS_ENC_ASCII,
    __SS_ENC_LATIN1,
};

/* normalize an encoding name (0 means the default, utf-8) to an
   __ss_encoding; raises LookupError for anything unsupported */
__ss_encoding __lookup_encoding(str *encoding);

/* only 'strict' (or 0) is accepted for the errors= argument for now */
void __check_errors_arg(str *errors);

/* internal conversions between the utf-8 boundary representation and
   the __ss_char code point representation used inside str. these never
   throw: invalid utf-8 bytes decode as one code point per byte, and
   surrogate code points encode as normal 3-byte sequences (wtf-8), so
   trusted internal sources (number formatting, literals) are safe. */
__GC_STR __from_utf8(const char *s, size_t len);
__GC_STR __from_utf8(const __GC_BYTES &b);
__GC_BYTES __to_utf8(const __ss_char *s, size_t len);
__GC_BYTES __to_utf8(const __GC_STR &u);

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

/* ascii + latin-1 case mapping for now (proper unicode tables later);
   the latin-1 exceptions: 0xd7/0xf7 are multiply/divide signs, 0xdf
   (sharp s) uppercases to "SS" which needs multi-char mappings, and
   0xff (y-diaeresis) uppercases outside latin-1 (U+0178) */
inline __ss_char __ss_toupper(__ss_char c) {
    if (c >= 'a' && c <= 'z') return c - 32;
    if (c >= 0xe0 && c <= 0xfe && c != 0xf7) return c - 32;
    return c;
}
inline __ss_char __ss_tolower(__ss_char c) {
    if (c >= 'A' && c <= 'Z') return c + 32;
    if (c >= 0xc0 && c <= 0xde && c != 0xd7) return c + 32;
    return c;
}

/* cased-letter predicates over the same ascii + latin-1 subset */
inline bool __ss_char_upper(__ss_char c) {
    return (c >= 'A' && c <= 'Z') || (c >= 0xc0 && c <= 0xde && c != 0xd7);
}
inline bool __ss_char_lower(__ss_char c) {
    return (c >= 'a' && c <= 'z') || (c >= 0xdf && c <= 0xff && c != 0xf7);
}
inline bool __ss_char_alpha(__ss_char c) {
    return __ss_char_upper(c) || __ss_char_lower(c);
}
#endif

#ifdef __SS_UNICODE_STANDALONE
} // namespace __shedskin__
#endif

#endif
