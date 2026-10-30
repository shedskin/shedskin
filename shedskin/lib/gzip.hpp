/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __GZIP_HPP
#define __GZIP_HPP

#include "builtin.hpp"
#include "io.hpp"

struct mz_stream_s; /* see miniz/miniz.h (only included by gzip.cpp) */

using namespace __shedskin__;
namespace __gzip__ {

extern str *READ, *WRITE;
extern __ss_int FTEXT, FHCRC, FEXTRA, FNAME, FCOMMENT;

extern class_ *cl_BadGzipFile;
class BadGzipFile : public OSError {
public:
    BadGzipFile(str *msg=0) : OSError(msg) {
        __class__ = cl_BadGzipFile;
        /* plain message, like CPython's BadGzipFile('Not a gzipped file') */
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

class GzipFile : public file_binary {
public:
    __ss_int mtime; /* of the last member header read (0 before that, None in CPython) */

    file_binary *fileobj;
    bool myfileobj; /* opened (and so closed) by us */
    bool direct; /* fileobj is a plain binary file: use its FILE * directly */
    bool writing;
    mz_stream_s *strm;

    unsigned int crc; /* of the current member */
    unsigned long long stream_size;
    __ss_int pos; /* uncompressed position (offset in write mode) */
    __ss_int size; /* uncompressed size, once known (read mode) */

    __GC_BYTES inbuf; /* compressed data, not yet decompressed */
    size_t inpos;
    __GC_BYTES outbuf; /* decompressed data, not yet read (compressed data, not yet written) */
    size_t outpos;
    bool new_member, member_end, at_eof;

    GzipFile(str *filename=0, str *mode=0, __ss_int compresslevel=9, file_binary *fileobj=0) {
        __init(filename, mode, compresslevel, fileobj, 0, false);
    }
    /* mtime is __ss_void_struct when omitted by the caller (model default __void) */
    template<class V> GzipFile(str *filename, str *mode, __ss_int compresslevel, file_binary *fileobj, V mtime) {
        if constexpr (std::is_same_v<V, __ss_void_struct>)
            __init(filename, mode, compresslevel, fileobj, 0, false);
        else
            __init(filename, mode, compresslevel, fileobj, (__ss_int)mtime, true);
    }
    void __init(str *filename, str *mode, __ss_int compresslevel, file_binary *fileobj, __ss_int mtime, bool has_mtime);

    bytes *read(__ss_int n=-1);
    bytes *read1(__ss_int n=-1);
    bytes *peek(__ss_int n=0);
    bytes *readline(__ss_int n=-1);
    list<bytes *> *readlines(__ss_int hint=-1);
    __ss_int readinto(bytes *b);
    __ss_int readinto1(bytes *b) { return readinto(b); }
    __ss_int write(bytes *data);
    __ss_int seek(__ss_int i, __ss_int w=0);
    __ss_int tell();
    void *rewind();
    void *flush();
    void *close();
    GzipFile *__enter__() { return this; }
    __ss_int truncate(__ss_int size=-1);
    __ss_int __ss_fileno();
    __ss_bool isatty();

    __ss_bool readable() { return ___bool(!writing); }
    __ss_bool writable() { return ___bool(writing); }
    __ss_bool seekable() { return True; }

    bytes *__next__();
    bool __eof();
    bool __error() { return false; }

    /* byte access for _GzipTextFile */
    int __getc() {
        if (outpos == outbuf.size() && !__fill())
            return -1;
        pos++;
        return (unsigned char)outbuf[outpos++];
    }
    void __ungetc() { outpos--; pos--; }
    void __unget(const char *s, size_t k) { /* the last k bytes read, again */
        if (outpos < k) { /* (a __fill may have dropped them) */
            outbuf.insert(0, s, k - outpos);
            outpos = k;
        }
        outpos -= k;
        pos -= k;
    }
    bool __ensure(size_t n); /* at least n bytes in outbuf, unless at eof */

    /* internals */
    void __check_can_read(const char *method);
    bool __fill();
    bool __read_input();
    int __read_byte();
    void __read_exact(char *buf, size_t n);
    bool __read_header();
    void __read_trailer();
    void __deflate(const char *data, size_t n, int flush);
    void __write_raw(const char *data, size_t n);
    void __flush_raw();
    void __reset_reader();
    void __end();
};

class _GzipTextFile : public file {
public:
    GzipFile *gz;
    int nl; /* newline mode */
    bool bom_check; /* utf-8-sig: skip a leading bom on the first read */

    _GzipTextFile(GzipFile *gz, str *mode, str *encoding=0, str *errors=0, str *newline=0);

    str *read(__ss_int n=-1);
    str *readline(__ss_int n=-1);
    list<str *> *readlines(__ss_int hint=-1);
    __ss_int write(str *s);
    __ss_int seek(__ss_int i, __ss_int w=0);
    __ss_int tell();
    __ss_int truncate(__ss_int size=-1);
    void *flush();
    void *close();
    _GzipTextFile *__enter__() { return this; }
    __ss_int __ss_fileno();
    __ss_bool isatty();

    __ss_bool readable() { __check_closed(); return gz->readable(); }
    __ss_bool writable() { __check_closed(); return gz->writable(); }
    __ss_bool seekable() { __check_closed(); return False; }

    str *__next__();
    bool __eof();
    bool __error() { return false; }

    void __skip_bom();
    bool __take_lf();
};

/* filename can also be a binary file object (such as an io.BytesIO) */
GzipFile *open(str *filename, str *mode=0, __ss_int compresslevel=9, str *encoding=0, str *errors=0, str *newline=0);
GzipFile *open(bytes *filename, str *mode=0, __ss_int compresslevel=9, str *encoding=0, str *errors=0, str *newline=0);
GzipFile *open(file_binary *fileobj, str *mode=0, __ss_int compresslevel=9, str *encoding=0, str *errors=0, str *newline=0);

_GzipTextFile *open_text(str *filename, str *mode=0, __ss_int compresslevel=9, str *encoding=0, str *errors=0, str *newline=0);
_GzipTextFile *open_text(bytes *filename, str *mode=0, __ss_int compresslevel=9, str *encoding=0, str *errors=0, str *newline=0);
_GzipTextFile *open_text(file_binary *fileobj, str *mode=0, __ss_int compresslevel=9, str *encoding=0, str *errors=0, str *newline=0);

bytes *__compress(bytes *data, __ss_int compresslevel, __ss_int mtime, bool has_mtime);
/* mtime is __ss_void_struct when omitted by the caller (model default __void) */
template<class V> bytes *compress(bytes *data, __ss_int compresslevel, V mtime) {
    if constexpr (std::is_same_v<V, __ss_void_struct>)
        return __compress(data, compresslevel, 0, false);
    else
        return __compress(data, compresslevel, (__ss_int)mtime, true);
}
inline bytes *compress(bytes *data, __ss_int compresslevel=9) { return __compress(data, compresslevel, 0, false); }

bytes *decompress(bytes *data);

void __init();

} // module namespace
#endif
