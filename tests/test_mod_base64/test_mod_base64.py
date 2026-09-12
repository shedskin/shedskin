import base64
import binascii
import io


def test_basic():
    input_bytes = bytes(range(256))

    e = base64.b64encode(input_bytes)
    assert e == b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
    assert base64.b64decode(e) == input_bytes

    e = base64.standard_b64encode(input_bytes)
    assert e == b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
    assert base64.standard_b64decode(e) == input_bytes

    e = base64.urlsafe_b64encode(input_bytes)
    assert e == b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0-P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn-AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq-wsbKztLW2t7i5uru8vb6_wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t_g4eLj5OXm5-jp6uvs7e7v8PHy8_T19vf4-fr7_P3-_w=='
    assert base64.urlsafe_b64decode(e) == input_bytes


def test_altchars():
    input_bytes = bytes(range(256))

    a1 = base64.b64encode(input_bytes)
    assert a1 == b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='

    a2 = base64.b64encode(input_bytes, altchars=b'*?')
    assert a2 == b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0*P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn*AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq*wsbKztLW2t7i5uru8vb6?wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t?g4eLj5OXm5*jp6uvs7e7v8PHy8?T19vf4*fr7?P3*?w=='

    assert base64.b64decode(a1) == input_bytes
    assert base64.b64decode(a2, altchars=b'*?') == input_bytes


# regression test: passing altchars must *add* '-'/'_' as extra encodings
# of 62/63, not make the standard '+'/'/' invalid. CPython's base64.py
# implements altchars by translating them onto '+'/'/' before decoding,
# which leaves any literal '+'/'/' already in the string untouched (and
# still valid data) -- so urlsafe_b64decode (and b64decode with an
# explicit altchars=) must still accept plain '+' and '/' characters.
def test_altchars_preserves_standard_chars():
    # data chosen so the standard b64 alphabet encodes it using '+' and '/'
    data = bytes([251, 255, 191, 62])
    enc = base64.b64encode(data)
    assert enc == b'+/+/Pg=='

    # urlsafe_b64decode must still decode this correctly even though it
    # contains literal '+'/'/' rather than the url-safe '-'/'_'
    assert base64.urlsafe_b64decode(enc) == data

    # same via explicit altchars=
    assert base64.b64decode(enc, altchars=b'-_') == data

    # sanity: '-'/'_' still work as before
    urlsafe_enc = base64.urlsafe_b64encode(data)
    assert urlsafe_enc == b'-_-_Pg=='
    assert base64.urlsafe_b64decode(urlsafe_enc) == data

    # and a mix of both '+/' and '-_' in the same string must decode fine
    mixed = b'+/-_Pg=='
    assert base64.b64decode(mixed, altchars=b'-_') == data


def test_name():
    assert base64.__name__ == 'base64'


def test_validate():
    good = base64.b64encode(b'Hello!')
    assert base64.b64decode(good, validate=True) == b'Hello!'

    # non-alphabet characters raise when validate=True ...
    bad = b'SGVsbG8h@#$%'
    ok = False
    try:
        base64.b64decode(bad, validate=True)
    except binascii.Error:
        ok = True
    assert ok

    # ... but are tolerated when validate=False (the default)
    assert base64.b64decode(bad, validate=False) == b'Hello!'
    assert base64.b64decode(bad) == b'Hello!'


def test_b16():
    input_bytes = bytes(range(256))
    e = base64.b16encode(input_bytes)
    assert e == binascii.hexlify(input_bytes).upper()
    assert base64.b16decode(e) == input_bytes
    assert base64.b16decode(e.lower(), casefold=True) == input_bytes

    ok = False
    try:
        base64.b16decode(e.lower())
    except binascii.Error:
        ok = True
    assert ok


