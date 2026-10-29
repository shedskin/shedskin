import gzip
import io
import os


# produced by CPython (zlib), so not by our own (miniz) compressor
ZLIB_BLOB = b'\x1f\x8b\x08\x0090\x00\x00\x02\xff\xcbH\xcd\xc9\xc9W(\xcf/\xcaI\xe1\xca\x18e\x8f\xb2\xa9\xc4\x06\x00\x17\x80\xe1PX\x02\x00\x00'
ZLIB_FNAME_BLOB = b"\x1f\x8b\x08\x081\xd4\x00\x00\x00\xffhello.txt\x00\xcb8\xbc2''_\xa1\xfc\xf0\xb6\xa2\x9c\x14\xae\x0c<<\x06F&f\x16V6v\x0eN.n\x1e^>~\x01A!a\x11Q1q\tI)i\x19Y9y\x05E%e\x15U5u\rM-m\x1d]=}\x03C#c\x13S3s\x0bK+k\x1b[;{\x07G'g\x17W7w\x0fO/o\x1f_?\xff\x80\xc0\xa0\xe0\x90\xd0\xb0\xf0\x88\xc8\xa8\xe8\x98\xd8\xb8\xf8\x84\xc4\xa4\xe4\x94\xd4\xb4\xf4\x8c\xcc\xac\xec\x9c\xdc\xbc\xfc\x82\xc2\xa2\xe2\x92\xd2\xb2\xf2\x8a\xca\xaa\xea\x9a\xda\xba\xfa\x86\xc6\xa6\xe6\x96\xd6\xb6\xf6\x8e\xce\xae\xee\x9e\xde\xbe\xfe\t\x13'M\x9e2u\xda\xf4\x193g\xcd\x9e3w\xde\xfc\x05\x0b\x17-^\xb2t\xd9\xf2\x15+W\xad^\xb3v\xdd\xfa\r\x1b7m\xde\xb2u\xdb\xf6\x1d;w\xed\xde\xb3w\xdf\xfe\x03\x07\x0f\x1d>r\xf4\xd8\xf1\x13'O\x9d>s\xf6\xdc\xf9\x0b\x17/]\xber\xf5\xda\xf5\x1b7o\xdd\xbes\xf7\xde\xfd\x07\x0f\x1f=~\xf2\xf4\xd9\xf3\x17/_\xbd~\xf3\xf6\xdd\xfb\x0f\x1f?}\xfe\xf2\xf5\xdb\xf7\x1f?\x7f\xfd\xfe\xf3\xf7\xdf\x7f\x00\x10\xf2\xc4\xcf*\x01\x00\x00"


def pseudo_random(n, seed=12345):
    data = bytearray()
    x = seed
    for i in range(n):
        x = (x * 1103515245 + 12345) & 0x7fffffff
        data.append((x >> 16) & 0xff)
    return bytes(data)


def tmpname(name):
    return 'test_mod_gzip_' + name


def test_roundtrip():
    samples = [b'', b'a', b'hello world', bytes(range(256)) * 100,
               b'x' * 1000000, pseudo_random(100000)]
    for data in samples:
        assert gzip.decompress(gzip.compress(data)) == data
        for level in range(-1, 10):
            assert gzip.decompress(gzip.compress(data, level)) == data
    # actually compresses
    assert len(gzip.compress(b'x' * 1000000)) < 5000
    assert len(gzip.compress(b'x' * 1000000, 1)) < 10000
    assert len(gzip.compress(b'x' * 10000, 0)) > 10000
    # bytearray input
    assert gzip.decompress(gzip.compress(bytearray(b'abc'))) == b'abc'


def test_compress_header():
    d = gzip.compress(b'abc', mtime=0x01020304)
    assert d[:4] == b'\x1f\x8b\x08\x00'
    assert d[4:8] == b'\x04\x03\x02\x01'
    assert d[8] == 2  # level 9
    assert d[9] == 255
    assert gzip.compress(b'abc', 1, mtime=0)[8] == 4
    assert gzip.compress(b'abc', 0, mtime=0)[8] == 4
    assert gzip.compress(b'abc', 6, mtime=0)[8] == 0
    assert gzip.compress(b'abc', -1, mtime=0)[8] == 0
    # trailer: crc32 and size
    assert d[-4:] == b'\x03\x00\x00\x00'
    assert d[-8:-4] == b'\xc2\x41\x24\x35'
    # mtime defaults to the current time
    d = gzip.compress(b'abc')
    assert d[4:8] != b'\x00\x00\x00\x00'


