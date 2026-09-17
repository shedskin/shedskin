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


def test_b2a_qp_leading_dot_at_end():
    # regression test: b2a_qp checked whether a leading "." at the
    # start of a line is followed by a newline/CR/NUL (the historical
    # C-string-terminator check) by unconditionally reading data[in+1],
    # which reads one byte past the buffer when "." is the very last
    # byte of the input.
    assert binascii.b2a_qp(b'.') == b'=2E'
    assert binascii.b2a_qp(b'.\x00') == b'=2E=00'
    assert binascii.b2a_qp(b'.\x00x') == b'=2E=00x'
    assert binascii.b2a_qp(b'.\n') == b'=2E\n'
    assert binascii.b2a_qp(b'.\r') == b'=2E\r'
    assert binascii.b2a_qp(b'a.') == b'a.'
    assert binascii.b2a_qp(b'test.') == b'test.'
    assert binascii.b2a_qp(b'.A') == b'.A'


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


def test_a2b_uu_short_input():
    # regression test: a2b_uu read the declared length byte (and later
    # data bytes) straight off the input buffer, with no guard for the
    # buffer running out before that many bytes were actually supplied.
    # CPython's buffers are always NUL-terminated so reading "past the
    # end" harmlessly sees an implicit 0 there and CPython treats that
    # like whitespace/padding; our storage has no such terminator, so
    # this used to read past the end of the buffer.
    assert binascii.a2b_uu(b'') == b'\x00' * 32

    # length byte claims 45 bytes of output, but only one data
    # character follows before the line ends.
    assert binascii.a2b_uu(bytes.fromhex('4d4d0a')) == b'\xb4' + b'\x00' * 44

    # the common case this code path exists for: a mail transport (or
    # a human) strips the trailing whitespace from a uuencoded line.
    encoded = binascii.b2a_uu(b'hoepa')
    stripped = encoded.rstrip(b' \n') + b'\n'
    assert binascii.a2b_uu(stripped) == b'hoepa'


def test_a2b_uu_trailing_garbage_message():
    # regression test: a2b_uu raised binascii.Error with no message
    # (None) for illegal trailing characters, where CPython raises
    # binascii.Error("Trailing garbage"). The exception type already
    # matched CPython; only the message text was missing.
    ok = False
    try:
        binascii.a2b_uu(b'!XXXXX!\n')
    except binascii.Error as e:
        ok = True
        assert str(e) == 'Trailing garbage'
    assert ok

    ok = False
    try:
        binascii.a2b_uu(b'!AB!!\n')
    except binascii.Error as e:
        ok = True
        assert str(e) == 'Trailing garbage'
    assert ok


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


def test_b2a_uu_and_b2a_base64_no_signed_overflow_on_long_input():
    # regression test: both b2a_uu and b2a_base64 accumulate bytes into
    # a signed accumulator ("leftchar") that, unlike its a2b_uu and
    # a2b_base64 counterparts, was never masked back down after each
    # 6-bit group was extracted. Every remaining bit ever shifted in
    # stayed in the value forever, so leftchar's magnitude grew by 8
    # bits per input byte with no bound -- for any input longer than a
    # handful of bytes this overflows the signed accumulator, which is
    # undefined behavior (caught by UBSan), even though the shift-and-
    # mask used to pull out each 6-bit group happens to read the
    # correct bits regardless. These exercise inputs long enough to
    # have triggered it.
    data45 = bytes(range(45))
    assert binascii.b2a_uu(data45) == b'M  $" P0%!@<("0H+# T.#Q 1$A,4%187&!D:&QP=\'A\\@(2(C)"4F)R@I*BLL\n'

    data200 = bytes(range(200))
    assert binascii.b2a_base64(data200) == (
        b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4v'
        b'MDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5f'
        b'YGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6P'
        b'kJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/'
        b'wMHCw8TFxsc=\n'
    )


