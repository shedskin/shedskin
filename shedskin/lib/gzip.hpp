/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __GZIP_HPP
#define __GZIP_HPP

#include "builtin.hpp"
#include "io.hpp"

using namespace __shedskin__;
namespace __gzip__ {

extern str *__name__;
extern str *READ;

extern class_ *cl_BadGzipFile;
class BadGzipFile : public OSError {
public:
    BadGzipFile(str *msg=0) : OSError(msg) {
        __class__ = cl_BadGzipFile;
        /* a plain message, like CPython's BadGzipFile('CRC check failed') */
        this->__init__(msg);
        __ss_errno = 0;
        strerror = 0;
        filename = 0;
    }
    str *__str__() { return BaseException::__str__(); }
    str *__repr__() { return BaseException::__repr__(); }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_OSError; }
#endif
};

/* reading only: the whole file is decompressed when it is opened */
extern class_ *cl_GzipFile;
class GzipFile : public __io__::BytesIO {
public:
    GzipFile(str *filename=0, str *mode=0);

    __ss_int write(bytes *data);
    __ss_int truncate(__ss_int size=-1);
    __ss_bool writable() { __check_closed(); return False; }
    str *__repr__();
};

GzipFile *open(str *filename, str *mode=0);
bytes *decompress(bytes *data);

void __init();

} // module namespace
#endif
