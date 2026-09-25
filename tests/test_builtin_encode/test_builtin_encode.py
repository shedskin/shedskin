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
    except UnicodeEncodeError:
        caught += 1
    assert caught == 1


def test_decode_ascii():
    assert b'hello'.decode('ascii') == 'hello'

    caught = 0
    try:
        b'caf\xe9'.decode('ascii')
    except UnicodeDecodeError:
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
    # note: shedskin rejects unsupported handlers ('backslashreplace', ...)
    # eagerly with ValueError; cpython only looks the handler up when an
    # error occurs, so that is not asserted here


def test_error_handlers_decode():
    bs = b'a\xe2\x82b\xed\xa0\x80c\xf0\x9f\x98\xff\xc0\xafd'
    assert bs.decode('utf-8', 'ignore') == 'abcd'
    # replace: one U+FFFD per maximal subpart
    assert bs.decode('utf-8', 'replace') == 'a\ufffdb\ufffd\ufffd\ufffdc\ufffd\ufffd\ufffd\ufffdd'
    assert str(bs, 'utf-8', 'replace') == bs.decode('utf-8', 'replace')
    se = bs.decode('utf-8', 'surrogateescape')
    assert se == 'a\udce2\udc82b\udced\udca0\udc80c\udcf0\udc9f\udc98\udcff\udcc0\udcafd'
    assert se.encode('utf-8', 'surrogateescape') == bs
    assert b'\xff\x80a'.decode('ascii', 'surrogateescape').encode('ascii', 'surrogateescape') == b'\xff\x80a'
    assert b'a\xe9b'.decode('ascii', 'replace') == 'a\ufffdb'
    assert b'a\xe9b'.decode('ascii', 'ignore') == 'ab'
    assert b'\xe9t\xe9'.decode('latin-1', 'ignore') == '\xe9t\xe9'
    assert b'caf\xc3\xa9'.decode('utf-8', 'replace') == 'caf\xe9'


def test_error_handlers_encode():
    s = '\xe9\u20ac\U0001f600x'
    assert s.encode('ascii', 'ignore') == b'x'
    assert s.encode('ascii', 'replace') == b'???x'
    assert s.encode('latin-1', 'replace') == b'\xe9??x'
    assert 'a\udcffb'.encode('utf-8', 'surrogateescape') == b'a\xffb'
    assert 'a\udcffb'.encode('latin-1', 'surrogateescape') == b'a\xffb'
    assert 'a\ud800b'.encode('utf-8', 'ignore') == b'ab'
    caught = 0
    try:
        'a\udc12b'.encode('utf-8', 'surrogateescape')  # below U+DC80: no byte
    except UnicodeEncodeError as e:
        assert (e.start, e.end) == (1, 2)
        caught += 1
    assert caught == 1


def test_cp1252():
    allb = bytes([i for i in range(256) if i not in (0x81, 0x8d, 0x8f, 0x90, 0x9d)])
    u = allb.decode('cp1252')
    assert len(u) == 251
    assert u.encode('cp1252') == allb
    assert b'\x80\x93q\x94\x96\x85\x9f'.decode('windows-1252') == '\u20ac\u201cq\u201d\u2013\u2026\u0178'
    assert '\u20ac\xe9'.encode('1252') == b'\x80\xe9'
    assert b'\x00a'.decode('cp1252') == '\x00a'
    assert b'a\x81b\x9d\x80'.decode('cp1252', 'replace') == 'a\ufffdb\ufffd\u20ac'
    assert b'a\x81b'.decode('cp1252', 'ignore') == 'ab'
    assert b'a\x81b'.decode('cp1252', 'surrogateescape') == 'a\udc81b'
    assert 'a\u20ac\u0100b'.encode('cp1252', 'replace') == b'a\x80?b'
    assert 'a\udc81b'.encode('cp1252', 'surrogateescape') == b'a\x81b'
    caught = 0
    try:
        b'x\x90'.decode('cp1252')
    except UnicodeDecodeError as e:
        assert e.encoding == 'charmap'
        assert (e.start, e.end) == (1, 2)
        assert e.reason == 'character maps to <undefined>'
        caught += 1
    try:
        'a\u20ac\u0100\u0101b'.encode('cp1252')
    except UnicodeEncodeError as e:
        assert e.encoding == 'charmap'
        assert (e.start, e.end) == (2, 4)
        caught += 1
    assert caught == 2