def test_base64_strict_mode():
    # valid data is accepted in strict mode
    assert binascii.a2b_base64(b'SGVsbG8h', strict_mode=True) == b'Hello!'

    # non-alphabet characters are rejected in strict mode ...
    ok = False
    try:
        binascii.a2b_base64(b'SGVsbG8h@#$%', strict_mode=True)
    except binascii.Error:
        ok = True
    assert ok
    # ... but silently skipped otherwise
    assert binascii.a2b_base64(b'SGVsbG8h@#$%', strict_mode=False) == b'Hello!'

    # embedded whitespace is rejected in strict mode ...
    ok = False
    try:
        binascii.a2b_base64(b'SGVs\r\nbG8h', strict_mode=True)
    except binascii.Error:
        ok = True
    assert ok
    # ... but tolerated otherwise
    assert binascii.a2b_base64(b'SGVs\r\nbG8h', strict_mode=False) == b'Hello!'

    # leading padding is always rejected in strict mode
    ok = False
    try:
        binascii.a2b_base64(b'=SGVsbG8h', strict_mode=True)
    except binascii.Error:
        ok = True
    assert ok

    # discontinuous / misplaced padding is rejected in strict mode
    ok = False
    try:
        binascii.a2b_base64(b'S=GVsbG8h', strict_mode=True)
    except binascii.Error:
        ok = True
    assert ok

    # trailing data (even just a newline) after a valid pad is rejected
    # in strict mode, but tolerated otherwise
    padded = binascii.b2a_base64(b'hello', newline=False)
    ok = False
    try:
        binascii.a2b_base64(padded + b'\n', strict_mode=True)
    except binascii.Error:
        ok = True
    assert ok
    assert binascii.a2b_base64(padded + b'\n', strict_mode=False) == b'hello'

    # empty input is fine in strict mode
    assert binascii.a2b_base64(b'', strict_mode=True) == b''

    # trailing padding right after an already-complete group (quad_pos
    # == 0) is tolerated in non-strict mode, but since CPython 3.15 it is
    # rejected as excess padding in strict mode (RFC 4648 section 3.3)
    for excess in (b'wK8j=', b'wK8j==', b'AAAA=', b'AAAA====', b'QQ==='):
        ok = False
        try:
            binascii.a2b_base64(excess, strict_mode=True)
        except binascii.Error as e:
            ok = True
            assert str(e) == 'Excess padding not allowed'
        assert ok
    assert binascii.a2b_base64(b'wK8j=') == b'\xc0\xaf#'
    assert binascii.a2b_base64(b'wK8j==') == b'\xc0\xaf#'
    assert binascii.a2b_base64(b'AAAA====') == b'\x00\x00\x00'
    assert binascii.a2b_base64(b'QQ===') == b'A'

    # ... and real data after that trailing padding is rejected too
    ok = False
    try:
        binascii.a2b_base64(b'AAAA=BBBB', strict_mode=True)
    except binascii.Error:
        ok = True
    assert ok

    # regression: a single (unmatched) pad at quad_pos == 2 followed by
    # whitespace must report the whitespace, not "discontinuous padding"
    # (the fix must not look ahead past the whitespace to find real data)
    ok = False
    try:
        binascii.a2b_base64(b'YpIygf=\rd', strict_mode=True)
    except binascii.Error as e:
        ok = True
        assert 'base64 data' in str(e)
    assert ok

    # regression: a single trailing pad at quad_pos == 2 with nothing
    # else following is "Incorrect padding", not "discontinuous padding"
    ok = False
    try:
        binascii.a2b_base64(b'8H=', strict_mode=True)
    except binascii.Error as e:
        ok = True
        assert str(e) == 'Incorrect padding'
    assert ok


def expect_error_msg(f, msg=None):
    ok = False
    try:
        f()
    except binascii.Error as e:
        ok = True
        if msg is not None:
            assert str(e) == msg, str(e)
    assert ok


def test_base64_ignorechars():
    # ignorechars only matters in strict mode, and giving it makes strict
    # mode the default (CPython 3.15 semantics) ...
    assert binascii.a2b_base64(b'aG\nk=', ignorechars=b'\n') == b'hi'
    assert binascii.a2b_base64(b'aG k=\r\n', ignorechars=b' \r\n') == b'hi'
    expect_error_msg(lambda: binascii.a2b_base64(b'aG\nk=', ignorechars=b' '),
                 'Only base64 data is allowed')
    expect_error_msg(lambda: binascii.a2b_base64(b'aGk=\n', ignorechars=b''),
                 'Only base64 data is allowed')
    assert binascii.a2b_base64(b'aGk=', ignorechars=b'') == b'hi'
    # ... unless strict_mode is explicitly turned off again
    assert binascii.a2b_base64(b'aG\nk=', ignorechars=b' ', strict_mode=False) == b'hi'
    assert binascii.a2b_base64(b'aGk=\n', ignorechars=b'', strict_mode=False) == b'hi'
    # and explicitly turning it on is the same as the default
    assert binascii.a2b_base64(b'aG\nk=', ignorechars=b'\n', strict_mode=True) == b'hi'

    # ignoring the pad character makes misplaced/excess padding acceptable
    expect_error_msg(lambda: binascii.a2b_base64(b'AAAA=', strict_mode=True),
                 'Excess padding not allowed')
    assert binascii.a2b_base64(b'AAAA=', ignorechars=b'=') == b'\x00\x00\x00'
    assert binascii.a2b_base64(b'AAAA==', ignorechars=b'=') == b'\x00\x00\x00'
    assert binascii.a2b_base64(b'aG=k=', ignorechars=b'=') == b'hi'
    assert binascii.a2b_base64(b'=AAAA', ignorechars=b'=') == b'\x00\x00\x00'
    assert binascii.a2b_base64(b'QQ==QQ==', ignorechars=b'=') == b'A\x04\x10'
    expect_error_msg(lambda: binascii.a2b_base64(b'aG=k=', ignorechars=b'\n'),
                 'Discontinuous padding not allowed')
    expect_error_msg(lambda: binascii.a2b_base64(b'QQ==QQ==', ignorechars=b'\n'),
                 'Excess data after padding')
    # ... but a missing closing pad is still an error
    expect_error_msg(lambda: binascii.a2b_base64(b'aGk', ignorechars=b'='),
                 'Incorrect padding')
    # and so is a lone data character
    expect_error_msg(lambda: binascii.a2b_base64(b'A=', ignorechars=b'='))
    expect_error_msg(lambda: binascii.a2b_base64(b'AAAAA', ignorechars=b'='))

    # with padded=False the pad character is just another non-alphabet char
    expect_error_msg(lambda: binascii.a2b_base64(b'aGk=', padded=False, ignorechars=b'\n'),
                 'Padding not allowed')
    assert binascii.a2b_base64(b'aGk=', padded=False, ignorechars=b'=') == b'hi'
    assert binascii.a2b_base64(b'aG=k', padded=False, ignorechars=b'=') == b'hi'

    # high bytes can be ignored too
    assert binascii.a2b_base64(b'aGk=\x80', ignorechars=b'\x80') == b'hi'
    expect_error_msg(lambda: binascii.a2b_base64(b'aGk=\x80', ignorechars=b'\n'),
                 'Only base64 data is allowed')

    # empty input is fine either way
    assert binascii.a2b_base64(b'', ignorechars=b'=\n') == b''