# regression test: altchars must be exactly 2 bytes, like CPython's
# `assert len(altchars) == 2, repr(altchars)` in base64.py. Without this
# check, a too-short altchars caused an out-of-bounds vector read and a
# too-long one was silently (and incorrectly) truncated.
#
# Note: CPython's base64.py enforces this with a plain `assert`, which
# raises AssertionError (and can be compiled away with -O); shedskin
# raises ValueError instead, which is deliberate and more robust. Both
# are accepted here so this test runs the same under CPython and
# shedskin.
def test_altchars_bad_length():
    for bad in (b'', b'-', b'-_-'):
        ok = False
        try:
            base64.b64encode(b'hello world', altchars=bad)
        except (AssertionError, ValueError):
            ok = True
        assert ok

        ok = False
        try:
            base64.b64decode(b'aGVsbG8gd29ybGQ=', altchars=bad)
        except (AssertionError, ValueError):
            ok = True
        assert ok


# regression test: b64decode must reject truncated/incorrectly padded
# input instead of silently returning wrong (truncated or fabricated)
# bytes. Mirrors CPython's binascii.Error('Incorrect padding') and
# binascii.Error('Invalid base64-encoded string: ...') behavior.
def test_decode_bad_padding():
    # b'QQ': 2 chars, no padding at all
    # b'QQ=': 2 chars, only one pad (needs two)
    # b'AA': 2 chars decode to < 1 full byte
    # b'A': single dangling char, never valid
    # b'A=': single dangling char + one pad
    for bad in (b'QQ', b'QQ=', b'AA', b'A', b'A='):
        ok = False
        try:
            base64.b64decode(bad)
        except binascii.Error:
            ok = True
        assert ok

    # well-formed padding must still decode correctly (regression check
    # for the fix itself: an earlier version of this fix broke this case)
    assert base64.b64decode(b'QQ==') == b'A'
    assert base64.b64decode(b'QUJD') == b'ABC'
    assert base64.b64decode(b'QUJ=') == b'AB'
    assert base64.b64decode(b'====') == b''
    assert base64.b64decode(b'') == b''


# regression test for a global-buffer-overflow (OOB read past the
# empty string literal used to preallocate output buffers) that
# AddressSanitizer catches on completely ordinary encode/decode calls,
# with no altchars or adversarial input needed.
def test_asan_regression():
    for n in (0, 1, 2, 3, 4, 5, 16, 45, 60, 61, 62, 63, 64, 100, 1000):
        data = bytes((i * 37) % 256 for i in range(n))
        e = base64.b64encode(data)
        assert base64.b64decode(e) == data
        h = base64.b16encode(data)
        assert base64.b16decode(h) == data


# note: older CPython versions raise ValueError from the pure-Python
# a85decode/b85decode; shedskin (like CPython 3.15) raises binascii.Error
def expect_error(f):
    ok = False
    try:
        f()
    except (binascii.Error, ValueError):
        ok = True
    assert ok


def b32decode_fails(s):
    ok = False
    try:
        base64.b32decode(s)
    except binascii.Error:
        ok = True
    assert ok


# RFC 4648 section 10 test vectors
def test_b32():
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
        assert base64.b32encode(raw) == enc
        assert base64.b32decode(enc) == raw
        # lowercase input is only accepted with casefold=True
        assert base64.b32decode(enc.lower(), casefold=True) == raw
        if raw:
            b32decode_fails(enc.lower())

    # RFC 4648 section 2.4 zero/one mapping
    assert base64.b32decode(b'MZXW6YTB0I======', map01=b'I') == b'foobar'
    assert base64.b32decode(b'MZXW6YTB01======', map01=b'I') == b'foobar'
    assert base64.b32decode(b'ME======', map01=b'L') == b'a'
    assert base64.b32decode(b'ME======', map01=b'I') == b'a'
    assert base64.b32decode(b'M1======', map01=b'L') == base64.b32decode(b'ML======')

    input_bytes = bytes(range(256))
    e = base64.b32encode(input_bytes)
    assert len(e) % 8 == 0
    assert base64.b32decode(e) == input_bytes

    # bad padding / non-alphabet characters
    for bad in (b'MY', b'MY=', b'M=======', b'MZXW6YTB=', b'my======', b'MZXW6YQ=MY======'):
        b32decode_fails(bad)


