# Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE)


class BytesI(file_binary):
    pass

def BytesIO(s=b''):
    return BytesI(s)