def test_base64_alphabet():
    data = bytes(range(256))
    for alphabet in (binascii.BASE64_ALPHABET, binascii.URLSAFE_BASE64_ALPHABET,
                     binascii.UU_ALPHABET, binascii.CRYPT_ALPHABET,
                     binascii.BINHEX_ALPHABET):
        enc = binascii.b2a_base64(data, alphabet=alphabet, newline=False)
        assert len(enc) == 344
        assert enc.endswith(b'==')
        unpadded = binascii.b2a_base64(data, alphabet=alphabet, padded=False, newline=False)
        assert len(unpadded) == 342
        assert binascii.b2a_base64(b'', alphabet=alphabet, newline=False) == b''
        if alphabet != binascii.UU_ALPHABET:
            # (UU_ALPHABET contains '=', which CPython always treats as
            # the pad character, so arbitrary data does not round-trip)
            assert binascii.a2b_base64(enc, alphabet=alphabet) == data
            assert binascii.a2b_base64(enc, alphabet=alphabet, strict_mode=True) == data
            assert binascii.a2b_base64(enc + b'\n', alphabet=alphabet, ignorechars=b'\n') == data
            assert binascii.a2b_base64(unpadded, alphabet=alphabet, padded=False) == data
            assert binascii.a2b_base64(unpadded + b'\n', alphabet=alphabet, padded=False, ignorechars=b'\n') == data

    # spot checks against CPython 3.15
    assert binascii.b2a_base64(b'hi', alphabet=binascii.UU_ALPHABET, newline=False) == b':&D='
    assert binascii.a2b_base64(b':&D', alphabet=binascii.UU_ALPHABET, padded=False) == b'hi'
    assert binascii.a2b_base64(b':&D=', alphabet=binascii.UU_ALPHABET) == b'hi'
    assert binascii.b2a_base64(b'hi', alphabet=binascii.CRYPT_ALPHABET, newline=False) == b'O4Y='
    assert binascii.b2a_base64(b'hi', alphabet=binascii.BINHEX_ALPHABET, newline=False) == b"D'N="
    assert binascii.b2a_base64(bytes([251, 255, 191, 62]), alphabet=binascii.URLSAFE_BASE64_ALPHABET, newline=False) == b'-_-_Pg=='
    assert binascii.a2b_base64(b'-_-_Pg==', alphabet=binascii.URLSAFE_BASE64_ALPHABET) == bytes([251, 255, 191, 62])

    # with an explicit alphabet, the standard '+' and '/' are not special
    expect_error_msg(lambda: binascii.a2b_base64(b'+/+/Pg==', alphabet=binascii.URLSAFE_BASE64_ALPHABET, strict_mode=True),
                 'Only base64 data is allowed')
    assert binascii.a2b_base64(b'+/+/Pg==', alphabet=binascii.URLSAFE_BASE64_ALPHABET) == b'>'

    for bad in (b'', b'abc', binascii.BASE64_ALPHABET + b'x'):
        ok = False
        try:
            binascii.b2a_base64(b'hi', alphabet=bad)
        except ValueError:
            ok = True
        assert ok
        ok = False
        try:
            binascii.a2b_base64(b'aGk=', alphabet=bad)
        except ValueError:
            ok = True
        assert ok


