import binascii

def test_binascii():
    s = b"my guitar wants to strum all night long"

    assert binascii.b2a_qp(s) == b'my guitar wants to strum all night long'
    # b2a = binascii.b2a_qp(s)
    # print(repr(b2a))
    # a2b = binascii.a2b_qp(b2a)
    # print(repr(a2b))

    assert binascii.b2a_uu(s) == b'G;7D@9W5I=&%R(\'=A;G1S(\'1O(\'-T<G5M(&%L;"!N:6=H="!L;VYG\n'

    # b2a = binascii.b2a_uu(s)
    # print(repr(b2a))
    # a2b = binascii.a2b_uu(b2a)
    # print(repr(a2b))

    assert binascii.b2a_hex(s) == b'6d79206775697461722077616e747320746f20737472756d20616c6c206e69676874206c6f6e67'
    # b2a = binascii.b2a_hex(s)
    # print(repr(b2a))
    # a2b = binascii.a2b_hex(b2a)
    # print(repr(a2b))


    assert binascii.b2a_base64(s) == b'bXkgZ3VpdGFyIHdhbnRzIHRvIHN0cnVtIGFsbCBuaWdodCBsb25n\n'
    # b2a = binascii.b2a_base64(s)
    # print(repr(b2a))
    # a2b = binascii.a2b_base64(b2a)
    # print(repr(a2b))


    assert binascii.hexlify(s) == b'6d79206775697461722077616e747320746f20737472756d20616c6c206e69676874206c6f6e67'
    # b2a = binascii.hexlify(s)
    # print(repr(b2a))
    # a2b = binascii.unhexlify(b2a)
    # print(repr(a2b))


def test_all():
    test_binascii()

if __name__ == '__main__':
    test_all()
