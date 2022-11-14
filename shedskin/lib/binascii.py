# Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE)

class Error(Exception):
    pass

class Incomplete(Exception):
    pass

def a2b_uu(string):
    return b''
def b2a_uu(data):
    return b''
def a2b_base64(string):
    return b''
def b2a_base64(data):
    return b''
def a2b_qp(string, header=False):
    return b''
def b2a_qp(data, quotetabs=False, istext=False, header=False):
    return b''
def a2b_hqx(string):
    return (b'',0)
def b2a_hqx(data):
    return b''
def rledecode_hqx(data):
    return b''
def rlecode_hqx(data):
    return b''
def crc_hqx(data, crc):
    return 0
def crc32(data, crc=0):
    return 0
def b2a_hex(data):
    return b''
def a2b_hex(data):
    return b''
def hexlify(data):
    return b''
def unhexlify(data):
    return b''
