/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "gzip.hpp"

/* reading gzip files (RFC 1952), with an inflate (RFC 1951) of its own, so
   as not to depend on zlib. errors follow CPython's gzip module, except that
   bad deflate data, a zlib.error there, raises BadGzipFile with the same
   message. */

namespace __gzip__ {

str *__name__;
str *READ;
class_ *cl_BadGzipFile, *cl_GzipFile;

static const char *EOF_MSG = "Compressed file ended before the end-of-stream marker was reached";

[[noreturn]] static void zlib_error(const char *msg) {
    throw new BadGzipFile(__add(new str("Error -3 while decompressing data: "), new str(msg)));
}

/* crc-32 */

static uint32_t crc_table[256];

static void make_crc_table() {
    for(uint32_t n = 0; n < 256; n++) {
        uint32_t c = n;
        for(int k = 0; k < 8; k++)
            c = (c & 1) ? 0xedb88320U ^ (c >> 1) : c >> 1;
        crc_table[n] = c;
    }
}

static uint32_t crc32(const char *data, size_t len) {
    uint32_t c = 0xffffffffU;
    for(size_t i = 0; i < len; i++)
        c = crc_table[(c ^ (unsigned char)data[i]) & 0xff] ^ (c >> 8);
    return c ^ 0xffffffffU;
}

/* inflate: an altered version of puff.c (zlib/contrib/puff), rewritten as a
   C++ class that appends to a byte string, with zlib's error messages and
   checks against the output of the current gzip member. its notice:

  Copyright (C) 2002-2013 Mark Adler, all rights reserved
  version 2.3, 21 Jan 2013

  This software is provided 'as-is', without any express or implied
  warranty.  In no event will the author be held liable for any damages
  arising from the use of this software.

  Permission is granted to anyone to use this software for any purpose,
  including commercial applications, and to alter it and redistribute it
  freely, subject to the following restrictions:

  1. The origin of this software must not be misrepresented; you must not
     claim that you wrote the original software. If you use this software
     in a product, an acknowledgment in the product documentation would be
     appreciated but is not required.
  2. Altered source versions must be plainly marked as such, and must not be
     misrepresented as being the original software.
  3. This notice may not be removed or altered from any source distribution.

  Mark Adler    madler@alumni.caltech.edu
*/

struct huffman {
    short count[16];   /* number of codes of each length */
    short symbol[288]; /* the symbols, ordered by code */
};

class inflater {
public:
    const unsigned char *in;
    size_t inlen, inpos;
    unsigned bitbuf;
    int bitcnt;
    __GC_BYTES &out;
    size_t start; /* where the output of this stream starts */

    inflater(const unsigned char *in_, size_t inlen_, size_t inpos_, __GC_BYTES &out_) :
        in(in_), inlen(inlen_), inpos(inpos_), bitbuf(0), bitcnt(0), out(out_), start(out_.size()) {}

    int bits(int need) {
        unsigned long val = bitbuf;
        while(bitcnt < need) {
            if(inpos == inlen)
                throw new EOFError(new str(EOF_MSG));
            val |= (unsigned long)in[inpos++] << bitcnt;
            bitcnt += 8;
        }
        bitbuf = (unsigned)(val >> need);
        bitcnt -= need;
        return (int)(val & ((1UL << need) - 1));
    }

    void stored() {
        bitbuf = 0; /* to a byte boundary */
        bitcnt = 0;
        if(inpos + 4 > inlen)
            throw new EOFError(new str(EOF_MSG));
        unsigned len = in[inpos] | (in[inpos + 1] << 8);
        unsigned nlen = in[inpos + 2] | (in[inpos + 3] << 8);
        inpos += 4;
        if(len != (~nlen & 0xffff))
            zlib_error("invalid stored block lengths");
        if(inpos + len > inlen)
            throw new EOFError(new str(EOF_MSG));
        out.append((const char *)in + inpos, len);
        inpos += len;
    }

    int decode(const huffman &h) {
        int code = 0, first = 0, index = 0;
        for(int len = 1; len < 16; len++) {
            code |= bits(1);
            int count = h.count[len];
            if(code - count < first)
                return h.symbol[index + (code - first)];
            index += count;
            first += count;
            first <<= 1;
            code <<= 1;
        }
        return -1; /* ran out of codes */
    }