def test_bad_level():
    for level in [-2, 10, 100]:
        try:
            gzip.compress(b'abc', level)
            assert False
        except Exception:  # (zlib.error in CPython)
            pass


def test_decompress_zlib_data():
    assert gzip.decompress(ZLIB_BLOB) == b'hello world\n' * 50
    expected = 'héllo wörld\n'.encode() * 3 + bytes(range(256))
    assert gzip.decompress(ZLIB_FNAME_BLOB) == expected
    g = gzip.GzipFile(fileobj=io.BytesIO(ZLIB_FNAME_BLOB))
    assert g.read() == expected
    assert g.mtime == 54321


def test_multi_member():
    a = gzip.compress(b'first\n', mtime=1)
    b = gzip.compress(b'second\n', mtime=2)
    assert gzip.decompress(a + b) == b'first\nsecond\n'
    # zero padding between and after members
    data = a + b'\x00\x00\x00' + b + b'\x00'
    assert gzip.decompress(data) == b'first\nsecond\n'
    g = gzip.GzipFile(fileobj=io.BytesIO(data))
    assert g.readlines() == [b'first\n', b'second\n']
    assert g.mtime == 2
    # many members, read in small pieces
    data = b''
    expected = b''
    for i in range(50):
        chunk = pseudo_random(i * 37, i)
        data += gzip.compress(chunk)
        expected += chunk
    assert gzip.decompress(data) == expected
    g = gzip.GzipFile(fileobj=io.BytesIO(data))
    result = b''
    while True:
        piece = g.read(13)
        if not piece:
            break
        result += piece
    assert result == expected


def test_header_fields():
    payload = gzip.compress(b'some data', mtime=0)[10:]
    flags = gzip.FEXTRA | gzip.FNAME | gzip.FCOMMENT | gzip.FHCRC
    header = b'\x1f\x8b\x08' + bytes([flags]) + b'\x07\x00\x00\x00\x00\xff'
    header += b'\x03\x00abc' + b'name.txt\x00' + b'a comment\x00' + b'\x12\x34'
    data = header + payload
    assert gzip.decompress(data) == b'some data'
    g = gzip.GzipFile(fileobj=io.BytesIO(data))
    assert g.read() == b'some data'
    assert g.mtime == 7


def expect_error(data, kind, msg):
    for i in range(2):
        try:
            if i == 0:
                gzip.decompress(data)
            else:
                gzip.GzipFile(fileobj=io.BytesIO(data)).read()
            assert False
        except gzip.BadGzipFile as e:
            assert kind == 'bad'
            if msg:
                assert str(e) == msg
        except EOFError as e:
            assert kind == 'eof'
            assert str(e) == 'Compressed file ended before the end-of-stream marker was reached'


def test_errors():
    d = gzip.compress(b'hello\nworld\n' * 3, mtime=0)
    expect_error(b'xy', 'bad', "Not a gzipped file (b'xy')")
    expect_error(b'x', 'bad', "Not a gzipped file (b'x')")
    expect_error(d[:2] + b'\x07' + d[3:], 'bad', 'Unknown compression method')
    expect_error(d[:-5] + b'\x01' + d[-4:], 'bad', '')
    expect_error(d[:-1] + b'\x01', 'bad', 'Incorrect length of data produced')
    expect_error(d + b'\x00\x00garbage', 'bad', "Not a gzipped file (b'ga')")
    for n in [5, 10, 15, len(d) - 8, len(d) - 3]:
        expect_error(d[:n], 'eof', '')
    try:
        gzip.decompress(d[:-5] + b'\x01' + d[-4:])
    except gzip.BadGzipFile as e:
        assert str(e) == 'CRC check failed'
    try:
        gzip.GzipFile(fileobj=io.BytesIO(d[:-5] + b'\x01' + d[-4:])).read()
    except gzip.BadGzipFile as e:
        assert str(e) == 'CRC check failed 0x1297875 != 0xb6297875'
    # corrupt deflate data
    try:
        gzip.decompress(d[:12] + b'\xff\xff\xff' + d[15:])
        assert False
    except Exception:  # (zlib.error in CPython)
        pass
    # BadGzipFile is an OSError
    try:
        gzip.decompress(b'nope')
        assert False
    except OSError as e:
        assert str(e) == "Not a gzipped file (b'no')"
    # empty input
    assert gzip.decompress(b'') == b''
    assert gzip.GzipFile(fileobj=io.BytesIO(b'')).read() == b''


