/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "base64.hpp"
#include "binascii.hpp"

namespace __base64__ {

str *__name__;

bytes *b64encode(bytes *s, bytes *altchars) {
    return __binascii__::b2a_base64(s, False, altchars);
}

bytes *standard_b64encode(bytes *s) {
    return b64encode(s, NULL);
}

bytes *urlsafe_b64encode(bytes *s) {
    return b64encode(s, new bytes("-_"));
}

bytes *b64decode(bytes *s, bytes *altchars, __ss_bool validate) {
    return __binascii__::a2b_base64(s, validate, altchars);
}

bytes *standard_b64decode(bytes *s) {
    return b64decode(s, NULL, False);
}

bytes *urlsafe_b64decode(bytes *s) {
    return b64decode(s, new bytes("-_"), False);
}

bytes *b16encode(bytes *s) {
    return __binascii__::hexlify(s)->upper();
}

bytes *b16decode(bytes *s, __ss_bool casefold) {
    bytes *t = casefold ? s->upper() : s;
    for (size_t i = 0; i < t->unit.size(); i++) {
        char c = t->unit[i];
        if (!((c >= '0' && c <= '9') || (c >= 'A' && c <= 'F')))
            throw new __binascii__::Error(new str("Non-base16 digit found"));
    }
    return __binascii__::unhexlify(t);
}

void __init() {
    __name__ = new str("base64");
}

}
