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


def test_bytesio_truncate_return_value():
    # truncate() must return the new size, not None (regression test)
    b = io.BytesIO(b'abcdefgh')
    b.seek(3)
    assert b.truncate() == 3
    assert b.getvalue() == b'abc'

    b2 = io.BytesIO(b'abcdef')
    assert b2.truncate(2) == 2
    assert b2.getvalue() == b'ab'


def test_stringio_truncate_return_value():
    s = io.StringIO('abcdefgh')
    s.seek(3)
    assert s.truncate() == 3
    assert s.getvalue() == 'abc'

    s2 = io.StringIO('abcdef')
    assert s2.truncate(2) == 2
    assert s2.getvalue() == 'ab'


def test_bytesio_does_not_alias_input():
    # BytesIO must copy its initial_bytes, not alias it -- writing to the
    # BytesIO must never mutate the object (or literal) that was passed in
    # (regression test for a bug where write()/truncate() silently
    # corrupted the caller's original bytes object, including any other
    # occurrence of the same literal elsewhere in the program).
    original = b'hello world'
    buf = io.BytesIO(original)
    buf.write(b'HELLO')
    assert original == b'hello world'
    assert buf.getvalue() == b'HELLO world'

    buf2 = io.BytesIO(b'abc')
    buf2.write(b'def')
    assert b'abc' == b'abc'


def test_stringio_does_not_alias_input():
    original = 'hello world'
    buf = io.StringIO(original)
    buf.write('HELLO')
    assert original == 'hello world'
    assert buf.getvalue() == 'HELLO world'

    buf2 = io.StringIO('abc')
    buf2.write('def')
    assert 'abc' == 'abc'


def test_bytesio_negative_seek():
    # seek(negative, whence=0) must raise, matching CPython exactly, rather
    # than silently storing a negative position (which corrupted later
    # read()/write() calls, since they cast pos to size_t).
    b = io.BytesIO(b"hello world")
    err = False
    try:
        b.seek(-1)
    except ValueError as e:
        err = True
        assert str(e) == "negative seek value -1"
    assert err

    # whence=1/2 that would land before the start must clamp to 0 instead,
    # again matching CPython.
    b2 = io.BytesIO(b"hello world")
    b2.seek(3)
    assert b2.seek(-100, 1) == 0
    assert b2.tell() == 0

    b3 = io.BytesIO(b"hello world")
    assert b3.seek(-100, 2) == 0

    # sanity: ordinary seeks still work as before
    b4 = io.BytesIO(b"hello world")
    assert b4.seek(0, 2) == 11
    assert b4.seek(5) == 5
    assert b4.read() == b" world"


def test_stringio_negative_seek():
    s = io.StringIO("hello world")
    err = False
    try:
        s.seek(-1)
    except ValueError as e:
        err = True
        assert str(e) == "Negative seek position -1"
    assert err


def test_readlines_newline_only():
    # readlines splits on '\n' only, not on the other splitlines boundaries
    s = io.StringIO('a\rb\x0bc\u2028d\ne\r\nf')
    assert s.readlines() == ['a\rb\x0bc\u2028d\n', 'e\r\n', 'f']
    b = io.BytesIO(b'a\rb\x0bc\nd\r\ne')
    assert b.readlines() == [b'a\rb\x0bc\n', b'd\r\n', b'e']


def test_readlines_hint():
    s = io.StringIO('aa\nbb\ncc\n')
    assert s.readlines(3) == ['aa\n', 'bb\n']
    assert s.readlines() == ['cc\n']
    b = io.BytesIO(b'aa\nbb\ncc\n')
    assert b.readlines(1) == [b'aa\n']
    assert b.readlines(0) == [b'bb\n', b'cc\n']


def test_getvalue_is_snapshot():
    s = io.StringIO()
    s.write('abc')
    v = s.getvalue()
    s.seek(0)
    s.write('XYZ')
    assert v == 'abc'
    assert s.getvalue() == 'XYZ'
    b = io.BytesIO()
    b.write(b'abc')
    w = b.getvalue()
    b.seek(0)
    b.write(b'XYZ')
    assert w == b'abc'
    assert b.getvalue() == b'XYZ'


def test_truncate_does_not_grow():
    s = io.StringIO('abc')
    assert s.truncate(10) == 10
    assert s.getvalue() == 'abc'
    b = io.BytesIO(b'abc')
    assert b.truncate(10) == 10
    assert b.getvalue() == b'abc'
    s = io.StringIO('abcdef')
    s.seek(4)
    assert s.truncate(2) == 2
    assert s.tell() == 4
    try:
        b.truncate(-2)
        assert False
    except ValueError as e:
        assert str(e) == 'negative size value -2'


