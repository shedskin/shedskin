/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifdef _MSC_VER
#define NOMINMAX
#endif

#include "io.hpp"

#include <algorithm>

namespace __io__ {

const __ss_int DEFAULT_BUFFER_SIZE = 8192;
const __ss_int __ss_SEEK_SET = 0, __ss_SEEK_CUR = 1, __ss_SEEK_END = 2;

/* BytesIO */

bytes *BytesIO::read(__ss_int n) {
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

bytes *BytesIO::readline(__ss_int n) {
    __check_closed();
    if(__eof())
        return new bytes("");
    size_t nl = s->unit.find('\n', (size_t)pos);
    if(nl != std::string::npos) {
        __ss_int tbr = (__ss_int)(nl - (size_t)pos + 1);
        return read(n < 0 ? tbr : std::min(tbr, n));
    } else {
        return read(n);
    }
}

list<bytes *> *BytesIO::readlines(__ss_int hint) {
    bytes *rest = s->__slice__(1, pos, 0, 0);
    pos = len(s);
    return rest->splitlines(True);
}

__ss_int BytesIO::seek(__ss_int i, __ss_int w) {
    __check_closed();
    if(w==0) {
        if(i < 0)
            throw new ValueError(__add(new str("negative seek value "), __str(i)));
        pos = i;
    }
    else if(w==1) {
        pos += i;
        if(pos < 0) pos = 0;
    }
    else {
        pos = len(s)+i;
        if(pos < 0) pos = 0;
    }
    return pos; 
}

__ss_int BytesIO::write(bytes *data) {
    __check_closed();
    if(!data)
        throw new TypeError(new str("a bytes-like object is required, not 'NoneType'"));
    const size_t size = data->unit.size();
    if((size_t)pos > s->unit.size())
        s->unit.resize((size_t)pos, '\0');
    s->unit.insert((size_t)pos, data->unit);
    pos += (__ss_int)size;
    s->unit.erase((size_t)pos, size);
    return (__ss_int)size;
}

bytes *BytesIO::getvalue() {
    return s;
};

/* StringIO */

str *StringIO::read(__ss_int n) {
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

str *StringIO::readline(__ss_int n) {
    __check_closed();
    if(__eof())
        return new str("");
    size_t nl = s->unit.find('\n', (size_t)pos);
    if(nl != std::string::npos) {
        __ss_int tbr = (__ss_int)(nl - (size_t)pos + 1);
        return read(n < 0 ? tbr : std::min(tbr, n));
    } else {
        return read(n);
    }
}

list<str *> *StringIO::readlines(__ss_int hint) {
    str *rest = s->__slice__(1, pos, 0, 0);
    pos = len(s);
    return rest->splitlines(True);
}

__ss_int StringIO::seek(__ss_int i, __ss_int w) {
    __check_closed();
    if(w==0) {
        if(i < 0)
            throw new ValueError(__add(new str("Negative seek position "), __str(i)));
        pos = i;
    }
    else if(w==1) {
        pos += i;
        if(pos < 0) pos = 0;
    }
    else {
        pos = len(s)+i;
        if(pos < 0) pos = 0;
    }
    return pos;
}

__ss_int StringIO::write(str *data) {
    __check_closed();
    if(!data)
        throw new TypeError(new str("string argument expected, got 'NoneType'"));
    const size_t size = data->unit.size();
    if((size_t)pos > s->unit.size())
        s->unit.resize((size_t)pos, '\0');
    s->unit.insert((size_t)pos, data->unit);
    pos += (__ss_int)size;
    s->unit.erase((size_t)pos, size);
    return (__ss_int)size;
}

str *StringIO::getvalue() {
    return s;
};

/* init */

void __init() {

}

} // module namespace