def test_b32hex():
    vectors = [
        (b'', b''),
        (b'f', b'CO======'),
        (b'fo', b'CPNG===='),
        (b'foo', b'CPNMU==='),
        (b'foob', b'CPNMUOG='),
        (b'fooba', b'CPNMUOJ1'),
        (b'foobar', b'CPNMUOJ1E8======'),
    ]
    for raw, enc in vectors:
        assert base64.b32hexencode(raw) == enc
        assert base64.b32hexdecode(enc) == raw
        assert base64.b32hexdecode(enc.lower(), casefold=True) == raw

    input_bytes = bytes(range(256))
    e = base64.b32hexencode(input_bytes)
    assert base64.b32hexdecode(e) == input_bytes
    # base32hex output is sortable like the input
    assert base64.b32hexencode(b'\x00') < base64.b32hexencode(b'\x01') < base64.b32hexencode(b'\xff')

    # standard base32 alphabet chars 'W'..'Z' are invalid in base32hex
    expect_error(lambda: base64.b32hexdecode(b'MZXW6==='))


def test_a85():
    assert base64.a85encode(b'') == b''
    assert base64.a85encode(b'\x00') == b'!!'
    assert base64.a85encode(b'\x00\x00\x00\x00') == b'z'
    assert base64.a85encode(b'www.python.org') == b'GB\\6`E-ZP=Df.1GEb>'
    assert base64.a85encode(b'f') == b'Ac'
    assert base64.a85encode(b'fo') == b'Ao@'
    assert base64.a85encode(b'foo') == b'AoDS'
    assert base64.a85encode(b'foob') == b'AoDTs'
    assert base64.a85encode(b'foobar') == b'AoDTs@<)'

    # foldspaces: four spaces become 'y'
    assert base64.a85encode(b'    ') == b'+<VdL'
    assert base64.a85encode(b'    ', foldspaces=True) == b'y'
    assert base64.a85decode(b'y', foldspaces=True) == b'    '
    expect_error(lambda: base64.a85decode(b'y'))

    # pad: final group is fully retained
    assert base64.a85encode(b'f', pad=True) == b'AcMf2'
    assert base64.a85encode(b'\x00', pad=True) == b'z'
    assert base64.a85decode(b'AcMf2') == b'f\x00\x00\x00'

    # adobe framing
    assert base64.a85encode(b'www.python.org', adobe=True) == b'<~GB\\6`E-ZP=Df.1GEb>~>'
    assert base64.a85decode(b'<~GB\\6`E-ZP=Df.1GEb>~>', adobe=True) == b'www.python.org'
    assert base64.a85decode(b'GB\\6`E-ZP=Df.1GEb>~>', adobe=True) == b'www.python.org'
    expect_error(lambda: base64.a85decode(b'GB\\6`E-ZP=Df.1GEb>', adobe=True))

    # wrapcol
    assert base64.a85encode(b'www.python.org', wrapcol=5) == b'GB\\6`\nE-ZP=\nDf.1G\nEb>'
    assert base64.a85encode(b'hello world', adobe=True, wrapcol=5) == b'<~BOu\n!rD]j\n7BEbo\n7~>'
    # the closing '~>' is never split across lines
    assert base64.a85encode(b'foob', adobe=True, wrapcol=7) == b'<~AoDTs\n~>'

    # whitespace in the input is ignored by default
    assert base64.a85decode(b'GB\\6`E-ZP=Df.1GEb>') == b'www.python.org'
    assert base64.a85decode(b'GB\\6`E \n\t-ZP=Df.1GE\rb>') == b'www.python.org'
    assert base64.a85decode(b'GB\\6`E-ZP=Df.1GEb>', ignorechars=b'') == b'www.python.org'
    expect_error(lambda: base64.a85decode(b'GB\\6`E -ZP=Df.1GEb>', ignorechars=b''))

    # invalid input
    expect_error(lambda: base64.a85decode(b'v'))         # outside '!'..'u'
    expect_error(lambda: base64.a85decode(b'!z'))        # 'z' inside a group
    expect_error(lambda: base64.a85decode(b'uuuuu'))     # > 2**32-1

    input_bytes = bytes(range(256))
    for foldspaces in (False, True):
        for adobe in (False, True):
            for pad in (False, True):
                e = base64.a85encode(input_bytes, foldspaces=foldspaces, adobe=adobe, pad=pad, wrapcol=40)
                assert base64.a85decode(e, foldspaces=foldspaces, adobe=adobe) == input_bytes


