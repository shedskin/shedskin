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


def test_all():
    test_stringio()
    test_bytesio()
    test_io_from_file()
    test_io_read_from_binary_string()
    test_io_write_to_binary_string()


if __name__ == '__main__':
    test_all() 