def test_gzipfile_bytesio():
    buf = io.BytesIO()
    g = gzip.GzipFile(fileobj=buf, mode='wb', mtime=0x0a0b0c0d)
    assert g.mode == gzip.WRITE == 'wb'
    assert g.name == ''
    assert g.writable() and not g.readable() and g.seekable()
    assert g.write(b'hello ') == 6
    assert g.write(bytearray(b'world\n')) == 6
    assert g.tell() == 12
    g.writelines([b'a\n', b'b\n'])
    assert not g.closed
    g.close()
    assert g.closed
    g.close()  # no-op
    assert not buf.closed  # not ours
    data = buf.getvalue()
    assert data[:4] == b'\x1f\x8b\x08\x00'  # no FNAME
    assert data[4:8] == b'\x0d\x0c\x0b\x0a'
    assert gzip.decompress(data) == b'hello world\na\nb\n'

    g = gzip.GzipFile(fileobj=io.BytesIO(data))
    assert g.mode == gzip.READ == 'rb'
    assert g.readable() and not g.writable() and g.seekable()
    assert g.readline() == b'hello world\n'
    assert g.mtime == 0x0a0b0c0d
    assert g.tell() == 12
    assert [line for line in g] == [b'a\n', b'b\n']
    assert g.read() == b''
    assert g.readline() == b''


def test_reading():
    data = b''.join([b'line %d\n' % i for i in range(1000)])
    g = gzip.GzipFile(fileobj=io.BytesIO(gzip.compress(data)))
    assert g.read(5) == b'line '
    assert g.peek(2)[:2] == b'0\n'
    assert g.read1(2) == b'0\n'
    assert g.readline(3) == b'lin'
    assert g.readline() == b'e 1\n'
    assert g.readline(0) == b''
    b = bytearray(10)
    assert g.readinto(b) == 10
    assert b == bytearray(b'line 2\nlin')
    assert g.tell() == 24
    assert g.readlines(20) == [b'e 3\n', b'line 4\n', b'line 5\n', b'line 6\n']
    assert g.read(0) == b''
    g.rewind()
    assert g.tell() == 0
    assert g.read() == data
    assert g.read(10) == b''
    assert g.read1(10) == b''
    assert g.peek(1) == b''
    g.close()

    g = gzip.GzipFile(fileobj=io.BytesIO(gzip.compress(data)))
    assert len(g.read1()) > 0
    g.rewind()
    assert len(g.readlines()) == 1000


def test_seek_read():
    data = pseudo_random(300000)
    g = gzip.GzipFile(fileobj=io.BytesIO(gzip.compress(data)))
    assert g.seek(100000) == 100000
    assert g.read(10) == data[100000:100010]
    assert g.seek(5) == 5  # backwards
    assert g.read(10) == data[5:15]
    assert g.seek(1000, 1) == 1015
    assert g.read(1) == data[1015:1016]
    assert g.seek(-10, 2) == len(data) - 10
    assert g.read() == data[-10:]
    assert g.seek(10, 2) == len(data)  # clamped
    assert g.seek(len(data) + 10) == len(data)
    assert g.seek(-5) == 0
    assert g.seek(-100, 1) == 0
    assert g.read(3) == data[:3]
    try:
        g.seek(0, 3)
        assert False
    except ValueError as e:
        assert str(e) == 'Invalid value for whence: 3'