def test_read_past_end_keeps_position():
    s = io.StringIO('abc')
    s.seek(10)
    assert s.read() == ''
    assert s.tell() == 10
    b = io.BytesIO(b'abc')
    b.seek(10)
    assert b.read(2) == b''
    assert b.tell() == 10


def test_stringio_seek_whence():
    s = io.StringIO('abc')
    assert s.seek(0, 2) == 3
    assert s.seek(0, 1) == 3
    err = False
    try:
        s.seek(1, 1)
    except OSError:
        err = True
    assert err
    err = False
    try:
        s.seek(-1, 2)
    except OSError:
        err = True
    assert err
    assert s.tell() == 3
    try:
        s.seek(0, 3)
        assert False
    except ValueError as e:
        assert str(e) == 'Invalid whence (3, should be 0, 1 or 2)'


def test_unicode_positions():
    s = io.StringIO('h\xe9llo\n\u20acuro\n')
    assert s.readline() == 'h\xe9llo\n'
    assert s.tell() == 6
    assert s.read(2) == '\u20acu'
    assert s.seek(0, 2) == 11
    s.write('\U0001f600')
    assert s.getvalue() == 'h\xe9llo\n\u20acuro\n\U0001f600'
    assert len(s.getvalue()) == 12


def test_close():
    s = io.StringIO('abc')
    s.close()
    assert s.closed
    try:
        s.write('x')
        assert False
    except ValueError:
        pass
    b = io.BytesIO(b'abc')
    b.close()
    assert b.closed
    try:
        b.read()
        assert False
    except ValueError:
        pass
    with io.StringIO('x') as f:
        assert f.read() == 'x'
    assert f.closed



def _encoding_or_default(encoding):
    return io.text_encoding(encoding)

def test_text_encoding():
    assert io.text_encoding('latin-1') == 'latin-1'
    assert io.text_encoding('utf-8', 3) == 'utf-8'
    # utf-8 mode is the default since 3.15 (and always on in shedskin)
    assert io.text_encoding(None) == 'utf-8'
    # str-or-None argument
    assert _encoding_or_default('cp1252') == 'cp1252'
    assert _encoding_or_default(None) == 'utf-8'
    assert 'h\xe9'.encode(io.text_encoding(None)) == b'h\xc3\xa9'

def test_module_constants():
    assert io.DEFAULT_BUFFER_SIZE == 8192
    assert io.SEEK_SET == 0
    assert io.SEEK_CUR == 1
    assert io.SEEK_END == 2
    assert io.SEEK_SET == os.SEEK_SET
    assert io.SEEK_CUR == os.SEEK_CUR
    assert io.SEEK_END == os.SEEK_END

    b = io.BytesIO(b'0123456789')
    assert b.seek(-2, io.SEEK_END) == 8
    assert b.read() == b'89'
    assert b.seek(-4, io.SEEK_CUR) == 6
    assert b.seek(1, io.SEEK_SET) == 1
    assert b.read(2) == b'12'

    s = io.StringIO('abcdef')
    assert s.seek(0, io.SEEK_END) == 6
    assert s.seek(0, io.SEEK_SET) == 0
    assert s.read(1) == 'a'
    assert s.seek(0, io.SEEK_CUR) == 1

    # DEFAULT_BUFFER_SIZE is a usable chunk size for a real file
    with open('io_bufsize_testdata.bin', 'wb') as f:
        f.write(b'x' * (io.DEFAULT_BUFFER_SIZE + 1))
    with open('io_bufsize_testdata.bin', 'rb') as f:
        chunk = f.read(io.DEFAULT_BUFFER_SIZE)
        assert len(chunk) == io.DEFAULT_BUFFER_SIZE
        assert f.read() == b'x'
    os.remove('io_bufsize_testdata.bin')


def test_capabilities():
    s = io.StringIO('abc')
    assert s.readable()
    assert s.writable()
    assert s.seekable()
    assert not s.isatty()
    s.flush()
    b = io.BytesIO(b'abc')
    assert b.readable()
    assert b.writable()
    assert b.seekable()
    assert not b.isatty()
    b.flush()

    s.close()
    b.close()
    s.flush()  # StringIO.flush doesn't check for closed in CPython
    for i in range(4):
        err = False
        try:
            if i == 0:
                s.readable()
            elif i == 1:
                s.writable()
            elif i == 2:
                s.seekable()
            else:
                s.isatty()
        except ValueError:
            err = True
        assert err
    for i in range(5):
        err = False
        try:
            if i == 0:
                b.readable()
            elif i == 1:
                b.writable()
            elif i == 2:
                b.seekable()
            elif i == 3:
                b.isatty()
            else:
                b.flush()
        except ValueError:
            err = True
        assert err


