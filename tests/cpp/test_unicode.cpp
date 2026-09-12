/* standalone unit test for shedskin/lib/builtin/unicode.{hpp,cpp}.

   not part of the python test suite; build and run manually:

     c++ -std=c++17 -Wall -Wextra -Wconversion -D__SS_UNICODE_STANDALONE \
         -I../../shedskin/lib/builtin tests/cpp/test_unicode.cpp -o test_unicode && ./test_unicode
*/

#ifndef __SS_UNICODE_STANDALONE
#define __SS_UNICODE_STANDALONE
#endif
#include "unicode.hpp"
#include "unicode.cpp"

#include <cstdio>
#include <cstring>

using namespace __shedskin__;

static int failures = 0;

#define CHECK(cond) do { \
    if (!(cond)) { \
        printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); \
        failures++; \
    } \
} while (0)

/* decode utf-8, expect success with the given code points */
static void ok_utf8(const char *bytes, size_t blen, const char32_t *cps, size_t clen) {
    char32_t buf[64];
    __codec_result measure = __utf8_decode(bytes, blen, 0);
    __codec_result r = __utf8_decode(bytes, blen, buf);
    CHECK(r.ok);
    CHECK(r.units == clen);
    CHECK(measure.ok && measure.units == r.units); /* NULL dst measures the same */
    for (size_t i = 0; i < clen; i++)
        CHECK(buf[i] == cps[i]);

    /* and roundtrip */
    char back[64];
    __codec_result e = __utf8_encode(cps, clen, back);
    CHECK(e.ok);
    CHECK(e.units == blen);
    CHECK(memcmp(back, bytes, blen) == 0);
    __codec_result emeasure = __utf8_encode(cps, clen, 0);
    CHECK(emeasure.ok && emeasure.units == blen);
}

/* decode utf-8, expect failure at errpos with errmsg */
static void bad_utf8(const char *bytes, size_t blen, size_t errpos, const char *errmsg) {
    __codec_result r = __utf8_decode(bytes, blen, 0);
    CHECK(!r.ok);
    CHECK(r.errpos == errpos);
    CHECK(strcmp(r.errmsg, errmsg) == 0);
}

