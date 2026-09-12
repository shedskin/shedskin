# Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE)

BASE64_ALPHABET = URLSAFE_BASE64_ALPHABET = BASE85_ALPHABET = ASCII85_ALPHABET = Z85_ALPHABET = BASE32_ALPHABET = BASE32HEX_ALPHABET = b''

class Error(Exception):
    pass

class Incomplete(Exception):
    pass

def a2b_uu(data):
    return b''
def b2a_uu(data, backtick=False):
    return b''

def a2b_base64(data, strict_mode=False):
    return b''
def b2a_base64(data, newline=True, wrapcol=0):
    return b''

def a2b_ascii85(data, foldspaces=False, adobe=False, ignorechars=b'', canonical=False):
    return b''
def b2a_ascii85(data, foldspaces=False, wrapcol=0, pad=False, adobe=False):
    return b''

def a2b_base85(data, alphabet=None, ignorechars=b'', canonical=False):
    return b''
def b2a_base85(data, alphabet=None, wrapcol=0, pad=False):
    return b''

def a2b_base32(data, padded=True, alphabet=None, ignorechars=b'', canonical=False):
    return b''
def b2a_base32(data, padded=True, alphabet=None, wrapcol=0):
    return b''

def a2b_qp(data, header=False):
    return b''
def b2a_qp(data, quotetabs=False, istext=True, header=False):
    return b''

def b2a_hex(data, sep=None, bytes_per_sep=1):
    return b''
def a2b_hex(hexstr):
    return b''
def hexlify(data, sep=None, bytes_per_sep=1):
    return b''
def unhexlify(hexstr):
    return b''

def crc_hqx(data, crc):
    return 0
def crc32(data, crc=0):
    return 0

