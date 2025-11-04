import binascii


s = b"my guitar wants to strum all night long"


def test_qp():
    b2a = binascii.b2a_qp(s)
    assert b2a == b'my guitar wants to strum all night long'
    a2b = binascii.a2b_qp(b2a)
    assert a2b == s

    b2a = binascii.b2a_qp(s, header=True)
    assert b2a == b'my_guitar_wants_to_strum_all_night_long'
    a2b = binascii.a2b_qp(b2a, header=True)
    assert a2b == s

    a2b = binascii.b2a_qp(b'hoei\npap\r  hoempa\troempa  ', header=True)
    assert a2b == b'hoei\npap\r__hoempa\troempa_=20'

    a2b = binascii.b2a_qp(b'hoei\npap\r  hoempa\troempa  ', quotetabs=True, header=True)
    assert a2b == b'hoei\npap\r=20=20hoempa=09roempa=20=20'

    a2b = binascii.b2a_qp(b'hoei\npap\r  hoempa\troempa  ', istext=False, quotetabs=True, header=True)
    assert a2b == b'hoei=0Apap=0D=20=20hoempa=09roempa=20=20'


def test_uu():
    b2a = binascii.b2a_uu(s)
    assert b2a == b'G;7D@9W5I=&%R(\'=A;G1S(\'1O(\'-T<G5M(&%L;"!N:6=H="!L;VYG\n'
    a2b = binascii.a2b_uu(b2a)
    assert a2b == s

    t = b'hoepa'
    b2a = binascii.b2a_uu(t)
    assert b2a == b'%:&]E<&$ \n'

    b2a = binascii.b2a_uu(t, backtick=True)
    assert b2a == b'%:&]E<&$`\n'


def test_base64():
    b2a = binascii.b2a_base64(s)
    assert b2a == b'bXkgZ3VpdGFyIHdhbnRzIHRvIHN0cnVtIGFsbCBuaWdodCBsb25n\n'
    a2b = binascii.a2b_base64(b2a)
    assert a2b == s

    b2a = binascii.b2a_base64(s, newline=False)
    assert b2a == b'bXkgZ3VpdGFyIHdhbnRzIHRvIHN0cnVtIGFsbCBuaWdodCBsb25n'
    a2b = binascii.a2b_base64(b2a)
    assert a2b == s

    input_bytes = bytes(range(256))
    output_bytes = b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==\n'

    b2a = binascii.b2a_base64(input_bytes)
    assert b2a == output_bytes
#    a2b = binascii.a2b_base64(b2a)
#    assert a2b == input_bytes


def test_hex():  # b2a_hex == hexlify
    b2a = binascii.hexlify(s)
    assert b2a == b'6d79206775697461722077616e747320746f20737472756d20616c6c206e69676874206c6f6e67'
    a2b = binascii.unhexlify(b2a)
    assert a2b == s

    b2a = binascii.b2a_hex(s)
    assert b2a == b'6d79206775697461722077616e747320746f20737472756d20616c6c206e69676874206c6f6e67'
    a2b = binascii.a2b_hex(b2a)
    assert a2b == s

    b = b'hoepa'
    t = binascii.b2a_hex(b, '-', 1)
    assert t == b'68-6f-65-70-61'

    b = b'hoepa'
    t = binascii.hexlify(b, sep='-')
    assert t == b'68-6f-65-70-61'

    b = b'hoepa'
    t = binascii.b2a_hex(b, sep='-', bytes_per_sep=2)
    assert t == b'68-6f65-7061'

    b = b'hoep'
    t = binascii.hexlify(b, sep='-', bytes_per_sep=2)
    assert t == b'686f-6570'


def test_crc():
    crc = binascii.crc32(s)
    assert crc == 1546323114

    crc = binascii.crc32(s, 12)
    assert crc == 2762308548

    crc = binascii.crc_hqx(s, 12)
    assert crc == 53552


def test_all():
    test_qp()
    test_uu()
    test_base64()
    test_hex()
    test_crc()


if __name__ == '__main__':
    test_all()
