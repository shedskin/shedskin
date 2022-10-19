/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

/* unicode methods */

inline unicode *unicode::__getitem__(__ss_int i) {
    i = __wrap(this, i);

    unicode *u = new unicode();
    u->unit.resize(2);

    u->unit[0] = unit[2*i];
    u->unit[1] = unit[2*i+1];

    return u;
}

inline __ss_int unicode::__len__() {
    return size()/2;
}

