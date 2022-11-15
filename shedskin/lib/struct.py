# Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE)

class error(Exception):
    pass

def pack(fmt, *vals):
    return b''

def unpack(fmt, s):
    pass

def calcsize(fmt):
    return 1