def test_errors_keyword_only():
    # 'errors' passed without 'encoding' must not end up as the encoding
    assert 'x'.encode(errors='strict') == b'x'
    assert b'x'.decode(errors='strict') == 'x'
    assert b'caf\xc3\xa9'.decode(errors='strict') == 'caf\xe9'


def test_str_decode():
    b = b'caf\xc3\xa9'
    assert str(b, 'utf-8') == 'caf\xe9'
    assert str(b, encoding='utf-8') == 'caf\xe9'
    assert str(b, 'utf-8', 'strict') == 'caf\xe9'
    assert str(object=b, encoding='utf-8') == 'caf\xe9'
    assert str(b'caf\xe9', 'latin-1') == 'caf\xe9'
    assert str(b'hello', 'ascii') == 'hello'
    assert str(b'', 'utf-8') == ''
    assert str(bytearray(b'caf\xc3\xa9'), 'utf-8') == 'caf\xe9'
    # note: str(b, errors=..) without encoding, and str(encoding=..), are
    # not supported (builtin defaults are skipped, shifting the arguments)

    # without encoding/errors, str() still gives the repr
    assert str(b'ab') == "b'ab'"
    assert list(map(str, [1, 2])) == ['1', '2']

    caught = 0
    try:
        str(b'caf\xe9', 'ascii')
    except UnicodeDecodeError:
        caught += 1
    try:
        str(b'x', 'bogus')
    except LookupError:
        caught += 1
    assert caught == 2


def test_literal_consistency():
    # '\xe9' is the same string as 'é', also in its encoded form
    assert '\xe9' == '\u00e9'
    assert len('\xe9'.encode('utf-8')) == 2
    assert len('\xe9'.encode('latin-1')) == 1


def test_bytearray_decode():
    assert bytearray(b'caf\xc3\xa9').decode() == 'caf\xe9'
    assert bytearray(b'caf\xe9').decode('latin-1') == 'caf\xe9'


def test_unicode_error_hierarchy():
    # UnicodeError subclasses ValueError; the concrete errors subclass UnicodeError
    caught = 0
    try:
        b'\xff'.decode()
    except UnicodeError:
        caught += 1
    try:
        '\xe9'.encode('ascii')
    except UnicodeError:
        caught += 1
    assert caught == 2

    caught = 0
    try:
        b'\xff'.decode()
    except ValueError:
        caught += 1
    try:
        '\xe9'.encode('ascii')
    except ValueError:
        caught += 1
    assert caught == 2

    # a decode error is not an encode error (and vice versa)
    caught = 0
    try:
        try:
            b'\xff'.decode()
        except UnicodeEncodeError:
            assert False
    except UnicodeDecodeError:
        caught += 1
    try:
        try:
            '\xe9'.encode('ascii')
        except UnicodeDecodeError:
            assert False
    except UnicodeEncodeError:
        caught += 1
    assert caught == 2


def test_decode_error_attrs():
    data = b'ab\xffcd'
    try:
        data.decode()
        assert False
    except UnicodeDecodeError as e:
        assert e.encoding == 'utf-8'
        assert e.object == data
        assert e.start == 2
        assert e.end == 3
        assert e.reason == 'invalid start byte'
        assert str(e) == "'utf-8' codec can't decode byte 0xff in position 2: invalid start byte"
        assert repr(e) == "UnicodeDecodeError('utf-8', b'ab\\xffcd', 2, 3, 'invalid start byte')"

    # start byte plus valid continuation bytes are reported as one range
    # (parallel lists: shedskin has no 4-element mixed-type tuples)
    datas = [b'\xe2\x28\xa1', b'\xe2\x82\x28', b'\xe0\x80', b'\xed\xa0\x80', b'\xf4\x90\x80\x80', b'\xc0\xaf', b'ab\xe2\x82', b'\xe2', b'\xf0\x9f\x98']
    ranges = [(0, 1), (0, 2), (0, 1), (0, 1), (0, 1), (0, 1), (2, 4), (0, 1), (0, 3)]
    reasons = ['invalid continuation byte'] * 5 + ['invalid start byte'] + ['unexpected end of data'] * 3
    for i in range(len(datas)):
        try:
            datas[i].decode('utf-8')
            assert False
        except UnicodeDecodeError as e:
            assert (e.start, e.end) == ranges[i]
            assert e.reason == reasons[i]
    try:
        b'ab\xe2\x82'.decode()
        assert False
    except UnicodeDecodeError as e:
        assert str(e) == "'utf-8' codec can't decode bytes in position 2-3: unexpected end of data"

    try:
        b'caf\xe9\xe9'.decode('ascii')
        assert False
    except UnicodeDecodeError as e:
        assert e.encoding == 'ascii'
        assert (e.start, e.end) == (3, 4)  # ascii decode does not coalesce
        assert e.reason == 'ordinal not in range(128)'
        assert str(e) == "'ascii' codec can't decode byte 0xe9 in position 3: ordinal not in range(128)"