def test_base64_canonical():
    # 'k' (36) has zero padding bits, 'l' (37) does not
    assert binascii.a2b_base64(b'aGk=', canonical=True) == b'hi'
    assert binascii.a2b_base64(b'aGl=') == b'hi'
    expect_error_msg(lambda: binascii.a2b_base64(b'aGl=', canonical=True), 'Non-zero padding bits')
    assert binascii.a2b_base64(b'QQ==', canonical=True) == b'A'
    expect_error_msg(lambda: binascii.a2b_base64(b'QR==', canonical=True), 'Non-zero padding bits')
    assert binascii.a2b_base64(b'QUJD', canonical=True) == b'ABC'
    # independent of strict_mode and padded
    expect_error_msg(lambda: binascii.a2b_base64(b'aGl', canonical=True, padded=False), 'Non-zero padding bits')
    assert binascii.a2b_base64(b'aGk', canonical=True, padded=False) == b'hi'
    expect_error_msg(lambda: binascii.a2b_base64(b'aG\nl=', canonical=True, ignorechars=b'\n'), 'Non-zero padding bits')


def test_base64_padding_errors():
    # a lone data character, or any leftover bits with no closing pad,
    # must raise -- not silently decode to truncated/fabricated bytes.
    for bad in (b'QQ', b'QQ=', b'AA', b'A', b'A='):
        ok = False
        try:
            binascii.a2b_base64(bad)
        except binascii.Error:
            ok = True
        assert ok

    # legitimately padded strings (single and double '=') must still
    # decode correctly -- regression check for the find_valid lookahead
    # used to detect a valid closing pad sequence.
    assert binascii.a2b_base64(b'QQ==') == b'A'
    assert binascii.a2b_base64(b'QUJ=') == b'AB'
    assert binascii.a2b_base64(b'QUJD') == b'ABC'

    # regression: the "1 more than a multiple of 4" message must include
    # the actual data-character count, matching CPython's wording.
    try:
        binascii.a2b_base64(b'AAAAA')
        assert False
    except binascii.Error as e:
        assert str(e) == (
            'Invalid base64-encoded string: number of data characters '
            '(5) cannot be 1 more than a multiple of 4')


def test_hex_ignorechars():
    assert binascii.a2b_hex(b'61 62', ignorechars=b' ') == b'ab'
    assert binascii.unhexlify(b'61\n62\n', ignorechars=b'\n') == b'ab'
    assert binascii.unhexlify(b'--61-62--', ignorechars=b'-') == b'ab'
    assert binascii.a2b_hex(b' ', ignorechars=b' ') == b''
    assert binascii.a2b_hex(b'6162', ignorechars=b'') == b'ab'
    assert binascii.a2b_hex(b'\x8061', ignorechars=b'\x80') == b'a'
    # hex digits are always consumed as digits, even if 'ignored'
    assert binascii.a2b_hex(b'6162', ignorechars=b'6') == b'ab'
    # non-ignored non-hex characters and odd digit counts still fail,
    # with the CPython 3.15 messages
    expect_error_msg(lambda: binascii.a2b_hex(b'61 62'), 'Non-hexadecimal digit found')
    expect_error_msg(lambda: binascii.a2b_hex(b'61 62', ignorechars=b'\n'), 'Non-hexadecimal digit found')
    expect_error_msg(lambda: binascii.unhexlify(b'616'), 'Odd number of hexadecimal digits')
    expect_error_msg(lambda: binascii.unhexlify(b'61 6', ignorechars=b' '), 'Odd number of hexadecimal digits')
    expect_error_msg(lambda: binascii.a2b_hex(b'6g'), 'Non-hexadecimal digit found')


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


# regression test: unhexlify indexed its lookup table with a signed
# char, so any input byte >= 0x80 sign-extended into a negative
# (out-of-bounds) index instead of being rejected as invalid hex.
def test_unhexlify_high_bit_bytes_rejected():
    for bad in (0x80, 0xff, 0xfe, 0x81):
        ok = False
        try:
            binascii.unhexlify(bytes([bad, 0x30]))
        except binascii.Error:
            ok = True
        assert ok, f"byte 0x{bad:02x} should have been rejected as invalid hex"

        ok = False
        try:
            binascii.a2b_hex(bytes([0x30, bad]))
        except binascii.Error:
            ok = True
        assert ok, f"byte 0x{bad:02x} should have been rejected as invalid hex"


# regression test: bytes_per_sep=0 used to divide/modulo by zero and crash
# the process with SIGFPE. CPython instead treats 0 the same as "no
# separators requested" (matching hexlify(data) with no sep at all).
def test_hex_bytes_per_sep_zero():
    assert binascii.hexlify(b'hello world', '-', 0) == b'68656c6c6f20776f726c64'
    assert binascii.hexlify(b'', '-', 0) == b''


# regression test: negative bytes_per_sep means "count groups from the
# left" in CPython, as opposed to positive values which count from the
# right. Shedskin used to ignore negative values entirely and emit no
# separators at all, regardless of magnitude.
def test_hex_bytes_per_sep_negative():
    data = bytes.fromhex('4dfad71427a0aeb3fee9')  # 10 bytes
    # evenly divisible lengths: left- and right-counting coincide
    assert binascii.hexlify(data, '-', 1) == binascii.hexlify(data, '-', -1)
    assert binascii.hexlify(data, '-', 2) == binascii.hexlify(data, '-', -2)
    # not evenly divisible by 3: left- and right-counting differ
    assert binascii.hexlify(data, '-', 3) == b'4d-fad714-27a0ae-b3fee9'
    assert binascii.hexlify(data, '-', -3) == b'4dfad7-1427a0-aeb3fe-e9'


