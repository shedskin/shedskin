# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

DEFAULT_BUFFER_SIZE = 8192
SEEK_SET = SEEK_CUR = SEEK_END = 0

__void = ''  # 'newline not given' sentinel (StringIO defaults to '\n', while None means universal newlines)


# CPython's UnsupportedOperation derives from both OSError and ValueError;
# shedskin exceptions are single-inheritance, so only OSError here
class UnsupportedOperation(OSError): pass

__exception = UnsupportedOperation('')


def text_encoding(encoding, stacklevel=2):
    return ''


class BytesIO(file_binary):
    def __init__(self, initial_bytes=None):
        self.unit = b''

    def getvalue(self):
        return b''

    def read1(self, size=-1):
        return b''

    def readable(self):
        return True

    def writable(self):
        return True

    def seekable(self):
        return True

    def detach(self):
        pass

    def truncate(self, size=-1):
        return 1


class StringIO(file):
    def __init__(self, initial_value=None, newline=__void):
        self.unit = ''

    def getvalue(self):
        return ''

    def readable(self):
        return True

    def writable(self):
        return True

    def seekable(self):
        return True

    def detach(self):
        pass

    def truncate(self, size=-1):
        return 1
