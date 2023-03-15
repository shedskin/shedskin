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
        sio.read() == b'aat'

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

def test_all():
    assert True
    # test_io_from_file()
    # test_io_read_from_binary_string()
    # test_io_write_to_binary_string()


if __name__ == '__main__':
    test_all() 