def test_write_mode():
    buf = io.BytesIO()
    g = gzip.GzipFile(fileobj=buf, mode='w')
    assert g.mode == 'wb'
    g.write(b'ab')
    g.seek(5)  # pads with zeros
    assert g.tell() == 5
    g.seek(2, 1)
    assert g.tell() == 7
    g.write(b'c')
    try:
        g.seek(1)
        assert False
    except OSError as e:
        assert str(e) == 'Negative seek in write mode'
    try:
        g.seek(0, 2)
        assert False
    except ValueError as e:
        assert str(e) == 'Seek from end not supported'
    for i in range(4):
        try:
            if i == 0:
                g.read()
            elif i == 1:
                g.read1()
            elif i == 2:
                g.peek(1)
            else:
                g.rewind()
            assert False
        except OSError as e:
            if i == 0:
                assert e.errno == 9
                assert str(e) == '[Errno 9] read() on write-only GzipFile object'
            elif i == 1:
                assert str(e) == '[Errno 9] read1() on write-only GzipFile object'
            elif i == 2:
                assert str(e) == '[Errno 9] peek() on write-only GzipFile object'
            else:
                assert str(e) == "Can't rewind in write mode"
    try:
        g.readline()
        assert False
    except OSError:  # io.UnsupportedOperation
        pass
    g.flush()
    # flushed data is complete up to here
    partial = buf.getvalue()
    g.write(b'more')
    g.close()
    assert gzip.decompress(buf.getvalue()) == b'ab\x00\x00\x00\x00\x00cmore'
    assert len(partial) > 10

    g = gzip.GzipFile(fileobj=io.BytesIO(gzip.compress(b'x')))
    try:
        g.write(b'y')
        assert False
    except OSError as e:
        assert e.errno == 9
        assert str(e) == '[Errno 9] write() on read-only GzipFile object'
    try:
        g.truncate()
        assert False
    except OSError:  # io.UnsupportedOperation
        pass
    try:
        g.fileno()
        assert False
    except OSError:  # io.UnsupportedOperation (BytesIO)
        pass
    assert not g.isatty()


def test_closed():
    g = gzip.GzipFile(fileobj=io.BytesIO(gzip.compress(b'abc')))
    g.close()
    assert g.closed
    for i in range(6):
        try:
            if i == 0:
                g.read()
            elif i == 1:
                g.readline()
            elif i == 2:
                g.seek(0)
            elif i == 3:
                g.tell()
            elif i == 4:
                g.peek(1)
            else:
                g.flush()
            assert False
        except ValueError as e:
            assert str(e) == 'I/O operation on closed file'
    g = gzip.GzipFile(fileobj=io.BytesIO(), mode='wb')
    g.close()
    try:
        g.write(b'abc')
        assert False
    except ValueError as e:
        assert str(e) == 'I/O operation on closed file'


def test_invalid_modes():
    for mode in ['rt', 'rU', 'q', 'wt']:
        try:
            gzip.GzipFile(fileobj=io.BytesIO(), mode=mode)
            assert False
        except ValueError as e:
            if mode == 'q':
                assert str(e) == "Invalid mode: 'qb'"
            else:
                assert str(e) == "Invalid mode: %r" % mode
    # by filename, the mode is checked (with a 'b' added) as by open()
    for mode in ['wa', 'rr']:
        try:
            gzip.open('shedskin_never_created.gz', mode)
            assert False
        except ValueError as e:
            if mode == 'wa':
                assert str(e) == 'must have exactly one of create/read/write/append mode'
            else:
                assert str(e) == "invalid mode: 'rrb'"
    assert not os.path.exists('shedskin_never_created.gz')
    # an empty mode is falsy: no 'b' is added, and the mode itself is rejected
    # (by filename, the file is first opened as 'rb'); 'tt' becomes ''
    with gzip.open('shedskin_empty_mode.gz', 'wb') as g:
        g.write(b'abc')
    msgs = []
    try:
        gzip.open('shedskin_empty_mode.gz', '')
    except ValueError as e:
        msgs.append(str(e))
    try:
        gzip.open('shedskin_empty_mode.gz', 'tt')  # (a constant text mode)
    except ValueError as e:
        msgs.append(str(e))
    try:
        gzip.open(io.BytesIO(), '')
    except ValueError as e:
        msgs.append(str(e))
    try:
        gzip.GzipFile('shedskin_empty_mode.gz', '')
    except ValueError as e:
        msgs.append(str(e))
    assert msgs == ["Invalid mode: ''"] * 4
    os.remove('shedskin_empty_mode.gz')
    try:
        gzip.open('shedskin_never_created.gz', '')
        assert False
    except FileNotFoundError:
        pass
    try:
        gzip.open(io.BytesIO(), 'rtb')
        assert False
    except ValueError as e:
        assert str(e) == "Invalid mode: 'rtb'"
    try:
        gzip.open(io.BytesIO(), 'rb', encoding='utf-8')
        assert False
    except ValueError as e:
        assert str(e) == "Argument 'encoding' not supported in binary mode"
    try:
        gzip.open(io.BytesIO(), 'rb', errors='strict')
        assert False
    except ValueError as e:
        assert str(e) == "Argument 'errors' not supported in binary mode"
    try:
        gzip.open(io.BytesIO(), 'rb', newline='')
        assert False
    except ValueError as e:
        assert str(e) == "Argument 'newline' not supported in binary mode"
    try:
        gzip.open(io.BytesIO(), 'wt', newline='x')
        assert False
    except ValueError as e:
        assert str(e) == "illegal newline value: x"
    try:
        gzip.open(io.BytesIO(), 'wt', encoding='bla')
        assert False
    except LookupError as e:
        assert str(e) == "unknown encoding: bla"


