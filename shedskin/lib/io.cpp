/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifdef _MSC_VER
#define NOMINMAX
#endif

#include "io.hpp"

#include <algorithm>

namespace __io__ {

bytes *default_0;
str *default_1;

/* BytesIO */

bytes *BytesIO::read(int n) {
    __check_closed();
    bytes *result;
    if(n < 0) {
        result = s->__slice__(1, pos, 0, 0);
        pos = len(s);
    } else {
        result = s->__slice__(3, pos, pos + n, 0);
        pos = std::min(pos + n, len(s));
    }
    return result;
}

bytes *BytesIO::readline(int n) {
    __check_closed();
    if(__eof())
        return new bytes("");
    size_t nl = s->unit.find('\n', (size_t)pos);
    if(nl != std::string::npos) {
        int tbr = (int)(nl - (size_t)pos + 1);
        return read(n < 0 ? tbr : std::min(tbr, n));
    } else {
        return read(n);
    }
}

void *BytesIO::seek(__ss_int i, __ss_int w) {
    __check_closed();
    if(w==0) pos = i;
    else if(w==1) pos += i;
    else pos = len(s)+i;
    return NULL;
}

void *BytesIO::write(bytes *data) {
    __check_closed();
    if(data) {
        const size_t size = data->unit.size();
        s->unit.insert((size_t)pos, data->unit);
        pos += (int)size;
        s->unit.erase((size_t)pos, size);
    }
    return 0;
}

bytes *BytesIO::getvalue() {
    return s;
};

/* StringIO */

str *StringIO::read(int n) {
    __check_closed();
    str *result;
    if(n < 0) {
        result = s->__slice__(1, pos, 0, 0);
        pos = len(s);
    } else {
        result = s->__slice__(3, pos, pos + n, 0);
        pos = std::min(pos + n, len(s));
    }
    return result;
}

str *StringIO::readline(int n) {
    __check_closed();
    if(__eof())
        return new str("");
    size_t nl = s->unit.find('\n', (size_t)pos);
    if(nl != std::string::npos) {
        int tbr = (int)(nl - (size_t)pos + 1);
        return read(n < 0 ? tbr : std::min(tbr, n));
    } else {
        return read(n);
    }
}

void *StringIO::seek(__ss_int i, __ss_int w) {
    __check_closed();
    if(w==0) pos = i;
    else if(w==1) pos += i;
    else pos = len(s)+i;
    return NULL;
}

void *StringIO::write(str *data) {
    __check_closed();
    if(data) {
        const size_t size = data->unit.size();
        s->unit.insert((size_t)pos, data->unit);
        pos += (int)size;
        s->unit.erase((size_t)pos, size);
    }
    return 0;
}

str *StringIO::getvalue() {
    return s;
};

/* init */

void __init() {
    default_0 = new bytes();
    default_1 = new str();

}

} // module namespace

