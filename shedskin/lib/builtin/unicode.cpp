/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

/* unicode methods */

unicode::unicode() {
    __class__ = cl_unicode_;
}

unicode::unicode(const char *s) : unit(s) {
    __class__ = cl_unicode_;
}

str *unicode::encode(str *encoding) {
    __class__ = cl_unicode_;

    return new str("test");
}

const int unicode::size() const {
    return this->unit.size();
}