def test_b85():
    assert base64.b85encode(b'') == b''
    assert base64.b85encode(b'\x00') == b'00'
    assert base64.b85encode(b'\x00\x00\x00\x00') == b'00000'
    assert base64.b85encode(b'www.python.org') == b'cXxL#aCvlSZ*DGca%T'
    assert base64.b85encode(b'f') == b'W&'
    assert base64.b85encode(b'foobar') == b'W^Zp|VR8'
    assert base64.b85encode(b'f', pad=True) == b'W&i*H'
    assert base64.b85decode(b'W&i*H') == b'f\x00\x00\x00'
    assert base64.b85decode(b'cXxL#aCvlSZ*DGca%T') == b'www.python.org'

    expect_error(lambda: base64.b85decode(b'~~~~~'))    # > 2**32-1
    expect_error(lambda: base64.b85decode(b'\x80'))
    expect_error(lambda: base64.b85decode(b'abc de'))

    input_bytes = bytes(range(256))
    for pad in (False, True):
        e = base64.b85encode(input_bytes, pad=pad)
        assert base64.b85decode(e) == input_bytes


def test_z85():
    # ZeroMQ RFC 32 test vector
    assert base64.z85encode(b'\x86\x4f\xd2\x6f\xb5\x59\xf7\x5b') == b'HelloWorld'
    assert base64.z85decode(b'HelloWorld') == b'\x86\x4f\xd2\x6f\xb5\x59\xf7\x5b'
    assert base64.z85encode(b'') == b''
    assert base64.z85encode(b'www.python.org') == b'CxXl-AcVLsz/dgCA+t'
    assert base64.z85decode(b'CxXl-AcVlsz*dgCA%t') == b'www.pyk\xc6ow\x8d\\s\x06'
    assert base64.z85encode(b'f', pad=True) == b'w=I/h'

    input_bytes = bytes(range(256))
    for pad in (False, True):
        e = base64.z85encode(input_bytes, pad=pad)
        assert base64.z85decode(e) == input_bytes

    expect_error(lambda: base64.z85decode(b'HelloWorl~'))   # '~' not in Z85 alphabet


def test_encodebytes():
    assert base64.encodebytes(b'') == b''
    assert base64.encodebytes(b'www.python.org') == b'd3d3LnB5dGhvbi5vcmc=\n'
    assert base64.encodebytes(b'a') == b'YQ==\n'
    assert base64.encodebytes(b'ab') == b'YWI=\n'
    assert base64.encodebytes(b'abc') == b'YWJj\n'
    assert base64.encodebytes(b'x' * 58) == b'eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4\neA==\n'

    input_bytes = bytes(range(256))
    e = base64.encodebytes(input_bytes)
    lines = e.split(b'\n')
    assert e.endswith(b'\n')
    for line in lines[:-2]:
        assert len(line) == 76
    assert base64.decodebytes(e) == input_bytes
    assert base64.decodebytes(b'd3d3LnB5dGhvbi5vcmc=\n') == b'www.python.org'
    assert base64.decodebytes(b'') == b''


def test_stream_encode_decode():
    data = bytes(range(256)) * 3
    inp = io.BytesIO(data)
    out = io.BytesIO()
    base64.encode(inp, out)
    encoded = out.getvalue()
    assert encoded == base64.encodebytes(data)
    assert encoded.endswith(b'\n')

    inp = io.BytesIO(encoded)
    out = io.BytesIO()
    base64.decode(inp, out)
    assert out.getvalue() == data

    # empty input yields empty output
    out = io.BytesIO()
    base64.encode(io.BytesIO(b''), out)
    assert out.getvalue() == b''
    out = io.BytesIO()
    base64.decode(io.BytesIO(b''), out)
    assert out.getvalue() == b''


def test_all():
    test_basic()
    test_altchars()
    test_altchars_preserves_standard_chars()
    test_altchars_bad_length()
    test_name()
    test_validate()
    test_decode_bad_padding()
    test_b16()
    test_asan_regression()
    test_b32()
    test_b32hex()
    test_a85()
    test_b85()
    test_z85()
    test_encodebytes()
    test_stream_encode_decode()


if __name__ == '__main__':
    test_all()