    /* 0: complete code, < 0: over-subscribed, > 0: incomplete */
    static int construct(huffman &h, const short *length, int n) {
        for(int len = 0; len < 16; len++)
            h.count[len] = 0;
        for(int symbol = 0; symbol < n; symbol++)
            h.count[length[symbol]]++;
        if(h.count[0] == n)
            return 0;
        int left = 1;
        for(int len = 1; len < 16; len++) {
            left <<= 1;
            left -= h.count[len];
            if(left < 0)
                return left;
        }
        short offs[16];
        offs[1] = 0;
        for(int len = 1; len < 15; len++)
            offs[len + 1] = offs[len] + h.count[len];
        for(int symbol = 0; symbol < n; symbol++)
            if(length[symbol] != 0)
                h.symbol[offs[length[symbol]]++] = (short)symbol;
        return left;
    }

    void codes(const huffman &lencode, const huffman &distcode) {
        static const short lbase[29] = {3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31,
            35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258};
        static const short lext[29] = {0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2,
            3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0};
        static const short dbase[30] = {1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193,
            257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145, 8193, 12289, 16385, 24577};
        static const short dext[30] = {0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6,
            7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13};
        for(;;) {
            int symbol = decode(lencode);
            if(symbol < 0)
                zlib_error("invalid literal/length code");
            if(symbol < 256)
                out.push_back((char)symbol);
            else if(symbol == 256)
                return;
            else {
                symbol -= 257;
                if(symbol >= 29)
                    zlib_error("invalid literal/length code");
                size_t len = lbase[symbol] + bits(lext[symbol]);
                symbol = decode(distcode);
                if(symbol < 0 || symbol >= 30)
                    zlib_error("invalid distance code");
                size_t dist = dbase[symbol] + bits(dext[symbol]);
                if(dist > out.size() - start)
                    zlib_error("invalid distance too far back");
                size_t from = out.size() - dist;
                for(size_t i = 0; i < len; i++) /* may overlap what it adds */
                    out.push_back(out[from + i]);
            }
        }
    }

    void fixed() {
        static huffman lencode, distcode;
        static bool built = false;
        if(!built) {
            short lengths[288];
            int symbol = 0;
            for(; symbol < 144; symbol++) lengths[symbol] = 8;
            for(; symbol < 256; symbol++) lengths[symbol] = 9;
            for(; symbol < 280; symbol++) lengths[symbol] = 7;
            for(; symbol < 288; symbol++) lengths[symbol] = 8;
            construct(lencode, lengths, 288);
            for(symbol = 0; symbol < 30; symbol++) lengths[symbol] = 5;
            construct(distcode, lengths, 30);
            built = true;
        }
        codes(lencode, distcode);
    }

    void dynamic() {
        static const short order[19] = {16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15};
        short lengths[320];
        huffman lencode, distcode;
        int nlen = bits(5) + 257;
        int ndist = bits(5) + 1;
        int ncode = bits(4) + 4;
        if(nlen > 286 || ndist > 30)
            zlib_error(nlen > 286 ? "too many length or distance symbols" : "invalid distances set");
        int index;
        for(index = 0; index < ncode; index++)
            lengths[order[index]] = (short)bits(3);
        for(; index < 19; index++)
            lengths[order[index]] = 0;
        if(construct(lencode, lengths, 19) != 0)
            zlib_error("invalid code lengths set");
        index = 0;
        while(index < nlen + ndist) {
            int symbol = decode(lencode);
            if(symbol < 0)
                zlib_error("invalid code lengths set");
            if(symbol < 16)
                lengths[index++] = (short)symbol;
            else {
                short len = 0;
                if(symbol == 16) {
                    if(index == 0)
                        zlib_error("invalid bit length repeat");
                    len = lengths[index - 1];
                    symbol = 3 + bits(2);
                } else if(symbol == 17)
                    symbol = 3 + bits(3);
                else
                    symbol = 11 + bits(7);
                if(index + symbol > nlen + ndist)
                    zlib_error("invalid bit length repeat");
                while(symbol--)
                    lengths[index++] = len;
            }
        }
        if(lengths[256] == 0)
            zlib_error("invalid code -- missing end-of-block");
        int err = construct(lencode, lengths, nlen);
        if(err < 0 || (err > 0 && nlen - lencode.count[0] != 1))
            zlib_error("invalid literal/lengths set");
        err = construct(distcode, lengths + nlen, ndist);
        if(err < 0 || (err > 0 && ndist - distcode.count[0] != 1))
            zlib_error("invalid distances set");
        codes(lencode, distcode);
    }