def test_unsupported():
    s = io.StringIO('abc')
    b = io.BytesIO(b'abc')
    for i in range(4):
        msg = ''
        try:
            if i == 0:
                s.fileno()
            elif i == 1:
                s.detach()
            elif i == 2:
                b.fileno()
            else:
                b.detach()
        except io.UnsupportedOperation as e:
            msg = str(e)
        assert msg == ['fileno', 'detach'][i % 2]
    err = False
    try:
        b.fileno()
    except OSError:
        err = True
    assert err
    # still usable afterwards
    assert s.read() == 'abc'
    assert b.read() == b'abc'


def test_writelines():
    s = io.StringIO()
    s.writelines(['aa\n', 'bb', '\n'])
    s.writelines(('cc',))
    assert s.getvalue() == 'aa\nbb\ncc'
    s.seek(1)
    s.writelines(['XY'])
    assert s.getvalue() == 'aXYbb\ncc'
    b = io.BytesIO()
    b.writelines([b'aa\n', b'bb'])
    b.writelines(iter([b'cc']))
    assert b.getvalue() == b'aa\nbbcc'


def test_read1():
    b = io.BytesIO(b'hello world')
    assert b.read1(5) == b'hello'
    assert b.tell() == 5
    assert b.read1() == b' world'
    assert b.read1() == b''
    b.seek(6)
    assert b.read1(-1) == b'world'
    b.seek(20)
    assert b.read1(2) == b''
    assert b.tell() == 20
    b.close()
    try:
        b.read1()
        assert False
    except ValueError:
        pass


def test_stringio_newline():
    # None: universal newlines, '\r\n' and '\r' are written as '\n'
    s = io.StringIO('a\rb\r\nc\nd', newline=None)
    assert s.getvalue() == 'a\nb\nc\nd'
    assert s.readlines() == ['a\n', 'b\n', 'c\n', 'd']
    s = io.StringIO(newline=None)
    assert s.write('x\r') == 2
    assert s.write('\ny\r\n') == 4
    assert s.getvalue() == 'x\n\ny\n'
    assert s.tell() == 5
    s = io.StringIO('abcdef', None)
    s.seek(2)
    s.write('\r\n')
    assert s.getvalue() == 'ab\ndef'
    assert s.tell() == 3
    # '': no translation, lines end at '\n', '\r' or '\r\n'
    s = io.StringIO('a\rb\r\nc\nd', newline='')
    assert s.getvalue() == 'a\rb\r\nc\nd'
    assert s.readlines() == ['a\r', 'b\r\n', 'c\n', 'd']
    assert list(io.StringIO('x\r\r\ny\rz\n', newline='')) == ['x\r', '\r\n', 'y\r', 'z\n']
    s = io.StringIO('a\r\nb', newline='')
    assert s.readline(2) == 'a\r'
    assert s.readline() == '\n'
    # '\n' (default): no translation, lines end at '\n' only
    s = io.StringIO('a\rb\r\nc\nd', newline='\n')
    assert s.readlines() == ['a\rb\r\n', 'c\n', 'd']
    # '\r': '\n' is written as '\r', lines end at '\r'
    s = io.StringIO('a\rb\r\nc\nd', newline='\r')
    assert s.getvalue() == 'a\rb\r\rc\rd'
    assert s.readlines() == ['a\r', 'b\r', '\r', 'c\r', 'd']
    # '\r\n': '\n' is written as '\r\n', lines end at '\r\n'
    s = io.StringIO(newline='\r\n')
    assert s.write('a\r\nb\n') == 5
    assert s.getvalue() == 'a\r\r\nb\r\n'
    assert s.tell() == 7
    s.seek(0)
    assert s.readlines() == ['a\r\r\n', 'b\r\n']
    s = io.StringIO('abc\n', newline='\r\n')
    assert s.tell() == 0
    assert s.read() == 'abc\r\n'
    # invalid values
    for bad in ['x', '\n\r', 'ab']:
        try:
            io.StringIO(newline=bad)
            assert False
        except ValueError as e:
            assert str(e) == 'illegal newline value: ' + repr(bad)


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
    test_bytesio_truncate_return_value()
    test_stringio_truncate_return_value()
    test_bytesio_does_not_alias_input()
    test_stringio_does_not_alias_input()
    test_bytesio_negative_seek()
    test_stringio_negative_seek()
    test_readlines_newline_only()
    test_readlines_hint()
    test_getvalue_is_snapshot()
    test_truncate_does_not_grow()
    test_read_past_end_keeps_position()
    test_stringio_seek_whence()
    test_unicode_positions()
    test_close()
    test_text_encoding()
    test_module_constants()
    test_capabilities()
    test_unsupported()
    test_writelines()
    test_read1()
    test_stringio_newline()


if __name__ == '__main__':
    test_all() 
