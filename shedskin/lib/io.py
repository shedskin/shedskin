# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

DEFAULT_BUFFER_SIZE = 8192
SEEK_SET = SEEK_CUR = SEEK_END = 0


class BytesIO(file_binary):
    def __init__(self, initial_bytes=None):
        self.unit = b''

    def getvalue(self):
        return b''

    def truncate(self, size=-1):
        return 1


class StringIO(file):
    def __init__(self, initial_value=None):
        self.unit = ''

    def getvalue(self):
        return ''

    def truncate(self, size=-1):
        return 1
