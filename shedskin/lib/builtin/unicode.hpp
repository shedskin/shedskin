/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

/* unicode methods */

inline unicode *unicode::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    return this; // XXX
}

inline __ss_int unicode::__len__() {
    return size();
}

