# Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE)

class Error(Exception):
    pass

class Incomplete(Exception):
    pass

def a2b_uu(string):
    return b''
def b2a_uu(data, backtick=False):
    return b''

def a2b_base64(string, strict_mode=False):
    return b''
def b2a_base64(data, newline=True):
    return b''

def a2b_qp(string, header=False):
    return b''
def b2a_qp(data, quotetabs=False, istext=True, header=False):
    return b''

def b2a_hex(data, sep=None, bytes_per_sep=1):
    return b''
def a2b_hex(data):
    return b''
def hexlify(data, sep=None, bytes_per_sep=1):
    return b''
def unhexlify(data):
    return b''

def crc_hqx(data, crc):
    return 0
def crc32(data, crc=0):
    return 0