# regression test: an invalid (non-length-1) sep must raise ValueError
# even when data is empty. This used to be skipped because the
# empty-data early return happened before the sep length was checked.
def test_hex_sep_validated_on_empty_data():
    for bad_sep in ('', 'ab'):
        ok = False
        try:
            binascii.hexlify(b'', bad_sep, 1)
        except ValueError as e:
            ok = True
            assert str(e) == 'sep must be length 1.'
        assert ok


def test_crc():
    crc = binascii.crc32(s)
    assert crc == 1546323114

    crc = binascii.crc32(s, 12)
    assert crc == 2762308548

    crc = binascii.crc_hqx(s, 12)
    assert crc == 53552


def test_crc_hqx_high_bit_bytes():
    # regression test: crc_hqx indexed its lookup table with a signed
    # char, so any input byte >= 0x80 sign-extended into a negative
    # (out-of-bounds) index instead of being treated as 0-255.
    data = bytes(range(256))
    assert binascii.crc_hqx(data, 0) == 32341
    assert binascii.crc_hqx(data, 12) == 8465

    data2 = bytes([0x8b, 0xff, 0x00, 0x80, 0x7f, 0xde, 0xad, 0xbe, 0xef])
    assert binascii.crc_hqx(data2, 0) == 18254
    assert binascii.crc_hqx(data2, 0xffff) == 24380


def expect_error(f):
    ok = False
    try:
        f()
    except binascii.Error:
        ok = True
    assert ok


def expect_value_error(f):
    ok = False
    try:
        f()
    except ValueError:
        ok = True
    assert ok


def a2b_base64_fails(s, padded=True, strict_mode=False):
    ok = False
    try:
        binascii.a2b_base64(s, strict_mode=strict_mode, padded=padded)
    except binascii.Error:
        ok = True
    assert ok


def a2b_base32_fails(s, padded=True):
    ok = False
    try:
        binascii.a2b_base32(s, padded=padded)
    except binascii.Error:
        ok = True
    assert ok


def a2b_base85_fails(s):
    ok = False
    try:
        binascii.a2b_base85(s)
    except binascii.Error:
        ok = True
    assert ok


def test_alphabets():
    assert len(binascii.BASE64_ALPHABET) == 64
    assert len(binascii.URLSAFE_BASE64_ALPHABET) == 64
    assert len(binascii.UU_ALPHABET) == 64
    assert len(binascii.CRYPT_ALPHABET) == 64
    assert len(binascii.BINHEX_ALPHABET) == 64
    assert binascii.UU_ALPHABET == bytes(range(32, 96))
    assert binascii.CRYPT_ALPHABET == b'./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    assert binascii.BINHEX_ALPHABET == b'!"#$%&\'()*+,-012345689@ABCDEFGHIJKLMNPQRSTUVXYZ[`abcdefhijklmpqr'
    for alphabet in (binascii.BASE64_ALPHABET, binascii.URLSAFE_BASE64_ALPHABET, binascii.UU_ALPHABET, binascii.CRYPT_ALPHABET, binascii.BINHEX_ALPHABET):
        assert len(set(alphabet)) == 64
    assert len(binascii.BASE85_ALPHABET) == 85
    assert len(binascii.ASCII85_ALPHABET) == 85
    assert len(binascii.Z85_ALPHABET) == 85
    assert len(binascii.BASE32_ALPHABET) == 32
    assert len(binascii.BASE32HEX_ALPHABET) == 32
    assert binascii.BASE64_ALPHABET.endswith(b'+/')
    assert binascii.URLSAFE_BASE64_ALPHABET.endswith(b'-_')
    assert binascii.ASCII85_ALPHABET == bytes(range(33, 118))
    assert binascii.BASE32_ALPHABET == b'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
    assert binascii.BASE32HEX_ALPHABET == b'0123456789ABCDEFGHIJKLMNOPQRSTUV'
    assert binascii.Z85_ALPHABET == b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#'
    for alphabet in (binascii.BASE85_ALPHABET, binascii.ASCII85_ALPHABET, binascii.Z85_ALPHABET):
        assert len(set(alphabet)) == 85


def test_b2a_base64_wrapcol():
    data = b'x' * 60
    assert binascii.b2a_base64(data, wrapcol=0) == b'eHh4' * 20 + b'\n'
    assert binascii.b2a_base64(data, wrapcol=8, newline=False) == b'\n'.join([b'eHh4eHh4'] * 10)
    assert binascii.b2a_base64(data, wrapcol=8) == b'\n'.join([b'eHh4eHh4'] * 10) + b'\n'
    # wrapcol is rounded down to a multiple of 4 (minimum 4)
    assert binascii.b2a_base64(b'\x00\x00\x00\x00\x00', wrapcol=1) == b'AAAA\nAAA=\n'
    assert binascii.b2a_base64(b'\x00\x00\x00\x00\x00', wrapcol=7) == b'AAAA\nAAA=\n'
    assert binascii.b2a_base64(b'', wrapcol=4) == b'\n'
    assert binascii.b2a_base64(b'abc', wrapcol=4) == b'YWJj\n'


