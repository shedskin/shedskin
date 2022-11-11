/* Copyright 2005-2012 Mark Dufour and contributors; License Expat (See LICENSE) */

/* bytes methods */

inline __ss_int bytes::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    return unit[i];
}

inline __ss_int bytes::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    return unit[i];
}

inline __ss_int bytes::__len__() {
    return size();
}

inline bool bytes::for_in_has_next(size_t i) {
    return i < size(); /* XXX opt end cond */
}

inline __ss_int bytes::for_in_next(size_t &i) {
    return unit[i++];
}