int main() {
    /* ascii fast path */
    { const char32_t c[] = {'h','e','l','l','o'}; ok_utf8("hello", 5, c, 5); }
    { ok_utf8("", 0, 0, 0); }
    { const char32_t c[] = {0}; ok_utf8("\0", 1, c, 1); } /* NUL is fine, not NUL-terminated api */

    /* 2/3/4-byte sequences: e-acute, euro sign, CJK, emoji */
    { const char32_t c[] = {0xe9}; ok_utf8("\xc3\xa9", 2, c, 1); }
    { const char32_t c[] = {0x20ac}; ok_utf8("\xe2\x82\xac", 3, c, 1); }
    { const char32_t c[] = {0x6f22, 0x5b57}; ok_utf8("\xe6\xbc\xa2\xe5\xad\x97", 6, c, 2); }
    { const char32_t c[] = {0x1f600}; ok_utf8("\xf0\x9f\x98\x80", 4, c, 1); }
    { const char32_t c[] = {'a', 0xe9, 0x1f600, 'z'}; ok_utf8("a\xc3\xa9\xf0\x9f\x98\x80z", 8, c, 4); }

    /* encoding-length boundaries: 7f/80, 7ff/800, ffff/10000, 10ffff */
    { const char32_t c[] = {0x7f}; ok_utf8("\x7f", 1, c, 1); }
    { const char32_t c[] = {0x80}; ok_utf8("\xc2\x80", 2, c, 1); }
    { const char32_t c[] = {0x7ff}; ok_utf8("\xdf\xbf", 2, c, 1); }
    { const char32_t c[] = {0x800}; ok_utf8("\xe0\xa0\x80", 3, c, 1); }
    { const char32_t c[] = {0xffff}; ok_utf8("\xef\xbf\xbf", 3, c, 1); }
    { const char32_t c[] = {0x10000}; ok_utf8("\xf0\x90\x80\x80", 4, c, 1); }
    { const char32_t c[] = {0x10ffff}; ok_utf8("\xf4\x8f\xbf\xbf", 4, c, 1); }
    /* around the surrogate gap */
    { const char32_t c[] = {0xd7ff}; ok_utf8("\xed\x9f\xbf", 3, c, 1); }
    { const char32_t c[] = {0xe000}; ok_utf8("\xee\x80\x80", 3, c, 1); }

    /* invalid start bytes: lone continuation, c0/c1, f5, ff */
    bad_utf8("\x80", 1, 0, "invalid start byte");
    bad_utf8("a\xbf", 2, 1, "invalid start byte");
    bad_utf8("\xc0\xaf", 2, 0, "invalid start byte");    /* overlong 2-byte */
    bad_utf8("\xc1\xbf", 2, 0, "invalid start byte");
    bad_utf8("\xf5\x80\x80\x80", 4, 0, "invalid start byte");
    bad_utf8("\xff", 1, 0, "invalid start byte");

    /* bad continuation bytes */
    bad_utf8("\xc3\x29", 2, 1, "invalid continuation byte");
    bad_utf8("\xe2\x82\xc0", 3, 2, "invalid continuation byte");
    bad_utf8("\xe0\x80\x80", 3, 1, "invalid continuation byte");  /* overlong 3-byte */
    bad_utf8("\xe0\x9f\xbf", 3, 1, "invalid continuation byte");  /* overlong 3-byte */
    bad_utf8("\xf0\x8f\xbf\xbf", 4, 1, "invalid continuation byte"); /* overlong 4-byte */
    bad_utf8("\xed\xa0\x80", 3, 1, "invalid continuation byte");  /* surrogate d800 */
    bad_utf8("\xed\xbf\xbf", 3, 1, "invalid continuation byte");  /* surrogate dfff */
    bad_utf8("\xf4\x90\x80\x80", 4, 1, "invalid continuation byte"); /* > 10ffff */

    /* truncated sequences: errpos = start of incomplete sequence */
    bad_utf8("\xc3", 1, 0, "unexpected end of data");
    bad_utf8("\xe2\x82", 2, 0, "unexpected end of data");
    bad_utf8("ab\xf0\x9f\x98", 5, 2, "unexpected end of data");

    /* error after valid prefix: units reflects code points already decoded */
    {
        __codec_result r = __utf8_decode("ab\xc3\xa9\x80", 5, 0);
        CHECK(!r.ok && r.units == 3 && r.errpos == 4);
    }

    /* encode errors: surrogate, out of range */
    {
        const char32_t c[] = {'a', 0xd800};
        __codec_result r = __utf8_encode(c, 2, 0);
        CHECK(!r.ok && r.errpos == 1 && strcmp(r.errmsg, "surrogates not allowed") == 0);
        CHECK(r.units == 1);
    }
    {
        const char32_t c[] = {0x110000};
        __codec_result r = __utf8_encode(c, 1, 0);
        CHECK(!r.ok && r.errpos == 0 && strcmp(r.errmsg, "code point out of range") == 0);
    }

    /* ascii */
    {
        char32_t cps[8]; char bytes[8];
        __codec_result r = __ascii_decode("abc", 3, cps);
        CHECK(r.ok && r.units == 3 && cps[0] == 'a' && cps[2] == 'c');
        r = __ascii_encode(cps, 3, bytes);
        CHECK(r.ok && r.units == 3 && memcmp(bytes, "abc", 3) == 0);
        r = __ascii_decode("ab\xc3", 3, 0);
        CHECK(!r.ok && r.errpos == 2 && strcmp(r.errmsg, "ordinal not in range(128)") == 0);
        const char32_t hi[] = {'a', 0x80};
        r = __ascii_encode(hi, 2, 0);
        CHECK(!r.ok && r.errpos == 1);
    }

    /* latin-1: decode maps bytes 1:1 and cannot fail; encode fails >= 0x100 */
    {
        char32_t cps[8]; char bytes[8];
        __codec_result r = __latin1_decode("\x00\x41\x80\xff", 4, cps);
        CHECK(r.ok && r.units == 4 && cps[0] == 0 && cps[1] == 0x41 && cps[2] == 0x80 && cps[3] == 0xff);
        r = __latin1_encode(cps, 4, bytes);
        CHECK(r.ok && r.units == 4 && memcmp(bytes, "\x00\x41\x80\xff", 4) == 0);
        const char32_t hi[] = {0xff, 0x100};
        r = __latin1_encode(hi, 2, 0);
        CHECK(!r.ok && r.errpos == 1 && strcmp(r.errmsg, "ordinal not in range(256)") == 0);
    }

    if (failures) {
        printf("%d FAILURES\n", failures);
        return 1;
    }
    printf("all tests passed\n");
    return 0;
}
