/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifdef _MSC_VER
#define NOMINMAX
#endif

#include "io.hpp"

#include <algorithm>

namespace __io__ {

class_ *cl_UnsupportedOperation;

const __ss_int DEFAULT_BUFFER_SIZE = 8192;
const __ss_int __ss_SEEK_SET = 0, __ss_SEEK_CUR = 1, __ss_SEEK_END = 2;

/* BytesIO */

bytes *BytesIO::read(__ss_int n) {
    __check_closed();
    __ss_int size = len(s);
    if(pos >= size) /* at or past the end: position stays put */
        return new bytes();
    bytes *result;
    if(n < 0) {
        result = s->__slice__(1, pos, 0, 0);
        pos = size;
    } else {
        result = s->__slice__(3, pos, pos + n, 0);
        pos = std::min(pos + n, size);
    }
    return result;
}

__ss_int BytesIO::readinto(bytes *b) {
    /* b must be a bytearray (array.array/memoryview are not supported) */
    if(b->frozen)
        throw new TypeError(new str("readinto() argument must be read-write bytes-like object, not bytes"));
    __check_closed();
    __ss_int size = len(s);
    if(pos >= size)
        return 0;
    size_t n = std::min(b->unit.size(), (size_t)(size - pos));
    b->unit.replace(0, n, s->unit, (size_t)pos, n);
    pos += (__ss_int)n;
    return (__ss_int)n;
}

bytes *BytesIO::readline(__ss_int n) {
    __check_closed();
    if(__eof())
        return new bytes();
    size_t nl = s->unit.find('\n', (size_t)pos);
    if(nl != std::string::npos) {
        __ss_int tbr = (__ss_int)(nl - (size_t)pos + 1);
        return read(n < 0 ? tbr : std::min(tbr, n));
    } else {
        return read(n);
    }
}

list<bytes *> *BytesIO::readlines(__ss_int hint) {
    /* lines end at '\n' only (unlike bytes.splitlines) */
    __check_closed();
    list<bytes *> *result = new list<bytes *>();
    __ss_int total = 0;
    while(!__eof()) {
        bytes *line = readline();
        result->append(line);
        total += len(line);
        if(hint > 0 && total > hint)
            break;
    }
    return result;
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
    else if(w==2) {
        pos = len(s)+i;
        if(pos < 0) pos = 0;
    }
    else
        throw new ValueError(__add(__add(new str("invalid whence ("), __str(w)), new str(", should be 0, 1 or 2)")));
    return pos;
}

__ss_int BytesIO::truncate(__ss_int size) {
    __check_closed();
    if(size == -1)
        size = pos;
    else if(size < 0)
        throw new ValueError(__add(new str("negative size value "), __str(size)));
    if((size_t)size < s->unit.size()) /* never grows the buffer */
        s->unit.resize((size_t)size);
    return size;
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
    __check_closed();
    return new bytes(s); /* copy: later writes must not change the result */
}

/* StringIO */

StringIO::StringIO(str *initial_value, str *newline) : file(), pos(0), s(new str()), universal(false), any_ending(false), line_buffering(False) {
    if(!newline) {
        universal = true;
        nl = __GC_STR(1, '\n');
    } else {
        const __GC_STR &n = newline->unit;
        if(n.empty())
            any_ending = true;
        else if(n.size() == 1 and (n[0] == '\n' or n[0] == '\r'))
            nl = n;
        else if(n.size() == 2 and n[0] == '\r' and n[1] == '\n')
            nl = n;
        else
            throw new ValueError(__add(new str("illegal newline value: "), repr(newline)));
    }
    if(initial_value)
        s->unit = __translate(initial_value);
}

__GC_STR StringIO::__translate(str *data) {
    const __GC_STR &u = data->unit;
    if(universal) { /* '\r\n' and lone '\r' -> '\n' */
        if(u.find('\r') == __GC_STR::npos)
            return u;
        __GC_STR r;
        r.reserve(u.size());
        for(size_t i = 0; i < u.size(); i++) {
            if(u[i] == '\r') {
                r.push_back('\n');
                if(i+1 < u.size() and u[i+1] == '\n')
                    i++;
            } else
                r.push_back(u[i]);
        }
        return r;
    }
    if(any_ending or (nl.size() == 1 and nl[0] == '\n') or u.find('\n') == __GC_STR::npos)
        return u;
    __GC_STR r; /* '\n' -> '\r' or '\r\n' */
    r.reserve(u.size());
    for(size_t i = 0; i < u.size(); i++) {
        if(u[i] == '\n')
            r.append(nl);
        else
            r.push_back(u[i]);
    }
    return r;
}

size_t StringIO::__line_end(size_t start) {
    /* index just past the line ending at or after start, or npos */
    const __GC_STR &u = s->unit;
    if(any_ending) {
        for(size_t i = start; i < u.size(); i++) {
            if(u[i] == '\n')
                return i+1;
            if(u[i] == '\r')
                return (i+1 < u.size() and u[i+1] == '\n') ? i+2 : i+1;
        }
        return __GC_STR::npos;
    }
    size_t i = u.find(nl, start);
    return i == __GC_STR::npos ? i : i + nl.size();
}

str *StringIO::read(__ss_int n) {
    __check_closed();
    __ss_int size = len(s);
    if(pos >= size) /* at or past the end: position stays put */
        return new str();
    str *result;
    if(n < 0) {
        result = s->__slice__(1, pos, 0, 0);
        pos = size;
    } else {
        result = s->__slice__(3, pos, pos + n, 0);
        pos = std::min(pos + n, size);
    }
    return result;
}

str *StringIO::readline(__ss_int n) {
    __check_closed();
    if(__eof())
        return new str();
    size_t end = __line_end((size_t)pos);
    if(end != std::string::npos) {
        __ss_int tbr = (__ss_int)(end - (size_t)pos);
        return read(n < 0 ? tbr : std::min(tbr, n));
    } else {
        return read(n);
    }
}

list<str *> *StringIO::readlines(__ss_int hint) {
    /* lines end according to newline (by default at '\n' only, unlike str.splitlines) */
    __check_closed();
    list<str *> *result = new list<str *>();
    __ss_int total = 0;
    while(!__eof()) {
        str *line = readline();
        result->append(line);
        total += len(line);
        if(hint > 0 && total > hint)
            break;
    }
    return result;
}

__ss_int StringIO::seek(__ss_int i, __ss_int w) {
    __check_closed();
    if(w==0) {
        if(i < 0)
            throw new ValueError(__add(new str("Negative seek position "), __str(i)));
        pos = i;
    }
    else if(w==1 || w==2) {
        if(i != 0) /* TODO OSError doesn't support a plain message yet */
            throw new OSError(new str("Can't do nonzero cur-relative seeks"));
        if(w==2)
            pos = len(s);
    }
    else
        throw new ValueError(__add(__add(new str("Invalid whence ("), __str(w)), new str(", should be 0, 1 or 2)")));
    return pos;
}

__ss_int StringIO::truncate(__ss_int size) {
    __check_closed();
    if(size == -1)
        size = pos;
    else if(size < 0)
        throw new ValueError(__add(new str("negative pos value "), __str(size)));
    if((size_t)size < s->unit.size()) /* never grows the buffer */
        s->unit.resize((size_t)size);
    return size;
}

__ss_int StringIO::write(str *data) {
    __check_closed();
    if(!data)
        throw new TypeError(new str("string argument expected, got 'NoneType'"));
    __GC_STR u = __translate(data);
    const size_t size = u.size();
    if((size_t)pos > s->unit.size())
        s->unit.resize((size_t)pos, '\0');
    s->unit.insert((size_t)pos, u);
    pos += (__ss_int)size;
    s->unit.erase((size_t)pos, size);
    return len(data); /* length before translation, like CPython */
}

str *StringIO::getvalue() {
    __check_closed();
    return new str(s->unit); /* copy: later writes must not change the result */
}

/* init */

str *text_encoding(str *encoding, __ss_int) {
    if (encoding)
        return encoding;
    return new str("utf-8");
}

void __init() {
    cl_UnsupportedOperation = new class_("UnsupportedOperation");

}

} // module namespace

