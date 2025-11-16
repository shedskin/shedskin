# Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE)


class BytesIO(file_binary):
    def __init__(self, initial_bytes=b''):
        self.unit = b''

    def getvalue(self):
        return b''


class StringIO(file):
    def __init__(self, initial_value=''):
        self.unit = ''

    def getvalue(self):
        return ''
