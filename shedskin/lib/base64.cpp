/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "base64.hpp"

namespace __base64__ {

str *__name__;


bytes *b64encode(bytes *s, bytes *altchars) {
    return NULL;
}

bytes *standard_b64encode(bytes *s) {
    return NULL;
}

bytes *urlsafe_b64encode(bytes *s) {
    return NULL;
}

bytes *b64decode(bytes *s, bytes *altchars, __ss_bool validate) {
    return NULL;
}

bytes *standard_b64decode(bytes *s) {
    return NULL;
}

bytes *urlsafe_b64decode(bytes *s) {
    return NULL;
}

void __init() {
    __name__ = new str("binascii");
}

}
