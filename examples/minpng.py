#!/usr/bin/env python

# A minimal encoder for uncompressed PNGs.
# http://mainisusuallyafunction.blogspot.com/search/label/png

import struct

def to_ppm(width, height, data):
    return 'P6\n%d %d\n255\n%s' % (width, height, data)

def be32(n):
    return struct.pack('>I', n)

def png_chunk(ty, data):
    return be32(len(data)) + ty + data + be32(crc(ty + data))

def png_header(width, height):
    return png_chunk('IHDR',
        struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))

MAX_DEFLATE = 0xffff
def deflate_block(data, last=False):
    n = len(data)
    assert n <= MAX_DEFLATE
    return struct.pack('<BHH', bool(last), n, 0xffff ^ n) + data

def pieces(seq, n):
    return [seq[i:i+n] for i in xrange(0, len(seq), n)]

def zlib_stream(data):
    segments = pieces(data, MAX_DEFLATE)

    blocks = ''.join(deflate_block(p) for p in segments[:-1])
    blocks += deflate_block(segments[-1], last=True)

    return '\x78\x01' + blocks + be32(adler32(data))

def to_png(width, height, data):
    lines = ''.join('\0'+p for p in pieces(data, 3*width))

    return ('\x89PNG\r\n\x1a\n'
        + png_header(width, height)
        + png_chunk('IDAT', zlib_stream(lines))
        + png_chunk('IEND', ''))

def crc(data):
    c = 0xffffffff
    for x in data:
        c ^= ord(x)
        for k in xrange(8):
            v = 0xedb88320 if c & 1 else 0
            c = v ^ ((c >> 1) & 0x7fffffff) # & 0x7fffffff to avoid sign-extension for 32-bit signed arithmetic
    return c ^ 0xffffffff

def adler32(data):
    s1, s2 = 1, 0
    for x in data:
        s1 = (s1 + ord(x)) % 65521
        s2 = (s2 + s1) % 65521
    return (s2 << 16) + s1

w, h = 500, 300
img = []
for y in xrange(h):
    for x in xrange(w):
        img.extend([chr(x % 256), chr(y % 256), '\0'])

open('out.ppm', 'wb').write(to_ppm(w, h, ''.join(img)))
open('out.png', 'wb').write(to_png(w, h, ''.join(img)))