def test_encode_error_attrs():
    s = 'caf\xe9'
    try:
        s.encode('ascii')
        assert False
    except UnicodeEncodeError as e:
        assert e.encoding == 'ascii'
        assert e.object == s
        assert (e.start, e.end) == (3, 4)
        assert e.reason == 'ordinal not in range(128)'
        assert str(e) == "'ascii' codec can't encode character '\\xe9' in position 3: ordinal not in range(128)"
        assert repr(e) == "UnicodeEncodeError('ascii', 'caf\xe9', 3, 4, 'ordinal not in range(128)')"

    # consecutive unencodable characters form one range, as in cpython
    try:
        'ab\xe9\xe9c'.encode('ascii')
        assert False
    except UnicodeEncodeError as e:
        assert (e.start, e.end) == (2, 4)
        assert str(e) == "'ascii' codec can't encode characters in position 2-3: ordinal not in range(128)"
    try:
        '\u20ac\u20acx'.encode('latin-1')
        assert False
    except UnicodeEncodeError as e:
        assert e.encoding == 'latin-1'
        assert (e.start, e.end) == (0, 2)
        assert e.reason == 'ordinal not in range(256)'
    try:
        '\u20ac'.encode('latin-1')
        assert False
    except UnicodeEncodeError as e:
        assert str(e) == "'latin-1' codec can't encode character '\\u20ac' in position 0: ordinal not in range(256)"
    try:
        '\U0001f600'.encode('ascii')
        assert False
    except UnicodeEncodeError as e:
        assert str(e) == "'ascii' codec can't encode character '\\U0001f600' in position 0: ordinal not in range(128)"
    try:
        'x\ud800\ud800y'.encode()
        assert False
    except UnicodeEncodeError as e:
        assert e.encoding == 'utf-8'
        assert (e.start, e.end) == (1, 3)
        assert e.reason == 'surrogates not allowed'
        assert str(e) == "'utf-8' codec can't encode characters in position 1-2: surrogates not allowed"


def test_unicode_error_construct():
    # the exceptions can also be raised from python code
    caught = 0
    try:
        raise UnicodeDecodeError('utf-8', b'\xff', 0, 1, 'bad')
    except UnicodeDecodeError as e1:
        assert str(e1) == "'utf-8' codec can't decode byte 0xff in position 0: bad"
        caught += 1
    try:
        raise UnicodeEncodeError('ascii', 'x\xe9y', 0, 3, 'bad')
    except UnicodeEncodeError as e2:
        assert str(e2) == "'ascii' codec can't encode characters in position 0-2: bad"
        assert repr(e2) == "UnicodeEncodeError('ascii', 'x\xe9y', 0, 3, 'bad')"
        caught += 1
    try:
        raise UnicodeTranslateError('x\xe9y', 1, 2, 'bad')
    except UnicodeTranslateError as e3:
        assert e3.object == 'x\xe9y'
        assert (e3.start, e3.end) == (1, 2)
        assert e3.reason == 'bad'
        assert str(e3) == "can't translate character '\\xe9' in position 1: bad"
        assert repr(e3) == "UnicodeTranslateError('x\xe9y', 1, 2, 'bad')"
        caught += 1
    try:
        raise UnicodeTranslateError('xy', 0, 2, 'bad')
    except UnicodeError as e4:
        assert str(e4) == "can't translate characters in position 0-1: bad"
        caught += 1
    try:
        raise UnicodeError('plain')
    except ValueError as e5:
        assert str(e5) == 'plain'
        assert repr(e5) == "UnicodeError('plain')"
        caught += 1
    assert caught == 5


