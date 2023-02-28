# Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE)

class error(Exception):
    pass

def pack(format, *vals):
    return b''

def unpack(format, s):
    pass

def unpack_from(format, buffer, offset=0):
    pass

def calcsize(format):
    return 1