    /* returns the position after the stream */
    size_t inflate() {
        int last;
        do {
            last = bits(1);
            int type = bits(2);
            if(type == 0)
                stored();
            else if(type == 1)
                fixed();
            else if(type == 2)
                dynamic();
            else
                zlib_error("invalid block type");
        } while(!last);
        return inpos;
    }
};

/* gzip members */

static size_t read_exact(size_t pos, size_t n, size_t len) {
    if(pos + n > len)
        throw new EOFError(new str(EOF_MSG));
    return pos + n;
}

/* the members in 'data', decompressed one after another; the crc messages
   of gzip.decompress and of reading a GzipFile differ in CPython */
static bytes *gunzip(bytes *data, bool file) {
    const unsigned char *in = (const unsigned char *)data->unit.data();
    size_t len = data->unit.size();
    size_t pos = 0;
    __GC_BYTES out;

    while(pos < len) {
        /* header */
        if(len - pos < 2 || in[pos] != 0x1f || in[pos + 1] != 0x8b) {
            bytes *magic = new bytes(data->unit.substr(pos, 2));
            throw new BadGzipFile(__add_strs(3, new str("Not a gzipped file ("), repr(magic), new str(")")));
        }
        size_t p = read_exact(pos + 2, 8, len);
        int method = in[pos + 2];
        int flag = in[pos + 3];
        if(method != 8)
            throw new BadGzipFile(new str("Unknown compression method"));
        if(flag & 4) { /* FEXTRA */
            size_t q = read_exact(p, 2, len);
            p = read_exact(q, in[p] | (in[p + 1] << 8), len);
        }
        for(int f = 8; f <= 16; f <<= 1) /* FNAME, FCOMMENT */
            if(flag & f) {
                while(p < len && in[p] != 0)
                    p++;
                if(p < len)
                    p++;
            }
        if(flag & 2) /* FHCRC */
            p = read_exact(p, 2, len);

        /* deflate stream, crc-32 and size */
        size_t start = out.size();
        inflater inf(in, len, p, out);
        p = inf.inflate();
        if(p + 8 > len)
            throw new EOFError(new str(EOF_MSG));
        uint32_t crc = in[p] | (in[p + 1] << 8) | (in[p + 2] << 16) | ((uint32_t)in[p + 3] << 24);
        uint32_t isize = in[p + 4] | (in[p + 5] << 8) | (in[p + 6] << 16) | ((uint32_t)in[p + 7] << 24);
        uint32_t crc2 = crc32(out.data() + start, out.size() - start);
        if(crc != crc2) {
            if(file)
                throw new BadGzipFile(__mod6(new str("CRC check failed %s != %s"), 2,
                                             hex((__ss_int)crc), hex((__ss_int)crc2)));
            throw new BadGzipFile(new str("CRC check failed"));
        }
        if(isize != (uint32_t)(out.size() - start))
            throw new BadGzipFile(new str("Incorrect length of data produced"));
        pos = p + 8;

        /* zero padding between members */
        while(pos < len && in[pos] == 0)
            pos++;
    }
    return new bytes(out);
}

/* GzipFile */

GzipFile::GzipFile(str *filename, str *mode) : __io__::BytesIO() {
    this->__class__ = cl_GzipFile;
    if(mode && !(__eq(mode, new str("r")) || __eq(mode, new str("rb"))))
        throw new ValueError(__add_strs(3, new str("Invalid mode: "), repr(mode),
                                        new str(" (shedskin's gzip only reads, in mode 'rb')")));
    if(!filename)
        throw new TypeError(new str("filename must be a str or bytes object, or a file"));
    file_binary *f = new file_binary(filename, new str("rb"));
    bytes *raw = f->read(-1);
    f->close();
    s = gunzip(raw, true);
    name = filename;
    this->mode = READ;
}

__ss_int GzipFile::write(bytes *) {
    __check_closed();
    throw new OSError(new str("[Errno 9] write() on read-only GzipFile object"));
}

__ss_int GzipFile::truncate(__ss_int) {
    throw new __io__::UnsupportedOperation(new str("truncate"));
}

str *GzipFile::__repr__() {
    return __add_strs(3, new str("<gzip _io.BufferedReader name="), repr(name), new str(">"));
}

GzipFile *open(str *filename, str *mode) {
    return new GzipFile(filename, mode);
}

bytes *decompress(bytes *data) {
    return gunzip(data, false);
}

void __init() {
    __name__ = new str("gzip");
    READ = new str("rb");
    cl_BadGzipFile = new class_("BadGzipFile");
    cl_GzipFile = new class_("GzipFile");
    make_crc_table();
}

} // module namespace