def test_no_file():
    try:
        gzip.GzipFile()
        assert False
    except TypeError:
        pass


def test_files():
    name = tmpname('a.txt.gz')
    data = pseudo_random(50000) + b'\nsome\nlines\n'
    with gzip.open(name, 'wb') as f:
        assert f.name == name
        f.write(data[:1000])
        f.write(data[1000:])
    assert f.closed
    # (close explicitly: without refcounting, an open handle would make
    # os.remove() fail under windows)
    with open(name, 'rb') as f:
        raw = f.read()
    assert raw[3] == gzip.FNAME
    assert raw[10:30] == b'test_mod_gzip_a.txt\x00'

    with gzip.open(name) as f:
        assert f.name == name
        assert f.read() == data
    with gzip.open(name, 'r') as f:
        lines = f.readlines()
        assert lines[-2:] == [b'some\n', b'lines\n']
        assert b''.join(lines) == data

    g = gzip.GzipFile(name)
    assert g.read(1000) == data[:1000]
    assert g.seek(-6, 2) == len(data) - 6
    assert g.read() == b'lines\n'
    g.close()

    # append: a second member
    with gzip.open(name, 'ab') as f:
        f.write(b'appended\n')
    with gzip.open(name, 'rb') as f:
        assert f.read() == data + b'appended\n'

    # exclusive creation
    try:
        gzip.open(name, 'xb')
        assert False
    except FileExistsError:
        pass
    os.remove(name)
    try:
        gzip.open(name)
        assert False
    except FileNotFoundError:
        pass

    # bytes file name
    with gzip.open(name.encode(), 'wb', 1) as f:
        f.write(b'level one')
    with gzip.open(name) as g:
        assert g.read() == b'level one'

    # wrapping an open file: not closed by us
    f = open(name, 'wb')
    g = gzip.GzipFile(fileobj=f, mode='wb', mtime=0)
    assert g.name == name
    g.write(b'wrapped')
    g.close()
    assert not f.closed
    f.write(b'\x00\x00')  # padding
    f.close()
    f = open(name, 'rb')
    g = gzip.GzipFile(fileobj=f)
    assert g.read() == b'wrapped'
    g.close()
    assert not f.closed
    f.close()

    # the wrapped file closed underneath us
    f = open(name, 'rb')
    g = gzip.GzipFile(fileobj=f)
    f.close()
    try:
        g.read()
        assert False
    except ValueError as e:
        assert str(e) == 'read of closed file'
    g.close()
    f = open(name, 'wb')
    g = gzip.GzipFile(fileobj=f, mode='wb')
    g.write(b'abc' * 10)
    f.close()
    try:
        g.close()
        assert False
    except ValueError as e:
        assert str(e) == 'write to closed file'
    assert g.closed
    os.remove(name)


def test_large():
    buf = io.BytesIO()
    g = gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=5)
    lines = []
    for i in range(20000):
        line = b'%d %s\n' % (i, pseudo_random(i % 100, i).hex().encode())
        lines.append(line)
        g.write(line)
    g.close()
    g = gzip.GzipFile(fileobj=io.BytesIO(buf.getvalue()))
    count = 0
    for line in g:
        assert line == lines[count]
        count += 1
    assert count == 20000
    assert g.tell() == sum([len(line) for line in lines])


