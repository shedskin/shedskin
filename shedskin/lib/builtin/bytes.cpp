/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* str methods */

bytes::bytes() : hash(-1) {
    __class__ = cl_bytes;
}

bytes::bytes(const char *s) : unit(s), hash(-1) {
    __class__ = cl_bytes;
}

bytes::bytes(__GC_STRING s) : unit(s), hash(-1) {
    __class__ = cl_bytes;
}

bytes::bytes(const char *s, int size) : unit(s, size), hash(-1) { /* '\0' delimiter in C */
    __class__ = cl_bytes;
}

const char *bytes::c_str() const {
    return this->unit.c_str();
}

const int bytes::size() const {
    return this->unit.size();
}

str *bytes::__str__() {
    return __add_strs(3, new str("b'"), new str(this->unit), new str("'"));
}

str *bytes::__repr__() {
    return this->__str__();
}