def test_surrogate_literals():
    # a surrogate code point in a str literal survives translation as one
    # code point (wtf-8 across the c++ boundary), and only fails at encode
    s = 'x\ud800\udfffy'
    assert len(s) == 4
    assert [ord(c) for c in s] == [120, 0xd800, 0xdfff, 121]
    assert s == 'x' + chr(0xd800) + chr(0xdfff) + 'y'
    caught = 0
    try:
        s.encode()
    except UnicodeEncodeError as e:
        assert (e.start, e.end) == (1, 3)
        caught += 1
    assert caught == 1


def test_cp1250_cp1251():
    for cp, undef in (('cp1250', [0x81, 0x83, 0x88, 0x90, 0x98]), ('windows-1251', [0x98])):
        allb = bytes([i for i in range(256) if i not in undef])
        u = allb.decode(cp)
        assert len(u) == 256 - len(undef)
        assert u.encode(cp) == allb
    assert 'Za\u017c\xf3\u0142\u0107'.encode('1250') == b'Za\xbf\xf3\xb3\xe6'
    assert '\u041f\u0440\u0438'.encode('cp1251') == b'\xcf\xf0\xe8'
    assert b'\xcf\xf0\xe8'.decode('1251') == '\u041f\u0440\u0438'
    assert b'a\x98b'.decode('cp1251', 'replace') == 'a\ufffdb'
    assert 'a\xe9b'.encode('cp1251', 'replace') == b'a?b'
    caught = 0
    try:
        b'a\x98b'.decode('cp1251')
    except UnicodeDecodeError as e:
        assert e.encoding == 'charmap' and (e.start, e.end) == (1, 2)
        caught += 1
    try:
        'a\u20ac\u0100b'.encode('cp1250')
    except UnicodeEncodeError as e:
        assert e.encoding == 'charmap' and (e.start, e.end) == (2, 3)
        caught += 1
    assert caught == 2


def test_utf8_sig():
    assert b'\xef\xbb\xbfab'.decode('utf-8-sig') == 'ab'
    assert b'ab'.decode('UTF_8_SIG') == 'ab'
    assert b''.decode('utf-8-sig') == ''
    assert b'\xef\xbb'.decode('utf-8-sig', 'replace') == '\ufffd'
    assert str(b'\xef\xbb\xbfx', 'utf-8-sig') == 'x'
    assert 'ab'.encode('utf-8-sig') == b'\xef\xbb\xbfab'
    assert ''.encode('utf-8-sig') == b'\xef\xbb\xbf'
    caught = 0
    try:
        b'\xef\xbb\xbfa\xff'.decode('utf-8-sig')
    except UnicodeDecodeError as e:
        assert e.encoding == 'utf-8' and (e.start, e.end) == (1, 2)  # after the bom, as cpython
        caught += 1
    assert caught == 1


def test_unknown_error_handler():
    # an unknown handler name is a LookupError (a ValueError is not caught)
    for i in range(2):
        error = ''
        try:
            if i == 0: '\xe9'.encode('ascii', 'bogus')
            else: b'\xe9'.decode('ascii', 'bogus')
        except LookupError as e:
            error = str(e)
        assert error == "unknown error handler name 'bogus'"


def test_all():
    test_unknown_error_handler()
    test_encode_utf8()
    test_decode_utf8()
    test_roundtrip()
    test_encode_ascii()
    test_decode_ascii()
    test_latin1()
    test_decode_errors()
    test_encoding_lookup()
    test_errors_arg()
    test_errors_keyword_only()
    test_error_handlers_decode()
    test_error_handlers_encode()
    test_cp1252()
    test_cp1250_cp1251()
    test_utf8_sig()
    test_str_decode()
    test_literal_consistency()
    test_bytearray_decode()
    test_unicode_error_hierarchy()
    test_decode_error_attrs()
    test_encode_error_attrs()
    test_unicode_error_construct()
    test_surrogate_literals()


if __name__ == '__main__':
    test_all()
