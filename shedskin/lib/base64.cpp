/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "base64.hpp"
#include "binascii.hpp"
#include <cstring>

namespace __base64__ {

str *__name__;

/* Non-trivial argument defaults from base64.py, numbered in definition
 * order by the compiler (every non-numeric, non-bool default counts, so
 * None and __void defaults take up numbers too; keep in sync when editing
 * the model):
 *   default_4:  b16decode(ignorechars=b'')
 *   default_6:  b32decode(ignorechars=b'')
 *   default_7:  b32hexdecode(ignorechars=b'')
 *   default_8:  a85decode(ignorechars=b' \t\n\r\v')
 *   default_9:  b85decode(ignorechars=b'')
 *   default_10: z85decode(ignorechars=b'')
 */
bytes *default_4, *default_6, *default_7, *default_8, *default_9, *default_10;

/* BASE64_ALPHABET[:-2] + altchars, as base64.py does it */
static bytes *alt_alphabet(bytes *altchars) {
    bytes *alphabet = new bytes(__binascii__::BASE64_ALPHABET);
    alphabet->unit[62] = altchars->unit[0];
    alphabet->unit[63] = altchars->unit[1];
    return alphabet;
}

bytes *b64encode(bytes *s, bytes *altchars, __ss_bool padded, __ss_int wrapcol) {
    if (altchars) {
        if (altchars->unit.size() != 2)
            throw new ValueError(new str("invalid altchars"));
        return __binascii__::b2a_base64(s, False, wrapcol, padded, alt_alphabet(altchars));
    }
    return __binascii__::b2a_base64(s, False, wrapcol, padded);
}

bytes *standard_b64encode(bytes *s) {
    return b64encode(s, NULL);
}

bytes *urlsafe_b64encode(bytes *s, __ss_bool padded) {
    return b64encode(s, new bytes("-_"), padded);
}

bytes *__b64decode(bytes *s, bytes *altchars, int validate, __ss_bool padded, bytes *ignorechars, __ss_bool canonical) {
    if (validate == -1)
        validate = (ignorechars != NULL);
    if (altchars) {
        if (altchars->unit.size() != 2)
            throw new ValueError(new str("invalid altchars"));
        if (ignorechars == NULL) {
            /* Legacy behaviour (deprecated in CPython 3.15 but still in
            ** effect): base64.py translates altchars onto '+'/'/' before
            ** decoding, so literal '+' and '/' stay valid data alongside
            ** the altchars. Emulate that with a reverse table that has
            ** both mappings, rather than translating a copy of s. */
            unsigned char table[256];
            memcpy(table, __binascii__::__a2b_base64_table(), 256);
            table[(unsigned char)altchars->unit[0]] = 62;
            table[(unsigned char)altchars->unit[1]] = 63;
            return __binascii__::__a2b_base64(s, validate, padded, (const unsigned char *)table, (bytes *)NULL, canonical);
        }
        /* New-style: '+'/'/' are only valid if they are the altchars. */
        return __binascii__::__a2b_base64(s, validate, padded, alt_alphabet(altchars), ignorechars, canonical);
    }
    return __binascii__::__a2b_base64(s, validate, padded, (bytes *)NULL, ignorechars, canonical);
}

bytes *standard_b64decode(bytes *s) {
    return b64decode(s, NULL, False);
}

bytes *urlsafe_b64decode(bytes *s, __ss_bool padded) {
    // note: unlike b64decode, this defaults to padded=False (CPython 3.15)
    return b64decode(s, new bytes("-_"), False, padded);
}

bytes *b16encode(bytes *s, __ss_int wrapcol) {
    /* mirrors base64.py: hexlify(s, bytes_per_sep=-(wrapcol//2), sep=b'\n') */
    if (!wrapcol)
        return __binascii__::hexlify(s)->upper();
    if (wrapcol < 0)
        throw new ValueError(new str("Negative wrapcol"));
    if (wrapcol < 2)
        wrapcol = 2;
    return __binascii__::hexlify(s, new str("\n"), -(wrapcol / 2))->upper();
}

bytes *b16decode(bytes *s, __ss_bool casefold, bytes *ignorechars) {
    /* mirrors base64.py: without casefold, lowercase hex digits are only
    ** acceptable if they are in ignorechars (and are then dropped before
    ** unhexlify gets to see them) */
    if (!casefold) {
        bool has_ignore = ignorechars && !ignorechars->unit.empty();
        bool lower_seen = false;
        for (size_t i = 0; i < s->unit.size(); i++) {
            char c = s->unit[i];
            if (c >= 'a' && c <= 'f') {
                if (!has_ignore || ignorechars->unit.find(c) == std::string::npos)
                    throw new __binascii__::Error(new str("Non-base16 digit found"));
                lower_seen = true;
            }
        }
        if (has_ignore && lower_seen) {
            bytes *t = new bytes(1);
            t->unit.reserve(s->unit.size());
            for (size_t i = 0; i < s->unit.size(); i++) {
                char c = s->unit[i];
                if (!(c >= 'a' && c <= 'f'))
                    t->unit.push_back(c);
            }
            s = t;
        }
    }
    return __binascii__::unhexlify(s, ignorechars);
}

/* ---------------------------------------------------------------------
 * Base32 (RFC 4648)
 */

bytes *b32encode(bytes *s, __ss_bool padded, __ss_int wrapcol) {
    return __binascii__::b2a_base32(s, padded, 0, wrapcol);
}

static bytes *b32_prepare(bytes *s, __ss_bool casefold, bytes *map01) {
    // Handle RFC 4648 section 2.4 zero and one mapping: map01 is the
    // character to map the digit 1 (one) to, either 'L' (el) or 'I' (eye);
    // 0 (zero) is always mapped to 'O' (oh).
    if (map01) {
        if (map01->unit.size() != 1)
            throw new ValueError(new str("map01 must be a single character"));
        bytes *t = new bytes(s);
        for (size_t i = 0; i < t->unit.size(); i++) {
            if (t->unit[i] == '0')
                t->unit[i] = 'O';
            else if (t->unit[i] == '1')
                t->unit[i] = map01->unit[0];
        }
        s = t;
    }
    if (casefold)
        s = s->upper();
    return s;
}

bytes *b32decode(bytes *s, __ss_bool casefold, bytes *map01, __ss_bool padded, bytes *ignorechars, __ss_bool canonical) {
    s = b32_prepare(s, casefold, map01);
    return __binascii__::a2b_base32(s, padded, 0, ignorechars, canonical);
}

bytes *b32hexencode(bytes *s, __ss_bool padded, __ss_int wrapcol) {
    return __binascii__::b2a_base32(s, padded, __binascii__::BASE32HEX_ALPHABET, wrapcol);
}

bytes *b32hexdecode(bytes *s, __ss_bool casefold, __ss_bool padded, bytes *ignorechars, __ss_bool canonical) {
    // base32hex does not have the 01 mapping
    s = b32_prepare(s, casefold, 0);
    return __binascii__::a2b_base32(s, padded, __binascii__::BASE32HEX_ALPHABET, ignorechars, canonical);
}

/* ---------------------------------------------------------------------
 * Ascii85 / Base85 / Z85
 */

bytes *a85encode(bytes *b, __ss_bool foldspaces, __ss_int wrapcol, __ss_bool pad, __ss_bool adobe) {
    return __binascii__::b2a_ascii85(b, foldspaces, wrapcol, pad, adobe);
}

bytes *a85decode(bytes *b, __ss_bool foldspaces, __ss_bool adobe, bytes *ignorechars, __ss_bool canonical) {
    if (!ignorechars)
        ignorechars = new bytes(" \t\n\r\v");
    return __binascii__::a2b_ascii85(b, foldspaces, adobe, ignorechars, canonical);
}

bytes *b85encode(bytes *b, __ss_bool pad, __ss_int wrapcol) {
    return __binascii__::b2a_base85(b, 0, wrapcol, pad);
}

bytes *b85decode(bytes *b, bytes *ignorechars, __ss_bool canonical) {
    return __binascii__::a2b_base85(b, 0, ignorechars, canonical);
}

bytes *z85encode(bytes *s, __ss_bool pad, __ss_int wrapcol) {
    return __binascii__::b2a_base85(s, __binascii__::Z85_ALPHABET, wrapcol, pad);
}

bytes *z85decode(bytes *s, bytes *ignorechars, __ss_bool canonical) {
    return __binascii__::a2b_base85(s, __binascii__::Z85_ALPHABET, ignorechars, canonical);
}

/* ---------------------------------------------------------------------
 * Legacy interface (RFC 2045 line-wrapped base64)
 */

const __ss_int MAXLINESIZE = 76; // Excluding the CRLF
const __ss_int MAXBINSIZE = (MAXLINESIZE / 4) * 3;

bytes *encodebytes(bytes *s) {
    bytes *result = __binascii__::b2a_base64(s, True, MAXLINESIZE);
    if (result->unit == "\n")
        return new bytes();
    return result;
}

bytes *decodebytes(bytes *s) {
    return __binascii__::a2b_base64(s, False);
}

void *encode(file_binary *input, file_binary *output) {
    for (;;) {
        bytes *s = input->read(MAXBINSIZE);
        if (s->unit.empty())
            break;
        while ((__ss_int)s->unit.size() < MAXBINSIZE) {
            bytes *ns = input->read(MAXBINSIZE - (__ss_int)s->unit.size());
            if (ns->unit.empty())
                break;
            s = s->__add__(ns);
        }
        output->write(__binascii__::b2a_base64(s, True));
    }
    return NULL;
}

void *decode(file_binary *input, file_binary *output) {
    for (;;) {
        bytes *line = input->readline();
        if (line->unit.empty())
            break;
        output->write(__binascii__::a2b_base64(line, False));
    }
    return NULL;
}

void __init() {
    __name__ = new str("base64");

    default_4 = default_6 = default_7 = default_9 = default_10 = new bytes();
    default_8 = new bytes(" \t\n\r\v");
}

}