def test_readlines_hint():
    # stop once the total length read exceeds the hint (as IOBase)
    data = gzip.compress('ab\ncd\n\xe9f\n'.encode('utf-8'))
    for hint, n in [(-1, 3), (0, 3), (1, 1), (2, 1), (3, 2), (5, 2), (6, 3)]:
        g = gzip.GzipFile(fileobj=io.BytesIO(data))
        assert len(g.readlines(hint)) == n
    g = gzip.GzipFile(fileobj=io.BytesIO(data))
    assert g.readlines(3) == [b'ab\n', b'cd\n']
    assert g.readlines() == [b'\xc3\xa9f\n']
    # text mode: in characters
    for hint, n in [(-1, 3), (0, 3), (2, 1), (3, 2), (5, 2), (6, 3)]:
        t = gzip.open(io.BytesIO(data), 'rt', encoding='utf-8')
        assert len(t.readlines(hint)) == n
    t = gzip.open(io.BytesIO(data), 'rt', encoding='utf-8')
    assert t.readlines(3) == ['ab\n', 'cd\n']
    assert t.readlines() == ['\xe9f\n']


def test_read_negative():
    g = gzip.GzipFile(fileobj=io.BytesIO(gzip.compress(b'abcdef')))
    assert g.read(-1) == b'abcdef'
    g = gzip.GzipFile(fileobj=io.BytesIO(gzip.compress(b'abcdef')))
    try:
        g.read(-7)
        assert False
    except ValueError as e:
        assert str(e) == 'read length must be non-negative or -1'
    assert g.read(2) == b'ab'


def test_text_mode():
    buf = io.BytesIO()
    with gzip.open(buf, 'wt') as f:
        assert f.write('héllo\n') == 6
        f.writelines(['wörld\n', '€uro\n'])
        # (newline=None: '\n' is written as os.linesep)
        assert f.tell() == 18 + 3 * len(os.linesep)
    data = gzip.decompress(buf.getvalue())
    assert data == 'héllo\nwörld\n€uro\n'.replace('\n', os.linesep).encode()

    f = gzip.open(io.BytesIO(buf.getvalue()), 'rt')
    assert f.encoding == 'utf-8'
    assert f.readable() and not f.writable()
    assert f.read(2) == 'hé'
    assert f.readline(2) == 'll'
    assert f.readline() == 'o\n'
    assert f.readline() == 'wörld\n'
    assert f.read() == '€uro\n'
    assert f.read() == ''
    f.close()
    assert f.closed

    f = gzip.open(io.BytesIO(buf.getvalue()), 'rt')
    assert [line for line in f] == ['héllo\n', 'wörld\n', '€uro\n']
    f = gzip.open(io.BytesIO(buf.getvalue()), 'rt')
    assert f.readlines() == ['héllo\n', 'wörld\n', '€uro\n']

    # tell/seek cookies
    f = gzip.open(io.BytesIO(buf.getvalue()), 'rt')
    f.readline()
    pos = f.tell()
    line = f.readline()
    assert f.seek(pos) == pos
    assert f.readline() == line
    assert f.seek(0) == 0
    assert f.readline() == 'héllo\n'
    try:
        f.seek(3, 1)
        assert False
    except OSError as e:  # io.UnsupportedOperation
        assert str(e) == "can't do nonzero cur-relative seeks"

    # errors
    f = gzip.open(io.BytesIO(buf.getvalue()), 'rt')
    try:
        f.write('x')
        assert False
    except OSError as e:  # io.UnsupportedOperation
        assert str(e) == 'not writable'
    f = gzip.open(io.BytesIO(), 'wt')
    try:
        f.read()
        assert False
    except OSError as e:  # io.UnsupportedOperation
        assert str(e) == 'not readable'


def test_text_encodings():
    buf = io.BytesIO()
    with gzip.open(buf, 'wt', encoding='latin-1') as f:
        f.write('héllo')
    assert gzip.decompress(buf.getvalue()) == b'h\xe9llo'
    with gzip.open(io.BytesIO(buf.getvalue()), 'rt', encoding='latin-1') as f:
        assert f.read() == 'héllo'
    with gzip.open(io.BytesIO(buf.getvalue()), 'rt', errors='replace') as f:
        assert f.read() == 'h�llo'
    with gzip.open(io.BytesIO(buf.getvalue()), 'rt') as f:
        try:
            f.read()
            assert False
        except UnicodeDecodeError:
            pass

    buf = io.BytesIO()
    with gzip.open(buf, 'wt', encoding='utf-8-sig') as f:
        f.write('hé')
    assert gzip.decompress(buf.getvalue()) == b'\xef\xbb\xbfh\xc3\xa9'
    with gzip.open(io.BytesIO(buf.getvalue()), 'rt', encoding='utf-8-sig') as f:
        assert f.read() == 'hé'
    with gzip.open(io.BytesIO(buf.getvalue()), 'rt') as f:
        assert f.read() == '﻿hé'