def test_base64_padded():
    assert binascii.b2a_base64(b'abcde', newline=False, padded=False) == b'YWJjZGU'
    assert binascii.b2a_base64(b'abcde', newline=False) == b'YWJjZGU='
    assert binascii.b2a_base64(b'ab', newline=False, padded=False) == b'YWI'
    assert binascii.b2a_base64(b'abcde', wrapcol=4, newline=False, padded=False) == b'YWJj\nZGU'
    assert binascii.a2b_base64(b'YWJjZGU', padded=False) == b'abcde'
    assert binascii.a2b_base64(b'YWI', padded=False) == b'ab'
    # '=' is not padding when padded=False, just non-alphabet data
    assert binascii.a2b_base64(b'YWJjZGU=', padded=False) == b'abcde'
    a2b_base64_fails(b'YWJjZGU=', padded=False, strict_mode=True)
    a2b_base64_fails(b'YWJjZGU')
    a2b_base64_fails(b'YWJjZ', padded=False)


def test_base32():
    vectors = [
        (b'', b''),
        (b'f', b'MY======'),
        (b'fo', b'MZXQ===='),
        (b'foo', b'MZXW6==='),
        (b'foob', b'MZXW6YQ='),
        (b'fooba', b'MZXW6YTB'),
        (b'foobar', b'MZXW6YTBOI======'),
    ]
    for raw, enc in vectors:
        assert binascii.b2a_base32(raw) == enc
        assert binascii.a2b_base32(enc) == raw
        unpadded = enc.rstrip(b'=')
        assert binascii.b2a_base32(raw, padded=False) == unpadded
        assert binascii.a2b_base32(unpadded, padded=False) == raw
        if unpadded != enc:
            a2b_base32_fails(unpadded)
            # with padded=False, '=' is a plain non-alphabet character
            a2b_base32_fails(enc, padded=False)
            assert binascii.a2b_base32(enc, padded=False, ignorechars=b'=') == raw

    # base32hex via alphabet=
    assert binascii.b2a_base32(b'foobar', alphabet=binascii.BASE32HEX_ALPHABET) == b'CPNMUOJ1E8======'
    assert binascii.a2b_base32(b'CPNMUOJ1E8======', alphabet=binascii.BASE32HEX_ALPHABET) == b'foobar'
    expect_value_error(lambda: binascii.b2a_base32(b'foo', alphabet=b'abc'))
    expect_value_error(lambda: binascii.a2b_base32(b'foo', alphabet=b'abc'))

    # wrapcol is rounded down to a multiple of 8 (minimum 8)
    data = bytes(range(20))
    enc = binascii.b2a_base32(data)
    assert len(enc) == 32
    assert binascii.b2a_base32(data, wrapcol=8) == b'\n'.join([enc[i:i + 8] for i in range(0, 32, 8)])
    assert binascii.b2a_base32(data, wrapcol=1) == binascii.b2a_base32(data, wrapcol=8)
    assert binascii.b2a_base32(data, wrapcol=15) == binascii.b2a_base32(data, wrapcol=8)
    assert binascii.b2a_base32(data, wrapcol=16) == enc[:16] + b'\n' + enc[16:]
    assert binascii.b2a_base32(data, wrapcol=32) == enc
    assert binascii.b2a_base32(data, wrapcol=100) == enc
    assert binascii.a2b_base32(binascii.b2a_base32(data, wrapcol=8), ignorechars=b'\n') == data
    a2b_base32_fails(binascii.b2a_base32(data, wrapcol=8))

    # canonical: non-zero padding bits are rejected
    assert binascii.a2b_base32(b'MZ======') == b'f'
    assert binascii.a2b_base32(b'MY======', canonical=True) == b'f'
    expect_error(lambda: binascii.a2b_base32(b'MZ======', canonical=True))

    # malformed input
    for bad in (b'M', b'MZX', b'MZXW6Y', b'=', b'M=======', b'MZXW6YTB=', b'MY======MZXQ====', b'MZ=XW6==', b'my======'):
        a2b_base32_fails(bad)
    # excess padding can be ignored explicitly
    assert binascii.a2b_base32(b'MY=======', ignorechars=b'=') == b'f'

    input_bytes = bytes(range(256))
    assert binascii.a2b_base32(binascii.b2a_base32(input_bytes)) == input_bytes
    assert binascii.a2b_base32(binascii.b2a_base32(input_bytes, padded=False), padded=False) == input_bytes


