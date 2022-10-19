/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

/* unicode methods */

#include <iconv.h>

unicode::unicode() {
    __class__ = cl_unicode_;
}

unicode::unicode(const char *s) {
    __class__ = cl_unicode_;

    char *src = (char *)s;
    size_t srclen = strlen(src); // TODO ehm

    char buf[1024]; // TODO larger strings

    char *dest = (char *)buf;
    size_t destlen = 1024;

    iconv_t conv = iconv_open("UTF-16LE", "UTF-8"); // TODO detect default encoding?
    size_t value = iconv(conv, &src, &srclen, &dest, &destlen);

    // TODO check value == (size_t)-1

    unit.resize(dest-buf);
    memcpy((void *)(unit.data()), buf, dest-buf);

    iconv_close(conv);
}

str *unicode::encode(str *encoding) { // TODO check encoding
    __class__ = cl_unicode_;

    size_t srclen = unit.size();
    char *src = (char *)unit.data();

    char buf[1024];

    char *dest = (char *)buf;
    size_t destlen = 1024;

    iconv_t conv = iconv_open("UTF-8", "UTF-16LE");
    size_t value = iconv(conv, &src, &srclen, &dest, &destlen);

    str *s = new str();
    s->unit.resize(dest-buf);
    memcpy((void *)(s->unit.data()), buf, dest-buf);

    iconv_close(conv);

    return s;
}

const int unicode::size() const {
    return this->unit.size();
}

str *unicode::__str__() { // TODO see above
    return encode(new str("UTF-8"));
}

str *unicode::__repr__() {
    size_t nchars = unit.size()/2;

    str *s = new str("u'");
    s->unit.resize(2+6*nchars);

    for(int i=0; i<nchars; i++)
        sprintf(((char *)(s->unit.data()))+2+6*i, "\\u%02x%02x", (uint8_t)unit[2*i+1], (uint8_t)unit[2*i]);

    s->unit += '\'';

    return s;
}
