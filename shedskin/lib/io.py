# Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE)


class BytesIO(file_binary):
    def __init__(self, initial_bytes=b''):
        pass

    def getvalue(self):
        return b''


class StringIO(file):
    def __init__(self, initial_value=''):
        pass

    def getvalue(self):
        return ''
