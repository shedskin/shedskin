/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifdef _MSC_VER
#define NOMINMAX
#endif

#include "io.hpp"

#include <algorithm>

namespace __io__ {

bytes *default_0;

bytes* BytesI::read(int n) {
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

bytes * BytesI::readline(int n) {
    __check_closed();
    if(__eof())
        return new bytes("");
    size_t nl = s->unit.find('\n', pos);
    if(nl != std::string::npos) {
        int tbr = nl - pos + 1;
        return read(n < 0 ? tbr : std::min(tbr, n));
    } else {
        return read(n);
    }
}

void *BytesI::seek(__ss_int i, __ss_int w) {
    __check_closed();
    if(w==0) pos = i;
    else if(w==1) pos += i;
    else pos = len(s)+i;
    return NULL;
}

void *BytesI::write(bytes *data) {
    __check_closed();
    if(data) {
        const size_t size = data->size();
        s->unit.insert(pos, data->unit);
        pos += size;
        s->unit.erase(pos, size);
    }
    return 0; 
}

BytesI *BytesIO(bytes *s) {
    return (new BytesI(s));
}

void __init() {
    default_0 = new bytes();

}

} // module namespace

