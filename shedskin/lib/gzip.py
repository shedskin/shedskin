# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

# reading only: open/GzipFile in mode 'rb', and decompress. the whole file is
# decompressed when it is opened (gzip.cpp has its own inflate, no zlib)

import io

READ = 'rb'


class BadGzipFile(OSError):
    pass


class GzipFile(io.BytesIO):
    def __init__(self, filename=None, mode=None):
        self.name = ''
        self.unit = b''
        self.closed = False


def open(filename, mode=None):
    return GzipFile(filename, mode)


def decompress(data):
    return b''
