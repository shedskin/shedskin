import binascii


s = b"my guitar wants to strum all night long"


# ..hqx.. functions are deprecated!


def test_b2a_a2b():
    b2a = binascii.b2a_qp(s)
    assert b2a == b'my guitar wants to strum all night long'
    a2b = binascii.a2b_qp(b2a)
    assert a2b == s

    b2a = binascii.b2a_uu(s)
    assert b2a == b'G;7D@9W5I=&%R(\'=A;G1S(\'1O(\'-T<G5M(&%L;"!N:6=H="!L;VYG\n'
    a2b = binascii.a2b_uu(b2a)
    assert a2b == s

    b2a = binascii.b2a_hex(s)
    assert b2a == b'6d79206775697461722077616e747320746f20737472756d20616c6c206e69676874206c6f6e67'
    a2b = binascii.a2b_hex(b2a)
    assert a2b == s

    b2a = binascii.b2a_base64(s)
    assert b2a == b'bXkgZ3VpdGFyIHdhbnRzIHRvIHN0cnVtIGFsbCBuaWdodCBsb25n\n'
    a2b = binascii.a2b_base64(b2a)
    assert a2b == s


def test_hexlify():
    b2a = binascii.hexlify(s)
    assert b2a == b'6d79206775697461722077616e747320746f20737472756d20616c6c206e69676874206c6f6e67'
    a2b = binascii.unhexlify(b2a)
    assert a2b == s


def test_crc():
    crc = binascii.crc32(s)
    assert crc == 1546323114


def test_all():
    test_b2a_a2b()
    test_hexlify()
    test_crc()


if __name__ == '__main__':
    test_all()
