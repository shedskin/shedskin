/* Copyright 2005-2026 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE) */

#ifndef SS_UNICODE_HPP
#define SS_UNICODE_HPP

/* codec primitives for unicode support: utf-8, ascii, latin-1.

   these translate between raw bytes (char) and unicode code points
   (char32_t), with strict validation matching CPython (overlong
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
#endif

const char32_t __MAX_CODEPOINT = 0x10FFFF;

struct __codec_result {
    bool ok;
    size_t units;       /* units produced (or that would be, if dst==NULL):
                           code points for decode, bytes for encode */
    size_t errpos;      /* on error: index in src of the offending unit */
    const char *errmsg; /* on error: static description (CPython wording) */
};

/* decode: bytes -> code points. dst may be NULL to validate/measure only. */
__codec_result __utf8_decode(const char *src, size_t len, char32_t *dst);

/* encode: code points -> bytes. dst may be NULL to measure only. */
__codec_result __utf8_encode(const char32_t *src, size_t len, char *dst);

/* ascii: code points < 0x80; latin-1: code points < 0x100
   (latin-1 decode cannot fail) */
__codec_result __ascii_decode(const char *src, size_t len, char32_t *dst);
__codec_result __ascii_encode(const char32_t *src, size_t len, char *dst);
__codec_result __latin1_decode(const char *src, size_t len, char32_t *dst);
__codec_result __latin1_encode(const char32_t *src, size_t len, char *dst);

#ifndef __SS_UNICODE_STANDALONE
/* wrappers that raise ValueError with a CPython-style message (to become
   UnicodeDecodeError/UnicodeEncodeError, which subclass ValueError, once
   those exist). return the number of units produced. */
size_t __utf8_decode_checked(const char *src, size_t len, char32_t *dst);
size_t __utf8_encode_checked(const char32_t *src, size_t len, char *dst);
#endif

#ifdef __SS_UNICODE_STANDALONE
} // namespace __shedskin__
#endif

#endif