def test_base85():
    assert binascii.b2a_base85(b'') == b''
    assert binascii.b2a_base85(b'www.python.org') == b'cXxL#aCvlSZ*DGca%T'
    assert binascii.a2b_base85(b'cXxL#aCvlSZ*DGca%T') == b'www.python.org'
    assert binascii.b2a_base85(b'\x00\x00\x00\x00') == b'00000'
    assert binascii.b2a_base85(b'\xff\xff\xff\xff') == b'|NsC0'
    assert binascii.b2a_base85(b'f') == b'W&'
    assert binascii.b2a_base85(b'f', pad=True) == b'W&i*H'
    assert binascii.a2b_base85(b'W&i*H') == b'f\x00\x00\x00'

    # z85 via alphabet= (ZeroMQ RFC 32 test vector)
    assert binascii.b2a_base85(b'\x86\x4f\xd2\x6f\xb5\x59\xf7\x5b', alphabet=binascii.Z85_ALPHABET) == b'HelloWorld'
    assert binascii.a2b_base85(b'HelloWorld', alphabet=binascii.Z85_ALPHABET) == b'\x86\x4f\xd2\x6f\xb5\x59\xf7\x5b'
    expect_value_error(lambda: binascii.b2a_base85(b'foo', alphabet=b'abc'))
    expect_value_error(lambda: binascii.a2b_base85(b'foo', alphabet=b'abc'))

    # wrapcol is rounded down to a multiple of 5 (minimum 5)
    data = bytes(range(16))
    enc = binascii.b2a_base85(data)
    assert len(enc) == 20
    assert binascii.b2a_base85(data, wrapcol=5) == b'\n'.join([enc[i:i + 5] for i in range(0, 20, 5)])
    assert binascii.b2a_base85(data, wrapcol=1) == binascii.b2a_base85(data, wrapcol=5)
    assert binascii.b2a_base85(data, wrapcol=9) == binascii.b2a_base85(data, wrapcol=5)
    assert binascii.b2a_base85(data, wrapcol=10) == enc[:10] + b'\n' + enc[10:]
    assert binascii.b2a_base85(data, wrapcol=20) == enc
    assert binascii.a2b_base85(binascii.b2a_base85(data, wrapcol=5), ignorechars=b'\n') == data
    a2b_base85_fails(binascii.b2a_base85(data, wrapcol=5))

    # canonical: partial final groups must use the encoder's padding digits
    assert binascii.a2b_base85(b'W&', canonical=True) == b'f'
    assert binascii.a2b_base85(b'W(') == b'f'
    expect_error(lambda: binascii.a2b_base85(b'W(', canonical=True))

    # malformed input
    expect_error(lambda: binascii.a2b_base85(b'~~~~~'))      # > 2**32-1
    expect_error(lambda: binascii.a2b_base85(b'a'))          # 1-char final group
    expect_error(lambda: binascii.a2b_base85(b'abcdef'))     # 1-char final group
    expect_error(lambda: binascii.a2b_base85(b'\x80'))
    expect_error(lambda: binascii.a2b_base85(b'abc de'))
    assert binascii.a2b_base85(b'abc de', ignorechars=b' ') == binascii.a2b_base85(b'abcde')

    input_bytes = bytes(range(256))
    for pad in (False, True):
        assert binascii.a2b_base85(binascii.b2a_base85(input_bytes, pad=pad)) == input_bytes
        assert binascii.a2b_base85(binascii.b2a_base85(input_bytes, pad=pad, alphabet=binascii.Z85_ALPHABET), alphabet=binascii.Z85_ALPHABET) == input_bytes


