import binascii

# TODO some functions accept strs in addition to bytes..

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

    input_bytes = bytes(range(256))
    output_bytes = b'=00=01=02=03=04=05=06=07=08=09\n=0B=0C\r=0E=0F=10=11=12=13=14=15=16=17=18=19=1A=1B=1C=1D=1E=1F !"#$%&\'()*+,-=\n./0123456789:;<=3D>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuv=\nwxyz{|}~=7F=80=81=82=83=84=85=86=87=88=89=8A=8B=8C=8D=8E=8F=90=91=92=93=94=\n=95=96=97=98=99=9A=9B=9C=9D=9E=9F=A0=A1=A2=A3=A4=A5=A6=A7=A8=A9=AA=AB=AC=AD=\n=AE=AF=B0=B1=B2=B3=B4=B5=B6=B7=B8=B9=BA=BB=BC=BD=BE=BF=C0=C1=C2=C3=C4=C5=C6=\n=C7=C8=C9=CA=CB=CC=CD=CE=CF=D0=D1=D2=D3=D4=D5=D6=D7=D8=D9=DA=DB=DC=DD=DE=DF=\n=E0=E1=E2=E3=E4=E5=E6=E7=E8=E9=EA=EB=EC=ED=EE=EF=F0=F1=F2=F3=F4=F5=F6=F7=F8=\n=F9=FA=FB=FC=FD=FE=FF'
    b2a = binascii.b2a_qp(input_bytes)
    assert b2a == output_bytes
    assert binascii.a2b_qp(b2a) == input_bytes


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

    output_bytes = b''
    for i in range(0, 256, 45):
        input_bytes = bytes(range(i, min(i+45, 256)))
        output_bytes += binascii.b2a_uu(input_bytes)
    assert output_bytes == b'M  $" P0%!@<("0H+# T.#Q 1$A,4%187&!D:&QP=\'A\\@(2(C)"4F)R@I*BLL\nM+2XO,#$R,S0U-C<X.3H[/#T^/T!!0D-$149\'2$E*2TQ-3D]045)35%565UA9\nM6EM<75Y?8&%B8V1E9F=H:6IK;&UN;W!Q<G-T=79W>\'EZ>WQ]?G^ @8*#A(6&\nMAXB)BHN,C8Z/D)&2DY25EI>8F9J;G)V>GZ"AHJ.DI::GJ*FJJZRMKJ^PL;*S\nMM+6VM[BYNKN\\O;Z_P,\'"P\\3%QL?(R<K+S,W.S]#1TM/4U=;7V-G:V]S=WM_@\n?X>+CY.7FY^CIZNOL[>[O\\/\'R\\_3U]O?X^?K[_/W^_P  \n'

    for i in range(0, 256, 45):
        input_bytes = bytes(range(i, min(i+45, 256)))
        output_bytes = binascii.b2a_uu(input_bytes)
        assert binascii.a2b_uu(output_bytes) == input_bytes

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
    assert binascii.a2b_base64(b2a) == input_bytes


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

    output_bytes = b'000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f606162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebfc0c1c2c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedfe0e1e2e3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfeff'
    input_bytes = bytes(range(256))
    b2a = binascii.b2a_hex(input_bytes)
    assert b2a == output_bytes
    assert binascii.a2b_hex(b2a) == input_bytes


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
