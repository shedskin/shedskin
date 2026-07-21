import io
import os


def test_io_from_file():
    if os.path.exists("testdata"):
        testdata = "testdata"
    elif os.path.exists("../testdata"):
        testdata = "../testdata"
    else:
        testdata = "../../testdata"

    datafile = os.path.join(testdata, "test_io.txt")

    with open(datafile, "rb") as f:
        sio = io.BytesIO(f.read())
        lines = sio.readlines()
        assert len(lines) == 6

def test_io_read_from_binary_string():
        sio = io.BytesIO(b"blaat")
        assert sio.seek(-3, 2) == 2
        assert sio.read() == b'aat'

def test_io_write_to_binary_string():
        sio = io.BytesIO()
        assert sio.tell() == 0
        assert sio.write(b"hallo\njoh") == 9
        assert sio.tell() == 9
        assert sio.seek(0, 0) == 0
        assert sio.tell() == 0
        assert sio.readlines() == [b'hallo\n', b'joh']
        assert sio.tell() == 9
        assert sio.seek(0, 0) == 0
        assert sio.tell() == 0
        assert sio.write(b"hoi") == 3
        assert sio.tell() == 3
        assert sio.readlines() == [b'lo\n', b'joh']
        assert sio.tell() == 9


def test_stringio():
    s = io.StringIO()
    assert s.getvalue() == ''

    s = io.StringIO()
    print('bert', file=s, end='')
    assert s.getvalue() == 'bert'

    s = io.StringIO()
    print('aa', file=s)
    print('bb', file=s)
    assert s.getvalue() == 'aa\nbb\n'

    s = io.StringIO(initial_value='hop')
    s.seek(0)
    assert s.read() == 'hop'

    s = io.StringIO(initial_value='empty')
    print('hopp', file=s)
    s.seek(0)
    assert s.read() == 'hopp\n'


def test_bytesio():
    b = io.BytesIO()
    assert b.getvalue() == b''

    b = io.BytesIO(initial_bytes=b'hap')
    assert b.getvalue() == b'hap'

    b = io.BytesIO(initial_bytes=b'hap')
    b.write(b'hup')
    b.seek(0)
    assert b.read() == b'hup'


def _maybe_none_bytes(flag):
    if flag:
        return b'hallo'
    return None


def _maybe_none_str(flag):
    if flag:
        return 'hallo'
    return None


def test_bytesio_write_none():
    # write(None) must raise TypeError, not crash (regression test for a
    # null-pointer dereference that previously segfaulted here)
    b = io.BytesIO()
    data = _maybe_none_bytes(False)
    raised = False
    try:
        b.write(data)
    except TypeError:
        raised = True
    assert raised
    # BytesIO must still be usable afterwards
    assert b.write(b'ok') == 2
    b.seek(0)
    assert b.read() == b'ok'


def test_stringio_write_none():
    s = io.StringIO()
    data = _maybe_none_str(False)
    raised = False
    try:
        s.write(data)
    except TypeError:
        raised = True
    assert raised
    # StringIO must still be usable afterwards
    assert s.write('ok') == 2
    s.seek(0)
    assert s.read() == 'ok'


def test_bytesio_write_past_end():
    # seeking past the current end and then writing must zero-pad the gap,
    # not crash (regression test for an out-of-range exception previously
    # thrown by std::string::insert when pos > buffer size)
    b = io.BytesIO()
    b.seek(5)
    assert b.write(b'hi') == 2
    assert b.getvalue() == b'\x00\x00\x00\x00\x00hi'
    assert b.tell() == 7

    # writing exactly at the current end still works and needs no padding
    b2 = io.BytesIO(b'abc')
    b2.seek(3)
    assert b2.write(b'def') == 3
    assert b2.getvalue() == b'abcdef'

    # overwrite-in-the-middle semantics must be unaffected by the fix
    b3 = io.BytesIO(b'abcdef')
    b3.seek(2)
    assert b3.write(b'XY') == 2
    assert b3.getvalue() == b'abXYef'


def test_stringio_write_past_end():
    s = io.StringIO()
    s.seek(5)
    assert s.write('hi') == 2
    assert s.getvalue() == '\x00\x00\x00\x00\x00hi'
    assert s.tell() == 7

    s2 = io.StringIO(initial_value='abc')
    s2.seek(3)
    assert s2.write('def') == 3
    assert s2.getvalue() == 'abcdef'

    s3 = io.StringIO(initial_value='abcdef')
    s3.seek(2)
    assert s3.write('XY') == 2
    assert s3.getvalue() == 'abXYef'


def test_all():
    test_stringio()
    test_bytesio()
    test_io_from_file()
    test_io_read_from_binary_string()
    test_io_write_to_binary_string()
    test_bytesio_write_none()
    test_stringio_write_none()
    test_bytesio_write_past_end()
    test_stringio_write_past_end()


if __name__ == '__main__':
    test_all() 