def test_text_newlines():
    data = gzip.compress(b'a\nb\r\nc\rd\r')
    expected_lines = [
        ['a\n', 'b\n', 'c\n', 'd\n'],  # None
        ['a\n', 'b\r\n', 'c\r', 'd\r'],  # ''
        ['a\n', 'b\r\n', 'c\rd\r'],  # '\n'
        ['a\nb\r', '\nc\r', 'd\r'],  # '\r'
        ['a\nb\r\n', 'c\rd\r'],  # '\r\n'
    ]
    expected_written = [
        b'a\nb\r\nc\rd',
        b'a\nb\r\nc\rd',
        b'a\nb\r\nc\rd',
        b'a\rb\r\rc\rd',
        b'a\r\nb\r\r\nc\rd',
    ]
    newlines = [None, '', '\n', '\r', '\r\n']
    for i in range(len(newlines)):
        nl = newlines[i]
        f = gzip.open(io.BytesIO(data), 'rt', newline=nl)
        assert f.readlines() == expected_lines[i]
        buf = io.BytesIO()
        f = gzip.open(buf, 'wt', newline=nl)
        f.write('a\nb\r\nc\rd')
        f.close()
        if os.name != 'nt' or nl is not None:
            assert gzip.decompress(buf.getvalue()) == expected_written[i]
    f = gzip.open(io.BytesIO(data), 'rt')
    assert f.read() == 'a\nb\nc\nd\n'


def test_text_files():
    name = tmpname('b.txt.gz')
    with gzip.open(name, 'wt') as f:
        for i in range(1000):
            print('line', i, file=f)
    with gzip.open(name, 'at') as f:
        f.write('the end\n')
    with gzip.open(name, 'rt') as f:
        lines = f.readlines()
    assert len(lines) == 1001
    assert lines[0] == 'line 0\n'
    assert lines[999] == 'line 999\n'
    assert lines[1000] == 'the end\n'
    count = 0
    f = gzip.open(name, mode='rt')
    for line in f:
        count += 1
    f.close()
    assert count == 1001
    os.remove(name)


def test_text_read_chars_invalid():
    # read(n)/readline(n) count decoded characters, also for invalid bytes
    blob = gzip.compress(b'\x80\x80\x80abc\n\xe2\x82a')
    with gzip.open(io.BytesIO(blob), 'rt', errors='replace') as f:
        assert f.read(2) == '\ufffd\ufffd'
        assert f.readline(3) == '\ufffdab'
        assert f.readline() == 'c\n'
        assert f.read(2) == '\ufffda'
    with gzip.open(io.BytesIO(blob), 'rt', errors='ignore') as f:
        assert f.read(2) == 'ab'
    with gzip.open(io.BytesIO(blob), 'rt', encoding='ascii', errors='ignore') as f:
        assert f.read(4) == 'abc\n'


def test_enter_exit_results():
    # __enter__ returns the file itself and __exit__ returns None
    name = tmpname('c.gz')
    g = gzip.open(name, 'wb')
    h = g.__enter__()
    assert h is g
    h.write(b'hoi')
    assert g.__exit__() is None
    t = gzip.open(name, 'rt')
    u = t.__enter__()
    assert u is t
    assert u.read() == 'hoi'
    assert t.__exit__() is None
    os.remove(name)


def test_all():
    test_roundtrip()
    test_compress_header()
    test_bad_level()
    test_enter_exit_results()
    test_decompress_zlib_data()
    test_multi_member()
    test_header_fields()
    test_errors()
    test_gzipfile_bytesio()
    test_reading()
    test_readlines_hint()
    test_read_negative()
    test_seek_read()
    test_write_mode()
    test_closed()
    test_invalid_modes()
    test_no_file()
    test_files()
    test_large()
    test_text_mode()
    test_text_encodings()
    test_text_newlines()
    test_text_files()
    test_text_read_chars_invalid()


if __name__ == '__main__':
    test_all()