def test_ascii85():
    assert binascii.b2a_ascii85(b'') == b''
    assert binascii.b2a_ascii85(b'\x00') == b'!!'
    assert binascii.b2a_ascii85(b'\x00\x00\x00\x00') == b'z'
    assert binascii.b2a_ascii85(b'www.python.org') == b'GB\\6`E-ZP=Df.1GEb>'
    assert binascii.a2b_ascii85(b'GB\\6`E-ZP=Df.1GEb>') == b'www.python.org'
    assert binascii.b2a_ascii85(b'f') == b'Ac'
    assert binascii.b2a_ascii85(b'f', pad=True) == b'AcMf2'
    assert binascii.b2a_ascii85(b'\x00', pad=True) == b'z'

    # foldspaces
    assert binascii.b2a_ascii85(b'    ') == b'+<VdL'
    assert binascii.b2a_ascii85(b'    ', foldspaces=True) == b'y'
    assert binascii.a2b_ascii85(b'y', foldspaces=True) == b'    '
    expect_error(lambda: binascii.a2b_ascii85(b'y'))

    # adobe framing: leading '<~' optional, trailing '~>' required
    assert binascii.b2a_ascii85(b'www.python.org', adobe=True) == b'<~GB\\6`E-ZP=Df.1GEb>~>'
    assert binascii.a2b_ascii85(b'<~GB\\6`E-ZP=Df.1GEb>~>', adobe=True) == b'www.python.org'
    assert binascii.a2b_ascii85(b'GB\\6`E-ZP=Df.1GEb>~>', adobe=True) == b'www.python.org'
    assert binascii.a2b_ascii85(b'<~~>', adobe=True) == b''
    expect_error(lambda: binascii.a2b_ascii85(b'GB\\6`E-ZP=Df.1GEb>', adobe=True))
    expect_error(lambda: binascii.a2b_ascii85(b'<~', adobe=True))

    # wrapcol (exact, not rounded); '~>' is never split across lines
    assert binascii.b2a_ascii85(b'www.python.org', wrapcol=5) == b'GB\\6`\nE-ZP=\nDf.1G\nEb>'
    assert binascii.b2a_ascii85(b'hello world', adobe=True, wrapcol=5) == b'<~BOu\n!rD]j\n7BEbo\n7~>'
    assert binascii.b2a_ascii85(b'foob', adobe=True, wrapcol=7) == b'<~AoDTs\n~>'

    # whitespace is only ignored when asked for
    expect_error(lambda: binascii.a2b_ascii85(b'GB\\6`E -ZP=Df.1GEb>'))
    assert binascii.a2b_ascii85(b'GB\\6`E \n-ZP=Df.1GEb>', ignorechars=b' \n') == b'www.python.org'

    # canonical: 'z' must be used for all-zero groups, partial groups must be canonical
    assert binascii.a2b_ascii85(b'!!!!!') == b'\x00\x00\x00\x00'
    assert binascii.a2b_ascii85(b'z', canonical=True) == b'\x00\x00\x00\x00'
    expect_error(lambda: binascii.a2b_ascii85(b'!!!!!', canonical=True))
    assert binascii.a2b_ascii85(b'Ac', canonical=True) == b'f'
    assert binascii.a2b_ascii85(b'Ad') == b'f'
    expect_error(lambda: binascii.a2b_ascii85(b'Ad', canonical=True))

    # malformed input
    expect_error(lambda: binascii.a2b_ascii85(b'v'))         # outside '!'..'u'
    expect_error(lambda: binascii.a2b_ascii85(b'!z'))        # 'z' inside a group
    expect_error(lambda: binascii.a2b_ascii85(b'uuuuu'))     # > 2**32-1
    expect_error(lambda: binascii.a2b_ascii85(b'!'))         # 1-char final group

    input_bytes = bytes(range(256))
    for foldspaces in (False, True):
        for adobe in (False, True):
            for pad in (False, True):
                e = binascii.b2a_ascii85(input_bytes, foldspaces=foldspaces, adobe=adobe, pad=pad, wrapcol=40)
                assert binascii.a2b_ascii85(e, foldspaces=foldspaces, adobe=adobe, ignorechars=b'\n') == input_bytes


def test_incomplete():
    # binascii.Incomplete is a leftover from the (removed in 3.11) hqx
    # functions: CPython still exports it but never raises it anymore.
    # We mirror that: the class exists, is a distinct Exception subclass
    # from binascii.Error, and user code can raise/catch it.
    try:
        raise binascii.Incomplete("need more data")
    except binascii.Incomplete as e:
        assert str(e) == "need more data"

    # it is an Exception subclass..
    try:
        raise binascii.Incomplete("x")
    except Exception as e:
        assert str(e) == "x"

    # ..but not a binascii.Error, and vice versa
    caught = ''
    try:
        raise binascii.Incomplete("y")
    except binascii.Error:
        caught = 'error'
    except binascii.Incomplete:
        caught = 'incomplete'
    assert caught == 'incomplete'

    caught = ''
    try:
        raise binascii.Error("z")
    except binascii.Incomplete:
        caught = 'incomplete'
    except binascii.Error:
        caught = 'error'
    assert caught == 'error'

    # the a2b_* decoders raise binascii.Error (not Incomplete) on short input
    try:
        binascii.a2b_base64(b'abc')
    except binascii.Incomplete:
        assert False
    except binascii.Error:
        pass


def test_all():
    test_qp()
    test_incomplete()
    test_b2a_qp_leading_dot_at_end()
    test_uu()
    test_a2b_uu_short_input()
    test_a2b_uu_trailing_garbage_message()
    test_base64()
    test_b2a_uu_and_b2a_base64_no_signed_overflow_on_long_input()
    test_base64_strict_mode()
    test_base64_ignorechars()
    test_base64_alphabet()
    test_base64_canonical()
    test_base64_padding_errors()
    test_hex_ignorechars()
    test_hex()
    test_unhexlify_high_bit_bytes_rejected()
    test_hex_bytes_per_sep_zero()
    test_hex_bytes_per_sep_negative()
    test_hex_sep_validated_on_empty_data()
    test_crc()
    test_crc_hqx_high_bit_bytes()
    test_alphabets()
    test_b2a_base64_wrapcol()
    test_base64_padded()
    test_base32()
    test_base85()
    test_ascii85()


if __name__ == '__main__':
    test_all()
