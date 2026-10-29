/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

/* deflate/inflate: the vendored miniz library (see miniz/README.md), compiled
   as part of this file. only its (mz_-prefixed) zlib-style stream api is used.
   included first, so its C code sees no shedskin names (except for Python.h,
   which must precede any system header) */
#ifdef __SS_BIND
#include <Python.h>
#endif
#define MINIZ_NO_STDIO
#define MINIZ_NO_TIME
#define MINIZ_NO_ARCHIVE_APIS
#define MINIZ_NO_ZLIB_COMPATIBLE_NAMES
#include "miniz/miniz.c"

#include "gzip.hpp"

#include <cstdlib>
#include <ctime>
#include <typeinfo>

namespace __gzip__ {

str *READ, *WRITE;
__ss_int FTEXT, FHCRC, FEXTRA, FNAME, FCOMMENT;

class_ *cl_BadGzipFile;

static const size_t READ_BUFFER_SIZE = 128 * 1024;
static const size_t CHUNK_SIZE = 64 * 1024;
static const unsigned int MAX_AVAIL = 1u << 30; /* avail_in/avail_out are 32-bit */

/* miniz state (about 300KB for deflate) on the gc heap, so an unclosed file
   does not leak it. it only points to buffers we keep alive ourselves */
static void *__mz_alloc(void *, size_t items, size_t size) {
#ifdef __SS_NOGC
    return std::malloc(items * size);
#else
    return GC_MALLOC_ATOMIC(items * size);
#endif
}

static void __mz_free(void *, void *address) {
#ifdef __SS_NOGC
    std::free(address);
#else
    GC_FREE(address);
#endif
}

static mz_stream *__new_stream() {
#ifdef __SS_NOGC
    mz_stream *strm = (mz_stream *)std::calloc(1, sizeof(mz_stream));
#else
    mz_stream *strm = (mz_stream *)GC_MALLOC(sizeof(mz_stream)); /* zeroed, scanned (->state) */
#endif
    if (!strm)
        throw new MemoryError();
    strm->zalloc = __mz_alloc;
    strm->zfree = __mz_free;
    return strm;
}

static void __check_level(__ss_int compresslevel) {
    if (compresslevel < -1 || compresslevel > 9) /* (miniz also has a level 10) */
        throw new ValueError(new str("Bad compression level"));
}

static void __deflate_init(mz_stream *strm, __ss_int compresslevel) {
    __check_level(compresslevel);
    if (mz_deflateInit2(strm, (int)compresslevel, MZ_DEFLATED, -MZ_DEFAULT_WINDOW_BITS, 9, MZ_DEFAULT_STRATEGY) != MZ_OK)
        throw new MemoryError();
}

static void __inflate_init(mz_stream *strm) {
    if (mz_inflateInit2(strm, -MZ_DEFAULT_WINDOW_BITS) != MZ_OK)
        throw new MemoryError();
}

static unsigned int __crc32(unsigned int crc, const char *data, size_t n) {
    return (unsigned int)mz_crc32(crc, (const unsigned char *)data, n);
}

static void __put32(__GC_BYTES &out, unsigned long long x) {
    for (int i = 0; i < 4; i++)
        out.push_back((char)((x >> (8 * i)) & 0xff));
}

static unsigned int __get32(const char *p) {
    unsigned int x = 0;
    for (int i = 3; i >= 0; i--)
        x = (x << 8) | (unsigned char)p[i];
    return x;
}

static str *__hex32(unsigned int x) {
    char buf[16];
    snprintf(buf, sizeof(buf), "0x%x", x);
    return new str(buf);
}

static EOFError *__eof_error() {
    return new EOFError(new str("Compressed file ended before the end-of-stream marker was reached"));
}

static BadGzipFile *__data_error() {
    /* (CPython raises zlib.error here) */
    return new BadGzipFile(new str("Error -3 while decompressing data"));
}

static OSError *__ebadf(str *msg) {
    OSError *e = new OSError();
    e->__init_errno(EBADF, 0);
    e->strerror = msg;
    e->message = e->__str__();
    return e;
}

/* deflate n bytes (and/or flush) into out. as with zlib, a flush is repeated
   while it fills the output chunk; an empty flush (a few bytes) never does */
static void __deflate_into(mz_stream *strm, __GC_BYTES &out, const char *data, size_t n, int flush) {
    for (;;) {
        size_t now = std::min(n, (size_t)MAX_AVAIL);
        strm->next_in = (const unsigned char *)data;
        strm->avail_in = (unsigned int)now;
        bool last = (now == n);
        int f = last ? flush : MZ_NO_FLUSH;
        for (;;) {
            size_t old = out.size();
            out.resize(old + CHUNK_SIZE);
            strm->next_out = (unsigned char *)&out[old];
            strm->avail_out = (unsigned int)CHUNK_SIZE;
            int status = mz_deflate(strm, f);
            out.resize(old + CHUNK_SIZE - strm->avail_out);
            if (status == MZ_STREAM_END)
                break;
            if (status == MZ_BUF_ERROR) /* nothing (more) to do */
                break;
            if (status != MZ_OK)
                throw new ValueError(new str("Error while compressing data"));
            if (f != MZ_FINISH && strm->avail_in == 0 && strm->avail_out != 0)
                break;
        }
        data += now;
        n -= now;
        if (last)
            break;
    }
}

/* gzip member header (RFC 1952): returns false when there is no (more)
   data, or throws. next() returns the next byte, or -1 at the end */
template<class R> static bool __read_gzip_header(R &next, __ss_int &mtime) {
    int c1 = next();
    if (c1 == -1)
        return false;
    int c2 = next();
    if (c1 != 0x1f || c2 != 0x8b) {
        __GC_BYTES magic(1, (char)c1);
        if (c2 != -1)
            magic.push_back((char)c2);
        throw new BadGzipFile(__add_strs(3, new str("Not a gzipped file ("), repr(new bytes(magic)), new str(")")));
    }
    char header[8];
    for (int i = 0; i < 8; i++) {
        int c = next();
        if (c == -1)
            throw __eof_error();
        header[i] = (char)c;
    }
    if ((unsigned char)header[0] != 8)
        throw new BadGzipFile(new str("Unknown compression method"));
    int flag = (unsigned char)header[1];
    mtime = (__ss_int)__get32(header + 2);
    if (flag & 4) { /* FEXTRA */
        int lo = next(), hi = next();
        if (lo == -1 || hi == -1)
            throw __eof_error();
        for (int i = 0; i < (lo | (hi << 8)); i++)
            if (next() == -1)
                throw __eof_error();
    }
    if (flag & 8) /* FNAME */
        for (int c = next(); c != -1 && c != 0; c = next()) ;
    if (flag & 16) /* FCOMMENT */
        for (int c = next(); c != -1 && c != 0; c = next()) ;
    if (flag & 2) /* FHCRC */
        if (next() == -1 || next() == -1)
            throw __eof_error();
    return true;
}

/* basename of the file name, as stored in the header: latin-1, or none */
static __GC_BYTES __header_name(str *name) {
    __GC_BYTES fname;
    if (!name)
        return fname;
    const __GC_STR &u = name->unit;
    size_t start = 0;
    for (size_t i = 0; i < u.size(); i++) {
#ifdef WIN32
        if (u[i] == '/' || u[i] == '\\' || u[i] == ':')
#else
        if (u[i] == '/')
#endif
            start = i + 1;
    }
    for (size_t i = start; i < u.size(); i++) {
        if (u[i] > 0xff)
            return __GC_BYTES();
        fname.push_back((char)u[i]);
    }
    if (fname.size() >= 3 && fname.compare(fname.size() - 3, 3, ".gz") == 0)
        fname.resize(fname.size() - 3);
    return fname;
}

/* write-mode files that are not closed explicitly are finished at exit,
   as CPython does when they are finalized */
static list<GzipFile *> *__writers;

static void __close_writers() {
    while (__writers && len(__writers)) {
        GzipFile *gz = __writers->pop();
        try {
            gz->close();
        } catch (BaseException *) {
        }
    }
}

static void __register_writer(GzipFile *gz) {
    if (!__writers) {
        __writers = new list<GzipFile *>();
        std::atexit(__close_writers);
    }
    __writers->append(gz);
}

static void __unregister_writer(GzipFile *gz) {
    if (__writers)
        for (__ss_int i = 0; i < len(__writers); i++)
            if (__writers->units[i] == gz) {
                __writers->units.erase(__writers->units.begin() + i);
                break;
            }
}

/* GzipFile */

void GzipFile::__init(str *filename, str *mode, __ss_int compresslevel, file_binary *fileobj, __ss_int mtime, bool has_mtime) {
    this->mtime = 0;
    this->fileobj = 0;
    myfileobj = direct = writing = false;
    strm = 0;
    crc = 0;
    stream_size = 0;
    pos = 0;
    size = -1;
    inpos = outpos = 0;
    new_member = true;
    member_end = at_eof = false;
    f = 0;
    closed = False;

    if (mode && (mode->unit.find('t') != __GC_STR::npos || mode->unit.find('U') != __GC_STR::npos))
        throw new ValueError(__add_strs(2, new str("Invalid mode: "), repr(mode)));
    /* like cpython, an empty mode is falsy: no 'b' is added, the file is
       opened as 'rb', and the mode check below then rejects the mode */
    if (mode && mode->unit.size() && mode->unit.find('b') == __GC_STR::npos)
        mode = __add_strs(2, mode, new str("b"));

    str *origmode = mode;
    if (!fileobj) {
        if (!filename)
            throw new TypeError(new str("expected str, bytes or os.PathLike object, not NoneType"));
        fileobj = new file_binary(filename, (mode && mode->unit.size()) ? mode : new str("rb"));
        myfileobj = true;
    }
    if (!filename)
        filename = fileobj->name ? fileobj->name : new str("");
    if (!mode)
        mode = fileobj->mode ? fileobj->mode : new str("rb");

    if (mode->unit.size() && mode->unit[0] == 'r') {
        this->mode = READ;
    } else if (mode->unit.size() && (mode->unit[0] == 'w' || mode->unit[0] == 'a' || mode->unit[0] == 'x')) {
        this->mode = WRITE;
        writing = true;
    } else {
        if (myfileobj)
            fileobj->close();
        throw new ValueError(__add_strs(2, new str("Invalid mode: "), repr(origmode ? origmode : mode)));
    }
    name = filename;
    this->fileobj = fileobj;
    direct = fileobj->f && typeid(*fileobj) == typeid(file_binary);

    strm = __new_stream();
    try {
        if (writing) {
            __deflate_init(strm, compresslevel);
            __GC_BYTES fname = __header_name(name);
            outbuf += "\x1f\x8b\x08";
            outbuf.push_back(fname.empty() ? '\0' : '\x08'); /* FNAME */
            __put32(outbuf, has_mtime ? (unsigned long long)mtime : (unsigned long long)::time(NULL));
            outbuf.push_back(compresslevel == 9 ? '\x02' : (compresslevel == 1 ? '\x04' : '\0'));
            outbuf.push_back('\xff');
            if (!fname.empty()) {
                outbuf += fname;
                outbuf.push_back('\0');
            }
            __flush_raw();
            __register_writer(this);
        } else
            __inflate_init(strm);
    } catch (BaseException *) {
        if (myfileobj)
            fileobj->close();
        this->fileobj = 0;
        closed = True;
        throw;
    }
}

void GzipFile::__check_can_read(const char *method) {
    __check_closed();
    if (writing) {
        throw __ebadf(__add_strs(2, new str(method), new str("() on write-only GzipFile object")));
    }
}

/* read more compressed data into inbuf; false at the end of fileobj */
bool GzipFile::__read_input() {
    if (inpos == inbuf.size()) {
        inbuf.clear();
        inpos = 0;
    }
    size_t old = inbuf.size();
    if (direct) {
        inbuf.resize(old + READ_BUFFER_SIZE);
        size_t n = fread(&inbuf[old], 1, READ_BUFFER_SIZE, fileobj->f);
        inbuf.resize(old + n);
        if (n == 0 && ferror(fileobj->f))
            __throw_oserror();
    } else {
        bytes *b = fileobj->read((__ss_int)READ_BUFFER_SIZE);
        inbuf += b->unit;
    }
    return inbuf.size() > old;
}

int GzipFile::__read_byte() {
    if (inpos == inbuf.size() && !__read_input())
        return -1;
    return (unsigned char)inbuf[inpos++];
}

void GzipFile::__read_exact(char *buf, size_t n) {
    for (size_t i = 0; i < n; i++) {
        int c = __read_byte();
        if (c == -1)
            throw __eof_error();
        buf[i] = (char)c;
    }
}

bool GzipFile::__read_header() {
    auto next = [this]() { return __read_byte(); };
    return __read_gzip_header(next, mtime);
}

void GzipFile::__read_trailer() {
    char trailer[8];
    __read_exact(trailer, 8);
    unsigned int stored_crc = __get32(trailer), isize = __get32(trailer + 4);
    if (stored_crc != crc)
        throw new BadGzipFile(__add_strs(4, new str("CRC check failed "), __hex32(stored_crc), new str(" != "), __hex32(crc)));
    if (isize != (unsigned int)(stream_size & 0xffffffff))
        throw new BadGzipFile(new str("Incorrect length of data produced"));
    /* gzip files can be padded with zeroes */
    int c;
    do
        c = __read_byte();
    while (c == 0);
    if (c != -1)
        inpos--;
}

/* decompress some more data into outbuf; false at the end of the last member */
bool GzipFile::__fill() {
    if (at_eof)
        return false;
    if (outpos == outbuf.size()) {
        outbuf.clear();
        outpos = 0;
    } else if (outpos >= CHUNK_SIZE) {
        outbuf.erase(0, outpos);
        outpos = 0;
    }
    for (;;) {
        if (member_end) {
            __read_trailer();
            member_end = false;
            new_member = true;
            mz_inflateReset(strm);
        }
        if (new_member) {
            crc = 0;
            stream_size = 0;
            if (!__read_header()) {
                at_eof = true;
                size = pos + (__ss_int)(outbuf.size() - outpos);
                return false;
            }
            new_member = false;
        }
        size_t avail = inbuf.size() - inpos;
        size_t old = outbuf.size();
        outbuf.resize(old + CHUNK_SIZE);
        strm->next_in = (const unsigned char *)inbuf.data() + inpos;
        strm->avail_in = (unsigned int)std::min(avail, (size_t)MAX_AVAIL);
        strm->next_out = (unsigned char *)&outbuf[old];
        strm->avail_out = (unsigned int)CHUNK_SIZE;
        int status = mz_inflate(strm, MZ_NO_FLUSH);
        size_t produced = CHUNK_SIZE - strm->avail_out;
        inpos = (const char *)strm->next_in - inbuf.data();
        outbuf.resize(old + produced);
        if (produced) {
            crc = __crc32(crc, &outbuf[old], produced);
            stream_size += produced;
        }
        if (status == MZ_STREAM_END)
            member_end = true;
        else if (status != MZ_OK && status != MZ_BUF_ERROR)
            throw __data_error();
        else if (produced == 0 && inpos == inbuf.size() && !__read_input())
            throw __eof_error();
        if (produced)
            return true;
    }
}

bool GzipFile::__ensure(size_t n) {
    if (outpos > 0 && outbuf.size() - outpos < n) { /* contiguous */
        outbuf.erase(0, outpos);
        outpos = 0;
    }
    while (outbuf.size() - outpos < n)
        if (!__fill())
            return false;
    return true;
}

bool GzipFile::__eof() {
    return writing || (outpos == outbuf.size() && !__fill());
}

bytes *GzipFile::read(__ss_int n) {
    __check_can_read("read");
    if (n < -1)
        throw new ValueError(new str("read length must be non-negative or -1"));
    if (n < 0) {
        while (__fill()) ;
    } else
        while (outbuf.size() - outpos < (size_t)n && __fill()) ;
    size_t avail = outbuf.size() - outpos;
    size_t k = (n < 0) ? avail : std::min(avail, (size_t)n);
    bytes *b = new bytes(outbuf.data() + outpos, k);
    outpos += k;
    pos += (__ss_int)k;
    return b;
}

bytes *GzipFile::read1(__ss_int n) {
    __check_can_read("read1");
    if (n < 0)
        n = __io__::DEFAULT_BUFFER_SIZE;
    if (n > 0 && outpos == outbuf.size())
        __fill();
    size_t k = std::min(outbuf.size() - outpos, (size_t)n);
    bytes *b = new bytes(outbuf.data() + outpos, k);
    outpos += k;
    pos += (__ss_int)k;
    return b;
}

bytes *GzipFile::peek(__ss_int) {
    __check_can_read("peek");
    if (outpos == outbuf.size())
        __fill();
    return new bytes(outbuf.data() + outpos, outbuf.size() - outpos);
}

__ss_int GzipFile::readinto(bytes *b) {
    /* b must be a bytearray (array.array/memoryview are not supported) */
    if (b->frozen)
        throw new TypeError(new str("readinto() argument must be read-write bytes-like object, not bytes"));
    bytes *data = read((__ss_int)b->unit.size());
    size_t n = data->unit.size();
    b->unit.replace(0, n, data->unit);
    return (__ss_int)n;
}

bytes *GzipFile::readline(__ss_int n) {
    __check_closed();
    if (writing)
        throw new __io__::UnsupportedOperation(new str("read"));
    size_t searched = 0; /* (relative to outpos, as __fill may compact) */
    for (;;) {
        size_t avail = outbuf.size() - outpos;
        size_t nl = outbuf.find('\n', outpos + searched);
        size_t k = 0;
        if (nl != __GC_BYTES::npos)
            k = nl - outpos + 1;
        else if (n >= 0 && avail >= (size_t)n)
            k = avail;
        if (k) {
            if (n >= 0)
                k = std::min(k, (size_t)n);
            bytes *b = new bytes(outbuf.data() + outpos, k);
            outpos += k;
            pos += (__ss_int)k;
            return b;
        }
        if (n == 0)
            return new bytes();
        if (!__fill()) { /* last line */
            bytes *b = new bytes(outbuf.data() + outpos, avail);
            outpos += avail;
            pos += (__ss_int)avail;
            return b;
        }
        searched = avail;
    }
}

list<bytes *> *GzipFile::readlines(__ss_int hint) {
    list<bytes *> *result = new list<bytes *>();
    __ss_int total = 0;
    for (;;) {
        bytes *line = readline();
        if (line->unit.empty())
            break;
        result->append(line);
        total += len(line);
        if (hint > 0 && total > hint)
            break;
    }
    return result;
}

bytes *GzipFile::__next__() {
    bytes *line = readline();
    if (line->unit.empty())
        throw new StopIteration();
    return line;
}

__ss_int GzipFile::write(bytes *data) {
    __check_closed();
    if (!writing)
        throw __ebadf(new str("write() on read-only GzipFile object"));
    size_t n = data->unit.size();
    if (n) {
        __deflate_into(strm, outbuf, data->unit.data(), n, MZ_NO_FLUSH);
        crc = __crc32(crc, data->unit.data(), n);
        stream_size += n;
        pos += (__ss_int)n;
        if (outbuf.size() >= READ_BUFFER_SIZE)
            __flush_raw();
    }
    return (__ss_int)n;
}

/* write the pending compressed data to fileobj */
void GzipFile::__flush_raw() {
    if (outbuf.empty())
        return;
    if (direct) {
        if (fwrite(outbuf.data(), 1, outbuf.size(), fileobj->f) != outbuf.size())
            __throw_oserror();
    } else
        fileobj->write(new bytes(outbuf.data(), outbuf.size()));
    outbuf.clear();
}

void *GzipFile::flush() {
    __check_closed();
    if (writing) {
        __deflate_into(strm, outbuf, 0, 0, MZ_SYNC_FLUSH);
        __flush_raw();
        fileobj->flush();
    }
    return NULL;
}

void GzipFile::__end() {
    if (strm) {
        if (writing)
            mz_deflateEnd(strm);
        else
            mz_inflateEnd(strm);
        strm = 0;
    }
}

void *GzipFile::close() {
    if (!fileobj)
        return NULL;
    file_binary *fo = fileobj;
    try {
        if (writing) {
            __unregister_writer(this);
            __deflate_into(strm, outbuf, 0, 0, MZ_FINISH);
            __put32(outbuf, crc);
            __put32(outbuf, stream_size & 0xffffffff);
            __flush_raw();
        }
    } catch (BaseException *) {
        __end();
        fileobj = 0;
        closed = True;
        if (myfileobj)
            fo->close();
        throw;
    }
    __end();
    fileobj = 0;
    closed = True;
    if (myfileobj)
        fo->close();
    return NULL;
}

void GzipFile::__reset_reader() {
    fileobj->seek(0);
    inbuf.clear();
    inpos = 0;
    outbuf.clear();
    outpos = 0;
    pos = 0;
    new_member = true;
    member_end = at_eof = false;
    mz_inflateReset(strm);
}

void *GzipFile::rewind() {
    if (writing)
        throw new OSError(new str("Can't rewind in write mode"));
    __check_closed();
    __reset_reader();
    return NULL;
}

__ss_int GzipFile::seek(__ss_int offset, __ss_int whence) {
    __check_closed();
    if (writing) {
        if (whence == 1)
            offset = pos + offset;
        else if (whence != 0)
            throw new ValueError(new str("Seek from end not supported"));
        if (offset < pos)
            throw new OSError(new str("Negative seek in write mode"));
        __GC_BYTES zeros(std::min((size_t)(offset - pos), CHUNK_SIZE), '\0');
        while (pos < offset) {
            size_t k = std::min((size_t)(offset - pos), zeros.size());
            write(new bytes(zeros.data(), k));
        }
        return pos;
    }
    if (whence == 1)
        offset = pos + offset;
    else if (whence == 2) {
        while (__fill()) ; /* to learn the size */
        offset = size + offset;
    } else if (whence != 0)
        throw new ValueError(__add_strs(2, new str("Invalid value for whence: "), __str(whence)));
    if (offset < pos)
        __reset_reader();
    while (pos < offset) {
        if (outpos == outbuf.size() && !__fill())
            break;
        size_t k = std::min(outbuf.size() - outpos, (size_t)(offset - pos));
        outpos += k;
        pos += (__ss_int)k;
    }
    return pos;
}

__ss_int GzipFile::tell() {
    __check_closed();
    return pos;
}

__ss_int GzipFile::truncate(__ss_int) {
    __check_closed();
    throw new __io__::UnsupportedOperation(new str("truncate"));
}

__ss_int GzipFile::__ss_fileno() {
    __check_closed();
    return fileobj->__ss_fileno();
}

__ss_bool GzipFile::isatty() {
    if (closed)
        throw new ValueError(new str("I/O operation on closed file."));
    return False;
}

/* _GzipTextFile: newline handling as io.TextIOWrapper */

enum { NL_UNIVERSAL, NL_ANY, NL_LF, NL_CR, NL_CRLF };

_GzipTextFile::_GzipTextFile(GzipFile *gz, str *mode, str *encoding, str *errors, str *newline) : file() {
    __encoding = __lookup_encoding(encoding);
    __errors = __lookup_errors(errors);
    this->encoding = encoding ? encoding : new str("utf-8");
    this->errors = errors ? errors : new str("strict");

    nl = NL_UNIVERSAL;
    if (newline) {
        const __GC_STR &n = newline->unit;
        if (n.empty())
            nl = NL_ANY;
        else if (n == U"\n")
            nl = NL_LF;
        else if (n == U"\r")
            nl = NL_CR;
        else if (n == U"\r\n")
            nl = NL_CRLF;
        else
            throw new ValueError(__add_strs(2, new str("illegal newline value: "), newline));
    }

    bom_check = false;
    if (__encoding == __SS_ENC_UTF8_SIG) {
        __encoding = __SS_ENC_UTF8;
        if (gz->writing)
            __bom_pending = true;
        else
            bom_check = true;
    }

    this->gz = gz;
    buffer = gz;
    name = gz->name;
    this->mode = mode;
}

void _GzipTextFile::__skip_bom() {
    bom_check = false;
    if (gz->__ensure(3) && gz->outbuf.compare(gz->outpos, 3, "\xef\xbb\xbf") == 0) {
        gz->outpos += 3;
        gz->pos += 3;
    }
}

str *_GzipTextFile::readline(__ss_int n) {
    __check_closed();
    if (gz->writing)
        throw new __io__::UnsupportedOperation(new str("not readable"));
    if (bom_check)
        __skip_bom();
    __read_cache.clear();
    __char_counter cc(__encoding, __errors);
    for (;;) {
        int c = gz->__getc();
        if (c == -1)
            break;
        if (cc.full(c, size_t(n))) { /* character n+1 starts: not ours */
            gz->__ungetc();
            break;
        }
        if (c == '\r' && nl != NL_LF) {
            if (nl == NL_CR) {
                __read_cache.push_back('\r');
                break;
            }
            int d = gz->__getc();
            bool crlf = (d == '\n');
            if (!crlf && d != -1)
                gz->__ungetc();
            if (nl == NL_UNIVERSAL) { /* '\r' and '\r\n' become '\n' */
                __read_cache.push_back('\n');
                break;
            }
            __read_cache.push_back('\r');
            if (crlf) {
                if (cc.chars < size_t(n)) {
                    __read_cache.push_back('\n');
                    cc.chars++;
                } else
                    gz->__ungetc();
                break;
            }
            if (nl == NL_ANY) /* (NL_CRLF: a lone '\r' does not end the line) */
                break;
            continue;
        }
        __read_cache.push_back((char)c);
        if (c == '\n' && nl != NL_CR && nl != NL_CRLF)
            break;
    }
    return __decode_cache();
}

str *_GzipTextFile::read(__ss_int n) {
    __check_closed();
    if (gz->writing)
        throw new __io__::UnsupportedOperation(new str("not readable"));
    if (bom_check)
        __skip_bom();
    __read_cache.clear();
    __char_counter cc(__encoding, __errors);
    for (;;) {
        int c = gz->__getc();
        if (c == -1)
            break;
        if (cc.full(c, size_t(n))) {
            gz->__ungetc();
            break;
        }
        if (c == '\r' && nl == NL_UNIVERSAL) { /* '\r' and '\r\n' become '\n' */
            int d = gz->__getc();
            if (d != '\n' && d != -1)
                gz->__ungetc();
            c = '\n';
        }
        __read_cache.push_back((char)c);
    }
    return __decode_cache();
}

list<str *> *_GzipTextFile::readlines(__ss_int hint) {
    list<str *> *result = new list<str *>();
    __ss_int total = 0;
    for (;;) {
        str *line = readline();
        if (line->unit.empty())
            break;
        result->append(line);
        total += len(line);
        if (hint > 0 && total > hint)
            break;
    }
    return result;
}

str *_GzipTextFile::__next__() {
    str *line = readline();
    if (line->unit.empty())
        throw new StopIteration();
    return line;
}

bool _GzipTextFile::__eof() {
    return gz->__eof();
}

__ss_int _GzipTextFile::write(str *s) {
    __check_closed();
    if (!gz->writing)
        throw new __io__::UnsupportedOperation(new str("not writable"));
    const char *wnl = 0; /* '\n' written as */
    if (nl == NL_UNIVERSAL) {
#ifdef WIN32
        wnl = "\r\n"; /* os.linesep */
#endif
    } else if (nl == NL_CR)
        wnl = "\r";
    else if (nl == NL_CRLF)
        wnl = "\r\n";
    str *t = s;
    if (wnl && s->unit.find('\n') != __GC_STR::npos) {
        t = new str();
        for (size_t i = 0; i < s->unit.size(); i++) {
            if (s->unit[i] == '\n')
                for (const char *p = wnl; *p; p++)
                    t->unit.push_back((__ss_char)*p);
            else
                t->unit.push_back(s->unit[i]);
        }
    }
    __GC_BYTES b;
    if (__bom_pending) {
        __bom_pending = false;
        b = "\xef\xbb\xbf";
    }
    __encode_into(b, t, __encoding, __errors, errors);
    gz->write(new bytes(b));
    return len(s); /* characters, before translation */
}

__ss_int _GzipTextFile::seek(__ss_int i, __ss_int w) {
    __check_closed();
    /* positions are opaque cookies (from tell()), or the end */
    if (w == 1 && i != 0)
        throw new __io__::UnsupportedOperation(new str("can't do nonzero cur-relative seeks"));
    if (w == 2 && i != 0)
        throw new __io__::UnsupportedOperation(new str("can't do nonzero end-relative seeks"));
    if (w < 0 || w > 2)
        throw new ValueError(__add_strs(3, new str("invalid whence ("), __str(w), new str(", should be 0, 1 or 2)")));
    if (i < 0)
        throw new ValueError(__add_strs(2, new str("negative seek position "), __str(i)));
    if (w == 1)
        return gz->tell();
    bom_check = false;
    return gz->seek(i, w);
}

__ss_int _GzipTextFile::tell() {
    __check_closed();
    return gz->tell();
}

__ss_int _GzipTextFile::truncate(__ss_int) {
    __check_closed();
    throw new __io__::UnsupportedOperation(new str("truncate"));
}

void *_GzipTextFile::flush() {
    __check_closed();
    return gz->flush();
}

void *_GzipTextFile::close() {
    if (!closed) {
        closed = True;
        gz->close();
    }
    return NULL;
}

__ss_int _GzipTextFile::__ss_fileno() {
    __check_closed();
    return gz->__ss_fileno();
}

__ss_bool _GzipTextFile::isatty() {
    __check_closed();
    return False;
}

/* open */

static str *__binary_mode(str *mode, str *encoding, str *errors, str *newline) {
    if (!mode)
        return new str("rb");
    if (mode->unit.find('t') != __GC_STR::npos) /* (constant text modes become open_text) */
        throw new ValueError(__add_strs(3, new str("Invalid mode: "), repr(mode), new str(" (shedskin only supports a constant text mode)")));
    if (encoding)
        throw new ValueError(new str("Argument 'encoding' not supported in binary mode"));
    if (errors)
        throw new ValueError(new str("Argument 'errors' not supported in binary mode"));
    if (newline)
        throw new ValueError(new str("Argument 'newline' not supported in binary mode"));
    return mode;
}

static str *__text_mode(str *mode) {
    if (!mode)
        return new str("r");
    if (mode->unit.find('b') != __GC_STR::npos)
        throw new ValueError(__add_strs(2, new str("Invalid mode: "), repr(mode)));
    __GC_STR m;
    for (__ss_char c : mode->unit)
        if (c != 't')
            m.push_back(c);
    return new str(m);
}

GzipFile *open(str *filename, str *mode, __ss_int compresslevel, str *encoding, str *errors, str *newline) {
    return new GzipFile(filename, __binary_mode(mode, encoding, errors, newline), compresslevel);
}

GzipFile *open(bytes *filename, str *mode, __ss_int compresslevel, str *encoding, str *errors, str *newline) {
    return open(new str(filename->unit), mode, compresslevel, encoding, errors, newline);
}

GzipFile *open(file_binary *fileobj, str *mode, __ss_int compresslevel, str *encoding, str *errors, str *newline) {
    return new GzipFile(NULL, __binary_mode(mode, encoding, errors, newline), compresslevel, fileobj);
}

_GzipTextFile *open_text(str *filename, str *mode, __ss_int compresslevel, str *encoding, str *errors, str *newline) {
    GzipFile *gz = new GzipFile(filename, __text_mode(mode), compresslevel);
    return new _GzipTextFile(gz, mode, encoding, errors, newline);
}

_GzipTextFile *open_text(bytes *filename, str *mode, __ss_int compresslevel, str *encoding, str *errors, str *newline) {
    return open_text(new str(filename->unit), mode, compresslevel, encoding, errors, newline);
}

_GzipTextFile *open_text(file_binary *fileobj, str *mode, __ss_int compresslevel, str *encoding, str *errors, str *newline) {
    GzipFile *gz = new GzipFile(NULL, __text_mode(mode), compresslevel, fileobj);
    return new _GzipTextFile(gz, mode, encoding, errors, newline);
}

/* compress, decompress */

bytes *__compress(bytes *data, __ss_int compresslevel, __ss_int mtime, bool has_mtime) {
    __check_level(compresslevel);
    mz_stream strm;
    memset(&strm, 0, sizeof(strm));
    strm.zalloc = __mz_alloc;
    strm.zfree = __mz_free;
    __deflate_init(&strm, compresslevel);

    bytes *result = new bytes();
    __GC_BYTES &out = result->unit;
    out.reserve(32 + data->unit.size() / 2);
    out += "\x1f\x8b\x08";
    out.push_back('\0');
    __put32(out, has_mtime ? (unsigned long long)mtime : (unsigned long long)::time(NULL));
    /* (as zlib does: the fast and stored levels both count as fastest) */
    out.push_back(compresslevel == 9 ? '\x02' : ((compresslevel == 0 || compresslevel == 1) ? '\x04' : '\0'));
    out.push_back('\xff');
    try {
        __deflate_into(&strm, out, data->unit.data(), data->unit.size(), MZ_FINISH);
    } catch (BaseException *) {
        mz_deflateEnd(&strm);
        throw;
    }
    mz_deflateEnd(&strm);
    __put32(out, __crc32(0, data->unit.data(), data->unit.size()));
    __put32(out, data->unit.size() & 0xffffffff);
    return result;
}

bytes *decompress(bytes *data) {
    const __GC_BYTES &in = data->unit;
    size_t pos = 0;
    bytes *result = new bytes();
    __GC_BYTES &out = result->unit;

    mz_stream strm;
    memset(&strm, 0, sizeof(strm));
    strm.zalloc = __mz_alloc;
    strm.zfree = __mz_free;
    __inflate_init(&strm);

    try {
        auto next = [&in, &pos]() { return pos < in.size() ? (int)(unsigned char)in[pos++] : -1; };
        __ss_int mtime;
        while (__read_gzip_header(next, mtime)) {
            mz_inflateReset(&strm);
            size_t start = out.size();
            int status;
            do {
                size_t old = out.size();
                size_t room = std::max(CHUNK_SIZE, std::min((size_t)MAX_AVAIL, 2 * (in.size() - pos)));
                out.resize(old + room);
                strm.next_in = (const unsigned char *)in.data() + pos;
                strm.avail_in = (unsigned int)std::min(in.size() - pos, (size_t)MAX_AVAIL);
                strm.next_out = (unsigned char *)&out[old];
                strm.avail_out = (unsigned int)room;
                status = mz_inflate(&strm, MZ_NO_FLUSH);
                pos = (const char *)strm.next_in - in.data();
                out.resize(old + room - strm.avail_out);
                if (status != MZ_OK && status != MZ_STREAM_END && status != MZ_BUF_ERROR)
                    throw __data_error();
                if (status == MZ_BUF_ERROR && pos == in.size())
                    throw __eof_error(); /* no more input */
            } while (status != MZ_STREAM_END);
            if (in.size() - pos < 8)
                throw __eof_error();
            size_t n = out.size() - start;
            if (__get32(in.data() + pos) != __crc32(0, out.data() + start, n))
                throw new BadGzipFile(new str("CRC check failed"));
            if (__get32(in.data() + pos + 4) != (unsigned int)(n & 0xffffffff))
                throw new BadGzipFile(new str("Incorrect length of data produced"));
            pos += 8;
            while (pos < in.size() && in[pos] == '\0')
                pos++;
        }
    } catch (BaseException *) {
        mz_inflateEnd(&strm);
        throw;
    }
    mz_inflateEnd(&strm);
    return result;
}

void __init() {
    READ = new str("rb");
    WRITE = new str("wb");
    FTEXT = 1;
    FHCRC = 2;
    FEXTRA = 4;
    FNAME = 8;
    FCOMMENT = 16;

    cl_BadGzipFile = new class_("BadGzipFile");
}

} // module namespace
