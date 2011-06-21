#include "cStringIO.hpp"

#include <algorithm>

namespace __cStringIO__ {

str* StringI::read(int n) {
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

str * StringI::readline(int n) {
    __check_closed();
    if(__eof())
        return new str("");
    size_t nl = s->unit.find('\n', pos);
    if(nl != std::string::npos) {
        int tbr = nl - pos + 1;
        return read(n < 0 ? tbr : std::min(tbr, n));
    } else {
        return read(n);
    }
}

void *StringI::seek(__ss_int i, __ss_int w) {
    __check_closed();
    if(w==0) pos = i;
    else if(w==1) pos += i;
    else pos = len(s)+i;
    return NULL;
}

void *StringI::write(str *data) {
    __check_closed();
    if(data) {
        const size_t size = data->unit.size();
        s->unit.insert(pos, data->unit);
        pos += size;
        s->unit.erase(pos, size);
    }
    return 0; 
}

StringI *StringIO(str *s) {
    return (new StringI(s));
}

void __init() {

}

} // module namespace

