# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

# deflate/inflate is done by the vendored miniz library (see miniz/)

import io

__void = 0  # 'mtime not given' sentinel (defaults to the current time)

READ = 'rb'
WRITE = 'wb'

FTEXT = 1
FHCRC = 2
FEXTRA = 4
FNAME = 8
FCOMMENT = 16


class BadGzipFile(OSError): pass

__exception = BadGzipFile('')


class GzipFile(file_binary):
    def __init__(self, filename=None, mode=None, compresslevel=9, fileobj=None, mtime=__void):
        self.unit = b''
        self.closed = False
        self.name = ''
        self.mode = ''
        self.mtime = 0  # (None in CPython, before the first header is read)

    def read1(self, size=-1):
        return b''

    def peek(self, n=0):
        return b''

    # NOTE b must be a bytearray (array.array/memoryview unsupported)
    def readinto(self, b):
        return 1

    def readinto1(self, b):
        return 1

    def rewind(self):
        pass

    def readable(self):
        return True

    def writable(self):
        return True

    def seekable(self):
        return True


# gzip.open(.., 'rt') and friends: text modes become open_text (see graph.py)
class _GzipTextFile(file):
    def __init__(self, gz):
        self.unit = ''
        self.closed = False
        self.name = ''
        self.mode = ''
        self.encoding = ''
        self.errors = ''

    def readable(self):
        return True

    def writable(self):
        return True

    def seekable(self):
        return True


def open(filename, mode=None, compresslevel=9, encoding=None, errors=None, newline=None):
    return GzipFile(filename)

def open_text(filename, mode=None, compresslevel=9, encoding=None, errors=None, newline=None):  # gzip.open(.., 'rt'), see graph.py
    return _GzipTextFile(GzipFile(filename))

def compress(data, compresslevel=9, mtime=__void):
    return b''

def decompress(data):
    return b''
