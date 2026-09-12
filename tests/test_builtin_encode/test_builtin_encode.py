def test_encode_utf8():
    assert 'hello'.encode() == b'hello'
    assert 'hello'.encode('utf-8') == b'hello'
    assert 'hello'.encode('utf8') == b'hello'
    assert 'hello'.encode('UTF-8') == b'hello'
    assert ''.encode() == b''

    assert 'h\xe9llo'.encode() == b'h\xc3\xa9llo'
    assert 'h\u20acllo'.encode() == b'h\xe2\x82\xacllo'
    assert '\U0001f600'.encode() == b'\xf0\x9f\x98\x80'
    assert '\xe9'.encode('utf-8') == b'\xc3\xa9'


def test_decode_utf8():
    assert b'hello'.decode() == 'hello'
    assert b'hello'.decode('utf-8') == 'hello'
    assert b''.decode() == ''

    assert b'h\xc3\xa9llo'.decode() == 'h\xe9llo'
    assert b'h\xe2\x82\xacllo'.decode() == 'h\u20acllo'
    assert b'\xf0\x9f\x98\x80'.decode() == '\U0001f600'


def test_roundtrip():
    for s in ['', 'plain ascii', 'caf\xe9', '\u20ac\u6f22\u5b57', 'mixed \xe9 \u20ac \U0001f600']:
        assert s.encode('utf-8').decode('utf-8') == s


def test_encode_ascii():
    assert 'hello'.encode('ascii') == b'hello'
    assert 'hello'.encode('us-ascii') == b'hello'

    caught = 0
    try:
        'caf\xe9'.encode('ascii')
    except ValueError:  # UnicodeEncodeError, eventually
        caught += 1
    assert caught == 1


def test_decode_ascii():
    assert b'hello'.decode('ascii') == 'hello'

    caught = 0
    try:
        b'caf\xe9'.decode('ascii')
    except ValueError:  # UnicodeDecodeError, eventually
        caught += 1
    assert caught == 1


def test_latin1():
    assert 'caf\xe9'.encode('latin-1') == b'caf\xe9'
    assert 'caf\xe9'.encode('latin1') == b'caf\xe9'
    assert 'caf\xe9'.encode('iso-8859-1') == b'caf\xe9'
    assert b'caf\xe9'.decode('latin-1') == 'caf\xe9'

    # every byte value roundtrips through latin-1
    all_bytes = bytes(range(256))
    assert all_bytes.decode('latin-1').encode('latin-1') == all_bytes

    # code points above 0xff don't fit
    caught = 0
    try:
        '\u20ac'.encode('latin-1')
    except ValueError:
        caught += 1
    assert caught == 1


def test_decode_errors():
    caught = 0
    try:
        b'\xff'.decode('utf-8')  # invalid start byte
    except ValueError:
        caught += 1
    try:
        b'ab\xe2\x82'.decode()  # truncated sequence
    except ValueError:
        caught += 1
    try:
        b'\xed\xa0\x80'.decode()  # surrogate
    except ValueError:
        caught += 1
    assert caught == 3


def test_encoding_lookup():
    caught = 0
    try:
        'x'.encode('utf-99')
    except LookupError:
        caught += 1
    try:
        b'x'.decode('bogus')
    except LookupError:
        caught += 1
    assert caught == 2


def test_errors_arg():
    assert 'x'.encode('utf-8', 'strict') == b'x'
    assert b'x'.decode('utf-8', 'strict') == 'x'
    assert 'x'.encode(encoding='ascii', errors='strict') == b'x'
    # note: shedskin rejects other handlers ('replace', ...) eagerly with
    # ValueError; cpython only looks the handler up when an error occurs,
    # so that is not asserted here


def test_literal_consistency():
    # '\xe9' is the same string as 'é', also in its encoded form
    assert '\xe9' == '\u00e9'
    assert len('\xe9'.encode('utf-8')) == 2
    assert len('\xe9'.encode('latin-1')) == 1


def test_bytearray_decode():
    assert bytearray(b'caf\xc3\xa9').decode() == 'caf\xe9'
    assert bytearray(b'caf\xe9').decode('latin-1') == 'caf\xe9'


def test_all():
    test_encode_utf8()
    test_decode_utf8()
    test_roundtrip()
    test_encode_ascii()
    test_decode_ascii()
    test_latin1()
    test_decode_errors()
    test_encoding_lookup()
    test_errors_arg()
    test_literal_consistency()
    test_bytearray_decode()


if __name__ == '__main__':
    test_all()
