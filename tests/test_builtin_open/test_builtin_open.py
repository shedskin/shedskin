import os
import sys
import io


if os.path.exists("testdata"):
    testdata = "testdata"
elif os.path.exists("../testdata"):
    testdata = "../testdata"
else:
    testdata = "../../testdata"

datafile = os.path.join(testdata, 'hoppa')
outputfile = os.path.join(testdata, 'hoppa_write')


def test_open_for():
    f = open(datafile)
    assert [l for l in f] == ['hop\n', 'hop\n', 'hoppa!\n']
    f.close()


def test_open_read():
    f = open(datafile)
    assert f.read() == 'hop\nhop\nhoppa!\n'
    f.close()


def test_open_readlines():
    f = open(datafile)
    assert f.readlines() == ['hop\n', 'hop\n', 'hoppa!\n']
    f.close()


def test_open_readlines_hint():
    # stop once the total length read exceeds the hint (text: in characters)
    # write in binary mode, so the file has no '\r\n' newlines under windows
    with open('rlh.txt', 'wb') as g:
        g.write(b'\xc3\xa9\xc3\xa9\nb\nc\n')
    for hint, n in [(-1, 3), (0, 3), (1, 1), (2, 1), (3, 2), (4, 2), (5, 3)]:
        with open('rlh.txt', encoding='utf-8') as f:
            assert len(f.readlines(hint)) == n
    with open('rlh.txt', encoding='utf-8') as f:
        assert f.readlines(1) == ['\xe9\xe9\n']
        assert f.readlines() == ['b\n', 'c\n']
    # binary: in bytes
    for hint, n in [(-1, 3), (0, 3), (4, 1), (5, 2), (6, 2), (7, 3)]:
        with open('rlh.txt', 'rb') as g:
            assert len(g.readlines(hint)) == n
    with open('rlh.txt', 'rb') as g:
        assert g.readlines(1) == [b'\xc3\xa9\xc3\xa9\n']
        assert g.readlines() == [b'b\n', b'c\n']
    os.remove('rlh.txt')


def test_with_open_read():
    with open(datafile) as f:
        assert f.read() == 'hop\nhop\nhoppa!\n'


def test_open_read2():
     with open(datafile) as f:
         words = f.read().split()
         d = {}
         res = []
         for i, word in enumerate(words):
             s = "".join(sorted(list(word.lower())))
             d.setdefault(s, []).append(i)
         for val in d.values():
             if len(val) > 1:
                 res.append([words[i] for i in val])
     assert res == [['hop', 'hop']]


def test_open_write():
    f = open(outputfile, 'w')
    f.write('hop\nhop\nhoppa!\n')
    f.close()
    with open(outputfile) as g:
        assert g.read() == 'hop\nhop\nhoppa!\n'


def test_open_enter_exit():
    f = open(outputfile, 'w+')
    f.__enter__()
    f.write('hop\nhop\nhoppa!\n')
    f.seek(0)
    assert f.read() == 'hop\nhop\nhoppa!\n'
    f.__exit__()


def test_with_open_write():
     with open(outputfile, 'w') as f: # FIXME doesn't work
         f.write('hop\nhop\nhoppa!\n')
     with open(outputfile) as f:
         assert f.read() == 'hop\nhop\nhoppa!\n'


def test_open_truncate():
    f = open(outputfile, 'w')
    f.write('hop\nhop\nhoppa!\n')
    result = f.truncate(3)
    assert result == 3
    f.close()
    with open(outputfile) as g:
        assert g.read() == 'hop'

    # truncate() without argument truncates at the current position
    f = open(outputfile, 'w')
    f.write('hello')
    f.seek(2)
    assert f.truncate() == 2
    f.close()
    with open(outputfile) as g:
        assert g.read() == 'he'

    fb = open(outputfile, 'wb')
    fb.write(b'hello')
    fb.seek(3)
    assert fb.truncate() == 3
    fb.close()
    with open(outputfile, 'rb') as gb:
        assert gb.read() == b'hel'


def test_lineendings():
     cr_txt = os.path.join(testdata, 'cr.txt')
     lf_txt = os.path.join(testdata, 'lf.txt')
     crlf_txt = os.path.join(testdata, 'crlf.txt')

     # regression test: file.read() bypassed universal-newline translation
     # entirely (only readline()/readlines()/iteration did the \r, \r\n ->
     # \n translation), so plain f.read() returned raw, untranslated bytes
     # in text mode. Lone '\r' and '\r\n' line endings must both normalize
     # to '\n' on read, matching CPython's universal newline handling.
     with open(cr_txt, "w") as f1:
         f1.write("hello world\r")
         f1.write("bye\r")

     with open(cr_txt, "r") as f2:
         assert list(f2) == ["hello world\n", "bye\n"]

     with open(cr_txt, "r") as f2b:
         assert f2b.read() == "hello world\nbye\n"

     with open(lf_txt, "w") as f3:
         f3.write("hello world\n")
         f3.write("bye\n")

     with open(lf_txt, "r") as f4:
         assert list(f4) == ["hello world\n", "bye\n"]

     with open(lf_txt, "r") as f4b:
         assert f4b.read() == "hello world\nbye\n"

     # (newline='': on windows, newline=None would write '\r\r\n')
     with open(crlf_txt, "w", newline='') as f5:
         f5.write("hello world\r\n")
         f5.write("bye\r\n")

     with open(crlf_txt, "rb") as f6r:
         assert f6r.read() == b"hello world\r\nbye\r\n"

     with open(crlf_txt, "r") as f6:
         assert list(f6) == ["hello world\n", "bye\n"]

     with open(crlf_txt, "r") as f6b:
         assert f6b.read() == "hello world\nbye\n"


def test_open_directory_raises_oserror():
    # opening a directory as a regular file must raise a catchable OSError
    # (previously this segfaulted instead)
    try:
        f = open(".")
        f.read()
        assert False, "expected OSError"
    except OSError:
        pass


def test_binary_read_negative():
    with open('rn.bin', 'wb') as g:
        g.write(b'abcdef')
    with open('rn.bin', 'rb') as g:
        try:
            g.read(-7)
            assert False
        except ValueError as e:
            assert str(e) == 'read length must be non-negative or -1'
        assert g.read(2) == b'ab'
        assert g.read(-1) == b'cdef'
    # text files accept any negative size
    with open('rn.bin') as f:
        assert f.read(-7) == 'abcdef'
    os.remove('rn.bin')


def test_read_chars_unicode():
    # text-mode read(n) counts characters, not bytes
    with open('utest.txt', 'w') as f:
        f.write('caf\xe9 \u20ac \U0001f600 end\n')
    with open('utest.txt') as f:
        a = f.read(5)
        b = f.read(3)
        c = f.read(1)
        d = f.read()
    assert a == 'caf\xe9 '
    assert b == '\u20ac \U0001f600'
    assert c == ' '
    assert d == 'end\n'
    os.remove('utest.txt')


def test_read_chars_invalid():
    # read(n)/readline(n) count decoded characters, also for invalid bytes
    with open('itest.txt', 'wb') as g:
        g.write(b'\x80\x80\x80abc\n\xe2\x82a\xe2\x82\xacb')
    with open('itest.txt', errors='replace') as f:
        assert f.read(2) == '\ufffd\ufffd'
        assert f.readline(3) == '\ufffdab'
        assert f.readline() == 'c\n'
        assert f.read(2) == '\ufffda'
    with open('itest.txt', errors='ignore') as f:
        assert f.read(2) == 'ab'
        assert f.readline() == 'c\n'
        assert f.read(2) == 'a\u20ac'
    with open('itest.txt', errors='surrogateescape') as f:
        assert f.read(2) == '\udc80\udc80'
        assert f.readline(3) == '\udc80ab'
        assert f.readline() == 'c\n'
        assert f.read(3) == '\udce2\udc82a'
    with open('itest.txt', encoding='ascii', errors='ignore') as f:
        assert f.read(4) == 'abc\n'
    os.remove('itest.txt')


def test_read_chars_truncated():
    # surrogateescape: a truncated sequence becomes one character per byte,
    # so read(n)/readline(n) must not take all of its bytes
    with open('ttest.txt', 'wb') as g:
        g.write(b'\xe2\x82abc\n\xf0\x9f\x98\n\xf0\x9f')
    with open('ttest.txt', errors='surrogateescape') as f:
        assert f.read(1) == '\udce2'
        assert f.read(1) == '\udc82'
        assert f.readline() == 'abc\n'
        assert f.readline(2) == '\udcf0\udc9f'
        assert f.readline() == '\udc98\n'
        assert f.read(1) == '\udcf0'  # (at eof)
        assert f.read() == '\udc9f'
    with open('ttest.txt', errors='surrogateescape', newline='') as f:
        assert f.readline(1) == '\udce2'
        assert f.read(2) == '\udc82a'
    os.remove('ttest.txt')


def test_crlf_ignore():
    # with errors='ignore', bytes that decode to nothing between '\r' and
    # '\n' do not split the line ending (newlines are translated after decoding)
    with open('ctest.txt', 'wb') as g:
        g.write(b'a\r\xff\nb\r\xe2\x82\n\xacc\r\xc3\xa9\nd\r\xff\xffe\r\xff')
    with open('ctest.txt', errors='ignore') as f:
        assert f.read() == 'a\nb\nc\n\xe9\nd\ne\n'
    with open('ctest.txt', errors='ignore') as f:
        assert f.readlines() == ['a\n', 'b\n', 'c\n', '\xe9\n', 'd\n', 'e\n']
    with open('ctest.txt', errors='ignore') as f:
        assert [f.read(1) for i in range(13)] == ['a', '\n', 'b', '\n', 'c', '\n', '\xe9', '\n', 'd', '\n', 'e', '\n', '']
    with open('ctest.txt', errors='replace') as f:
        assert f.read() == 'a\n\ufffd\nb\n\ufffd\n\ufffdc\n\xe9\nd\n\ufffd\ufffde\n\ufffd'
    with open('ctest.txt', 'wb') as g:
        g.write(b'a\r\xff\nb\r\xc3\xa9\nc\r\xffd')
    with open('ctest.txt', errors='ignore', newline='') as f:
        assert f.readlines() == ['a\r\n', 'b\r', '\xe9\n', 'c\r', 'd']
    # .. also a cut-short utf-8 sequence, which later bytes could still complete (1031-B1)
    for data in [b'a\r\xe2\nb\n', b'a\r\xe2\x82\nb\n', b'a\r\xf0\x9f\x98\nb', b'a\r\x80\xe2\nb',
                 b'a\r\xc3\xe2\x82\nb', b'a\r\xff\xff\xff\xe2\x82\nb']:
        with open('ctest.txt', 'wb') as g:
            g.write(data)
        with open('ctest.txt', errors='ignore', newline='') as f:
            assert f.readlines() == ['a\r\n', 'b\n' if data.endswith(b'\n') else 'b']
        with open('ctest.txt', errors='ignore', newline='') as f:
            assert f.readline(2) == 'a\r'
            assert f.readline() == '\n'
    with open('ctest.txt', 'wb') as g:
        g.write(b'a\r\xe2\x82\xacb\r\xf0\x9f\x98\x80\nc\r\xe2')
    with open('ctest.txt', errors='ignore', newline='') as f:
        assert f.readlines() == ['a\r', '€b\r', '\U0001f600\n', 'c\r']
    # tell() (or seek, or a write) after '\r', '\n' and ignored bytes between (1031-B2)
    with open('ctest.txt', 'wb') as g:
        g.write(b'x\r\xff\nyz\r\xe2\x82\nw')
    with open('ctest.txt', errors='ignore') as f:
        assert f.readline() == 'x\n'
        pos = f.tell()
        assert pos == 4
        assert f.readline() == 'yz\n'
        assert f.tell() == 10
        assert f.read() == 'w'
        f.seek(pos)
        assert f.read() == 'yz\nw'
    os.remove('ctest.txt')


def test_closed_is_bool():
    # 'closed' used to be an __ss_int, printing as 1/0 instead of True/False
    w = open('ctest.txt', 'w')
    assert str(w.closed) == 'False'
    w.write('x\n')
    w.close()
    assert str(w.closed) == 'True'
    assert w.closed is True

    r = open('ctest.txt', 'rb')
    assert str(r.closed) == 'False'
    r.close()
    assert str(r.closed) == 'True'
    os.remove('ctest.txt')


def test_use_after_close():
    # reading or iterating a closed file used to read the freed FILE
    with open('uctest.txt', 'w') as w:
        w.write('a\nb\nc\n')

    f = open('uctest.txt')
    f.close()
    try:
        for line in f:
            assert False
        assert False
    except ValueError as e:
        assert str(e).startswith('I/O operation on closed file')
    try:
        next(f)
        assert False
    except ValueError:
        pass

    f = open('uctest.txt')
    lines = []
    try:
        for line in f:
            lines.append(line)
            f.close()
        assert False
    except ValueError:
        pass
    assert lines == ['a\n']

    g = open('uctest.txt', 'rb')
    g.close()
    try:
        for bline in g:
            assert False
        assert False
    except ValueError:
        pass
    try:
        next(g)
        assert False
    except ValueError:
        pass
    os.remove('uctest.txt')


def test_buffer_shares_file():
    # .buffer is the same file: closing either one closes both (once)
    with open('bftest.txt', 'w') as w:
        w.write('hello\nworld\n')

    g = open('bftest.txt')
    assert g.buffer.read(5) == b'hello'
    g.buffer.close()
    assert g.closed and g.buffer.closed
    try:
        g.readline()
        assert False
    except ValueError:
        pass
    g.close()

    f = open('bftest.txt')
    f.close()
    assert f.buffer.closed
    try:
        f.buffer.read(10)
        assert False
    except ValueError:
        pass
    f.buffer.close()

    with open('bftest.txt') as h:
        h.buffer.close()
    assert h.closed

    os.remove('bftest.txt')


def test_stderr_backslashreplace():
    # as CPython, sys.stderr uses errors='backslashreplace': a surrogate is
    # written as an escape (and does not raise), unlike sys.stdout
    assert sys.stderr.errors == 'backslashreplace'
    assert sys.stdout.errors == 'surrogateescape'
    sys.stderr.flush()
    saved = os.dup(2)
    fd = os.open('stderr_bsr.txt', os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    os.dup2(fd, 2)
    os.close(fd)
    n = sys.stderr.write('a\udcffb\ud800\n')
    print('c\udc80d', file=sys.stderr)
    sys.stderr.flush()
    os.dup2(saved, 2)
    os.close(saved)
    assert n == 5
    with open('stderr_bsr.txt', 'rb') as f:
        assert f.read() == b'a\\udcffb\\ud800\nc\\udc80d\n'
    os.remove('stderr_bsr.txt')


def test_std_buffers():
    # the standard streams (and fdopen/popen files) used to have no .buffer
    assert sys.stdout.buffer.write(b'') == 0
    sys.stdout.buffer.flush()
    assert not sys.stderr.buffer.closed
    assert not sys.stdin.buffer.closed

    p = os.popen('echo hi')
    assert p.buffer.read() == b'hi\n'
    p.close()
    assert p.buffer.closed

    p = os.popen('echo hi')
    assert p.buffer.readline() == b'hi\n'
    p.buffer.close()
    assert p.closed

    r, w = os.pipe()
    os.write(w, b'piped')
    os.close(w)
    fr = os.fdopen(r)
    assert fr.buffer.read(5) == b'piped'
    fr.close()
    assert fr.buffer.closed


# helpers that close their files: on Windows an open file cannot be removed,
# and with a garbage collector it is not closed at a predictable moment

def rbytes(name):
    with open(name, 'rb') as g:
        return g.read()


def rtext(name, encoding=None, errors=None, newline=None):
    with open(name, encoding=encoding, errors=errors, newline=newline) as f:
        return f.read()


def nl(b):
    # text mode writes '\n' as os.linesep (as CPython, for newline=None)
    return b.replace(b'\n', os.linesep.encode())


def test_open_encoding():
    with open('uenc.txt', 'w', encoding='latin-1') as f:
        f.write('caf\xe9 \xff\n')
    assert rbytes('uenc.txt') == nl(b'caf\xe9 \xff\n')
    with open('uenc.txt', encoding='ISO-8859-1') as f:
        assert f.read(4) == 'caf\xe9'
        assert f.read() == ' \xff\n'
    # default utf-8 is strict, as in cpython
    caught = 0
    with open('uenc.txt') as f:
        try:
            f.read()
        except UnicodeDecodeError as e:
            assert (e.start, e.end) == (3, 4)
            caught += 1
    assert caught == 1
    assert rtext('uenc.txt', errors='surrogateescape') == 'caf\udce9 \udcff\n'
    assert rtext('uenc.txt', errors='ignore') == 'caf \n'
    assert rtext('uenc.txt', errors='replace') == 'caf\ufffd \ufffd\n'
    with open('uenc.txt', encoding='ascii', errors='replace') as f:
        assert f.readline() == 'caf\ufffd \ufffd\n'

    with open('uenc.txt', 'w', encoding='cp1252') as f:
        f.write('\u20ac \u201cq\u201d \u2013 na\xefve\u2026\n')
    assert rbytes('uenc.txt') == nl(b'\x80 \x93q\x94 \x96 na\xefve\x85\n')
    with open('uenc.txt', encoding='windows-1252') as f:
        assert f.read(3) == '\u20ac \u201c'
        assert f.readline() == 'q\u201d \u2013 na\xefve\u2026\n'

    with open('uenc.txt', 'w', encoding='ascii', errors='replace') as f:
        f.write('\xe9\u20acx\n')
    assert rtext('uenc.txt') == '??x\n'
    caught = 0
    with open('uenc.txt', 'w', encoding='latin-1') as f:
        try:
            f.write('\u20ac')
        except UnicodeEncodeError:
            caught += 1
    with open('uenc.txt', 'w') as f:
        try:
            f.write('a\udcffb')
        except UnicodeEncodeError:
            caught += 1
    assert caught == 2
    os.remove('uenc.txt')


def test_open_utf8_sig():
    with open('usig.txt', 'w', encoding='utf-8-sig') as f:
        f.write('caf\xe9')
        f.write('!\n')
    assert rbytes('usig.txt') == nl(b'\xef\xbb\xbfcaf\xc3\xa9!\n')
    assert rtext('usig.txt', encoding='utf-8-sig') == 'caf\xe9!\n'
    assert rtext('usig.txt') == '\ufeffcaf\xe9!\n'
    with open('usig.txt', encoding='utf-8-sig') as f:
        assert f.read(1) == 'c'
        assert f.readline() == 'af\xe9!\n'
    with open('usig.txt', 'a', encoding='utf-8-sig') as f:  # no second bom
        f.write('more\n')
    assert rbytes('usig.txt') == nl(b'\xef\xbb\xbfcaf\xc3\xa9!\nmore\n')
    with open('usig.txt', 'wb') as g:
        g.write(b'plain\n')
    assert rtext('usig.txt', encoding='utf-8-sig') == 'plain\n'
    os.remove('usig.txt')
    with open('usig.txt', 'a', encoding='utf-8-sig') as f:  # new file: bom
        f.write('x')
    assert rbytes('usig.txt') == b'\xef\xbb\xbfx'
    with open('usig.txt', 'w', encoding='cp1251') as f:
        f.write('\u041f\u0440\u0438\u0432\u0435\u0442\n')
    assert rbytes('usig.txt') == nl(b'\xcf\xf0\xe8\xe2\xe5\xf2\n')
    with open('usig.txt', encoding='cp1251') as f:
        assert f.read(3) == '\u041f\u0440\u0438'
    os.remove('usig.txt')


def test_utf8_sig_seek():
    # seek() resets the bom state, as cpython resets the codec
    with open('usig2.txt', 'w+', encoding='utf-8-sig') as f:
        f.write('hi\n')
        f.seek(0)
        assert f.read() == 'hi\n'
    with open('usig2.txt', encoding='utf-8-sig') as f:
        assert f.read() == 'hi\n'
        f.seek(0)
        assert f.read() == 'hi\n'
    with open('usig2.txt', 'w', encoding='utf-8-sig') as f:
        f.write('abc')
        f.seek(0)
        f.write('X')
    assert rbytes('usig2.txt') == b'\xef\xbb\xbfXbc'
    with open('usig2.txt', 'r+', encoding='utf-8-sig') as f:
        f.seek(0)
        f.write('Y')
    assert rbytes('usig2.txt') == b'\xef\xbb\xbfYbc'
    with open('usig2.txt', 'w', encoding='utf-8-sig') as f:
        f.write('abc')
        f.seek(0, 2)
        f.write('d')
    assert rbytes('usig2.txt') == b'\xef\xbb\xbfabcd'
    os.remove('usig2.txt')


def test_append_plus_starts_at_end():
    with open('aplus.txt', 'w') as f:
        f.write('hello')
    with open('aplus.txt', 'a+') as f:
        assert f.tell() == 5
        assert f.read() == ''
        f.seek(0)
        assert f.read() == 'hello'
    with open('aplus.txt', 'ab+') as g:
        assert g.tell() == 5
        assert g.read() == b''
        g.seek(0)
        assert g.read() == b'hello'
    os.remove('aplus.txt')


def test_open_bad_args():
    caught = 0
    try:
        open(datafile, encoding='utf-99')
    except LookupError:
        caught += 1
    try:
        open(datafile, 'rb', encoding='utf-8')
    except ValueError:
        caught += 1
    try:
        open(datafile, newline='x')
    except ValueError:
        caught += 1
    assert caught == 3


def test_open_unknown_errors():
    # as cpython, an unknown error handler is only looked up when needed
    with open('uerr.txt', 'w', encoding='ascii', errors='bogus') as f:
        f.write('abc\n')
        error = ''
        try:
            f.write('\xe9')
        except LookupError as e:
            error = str(e)
        assert error == "unknown error handler name 'bogus'"
    with open('uerr.txt', errors='bogus') as f:
        assert f.read() == 'abc\n'
    with open('uerr.txt', 'wb') as g:
        g.write(b'abc\xff\n')
    error = ''
    try:
        with open('uerr.txt', errors='bogus') as f:
            f.read()
    except LookupError as e:
        error = str(e)
    assert error == "unknown error handler name 'bogus'"
    os.remove('uerr.txt')


def test_open_mode_keyword():
    # (own file: a checkout may turn testdata into crlf, e.g. git autocrlf on Windows)
    with open('umode.txt', mode='wb') as f:
        f.write(b'hop\nhop\nhoppa!\n')
    with open('umode.txt', mode='rb') as f:
        assert f.read() == b'hop\nhop\nhoppa!\n'
    with open('umode.txt', mode='r', encoding='utf-8') as g:
        assert g.read() == 'hop\nhop\nhoppa!\n'
    os.remove('umode.txt')


def test_open_encoding_attributes():
    # the names are kept as given (CPython doesn't normalize them)
    with open('uattr.txt', 'w') as f:
        assert f.encoding == 'utf-8'
        assert f.errors == 'strict'
    with open('uattr.txt', encoding='Latin-1', errors='replace') as f:
        assert f.encoding == 'Latin-1'
        assert f.errors == 'replace'
    with open('uattr.txt', 'a', encoding='utf-8-sig', errors='surrogateescape') as f:
        assert f.encoding == 'utf-8-sig'
        assert f.errors == 'surrogateescape'
    f = open('uattr.txt', errors='bogus')  # (unknown handlers only fail when used)
    assert f.errors == 'bogus'
    f.close()
    os.remove('uattr.txt')


def test_open_newline():
    with open('unl.txt', 'w', newline='') as f:
        f.write('a\r\nb\n')
    assert rbytes('unl.txt') == b'a\r\nb\n'
    assert rtext('unl.txt') == 'a\nb\n'
    assert rtext('unl.txt', newline='') == 'a\r\nb\n'
    with open('unl.txt', newline='\n') as f:
        assert f.readlines() == ['a\r\n', 'b\n']
    os.remove('unl.txt')


def test_open_unicode_name():
    # non-ascii file names (the wide apis on Windows, not the ansi code page)
    fn = 'u_caf\xe9_\u20ac_\U0001f600.txt'
    with open(fn, 'w') as f:
        f.write('x')
    assert fn in os.listdir('.')
    assert rtext(fn) == 'x'
    with open(fn.encode(), 'rb') as g:  # bytes name
        assert g.read() == b'x'
    os.remove(fn)
    assert not os.path.exists(fn)


def test_seek_returns_position():
    with open('useek.bin', 'wb') as g:
        g.write(b'abcdef')
    with open('useek.bin') as f:
        assert f.seek(2) == 2
        assert f.read() == 'cdef'
        assert f.seek(0, 2) == 6
    with open('useek.bin', 'rb') as h:
        assert h.seek(2) == 2
        assert h.seek(-1, 2) == 5
        assert h.seek(-2, 1) == 3
        assert h.read() == b'def'
    os.remove('useek.bin')


def test_open_exclusive():
    if os.path.exists('uexcl.txt'):
        os.remove('uexcl.txt')
    with open('uexcl.txt', 'x') as f:
        f.write('hop')
    assert rtext('uexcl.txt') == 'hop'
    try:
        open('uexcl.txt', 'x')
        assert False
    except FileExistsError:
        pass
    os.remove('uexcl.txt')
    with open('uexcl.txt', 'xb') as g:
        g.write(b'hop')
    assert rbytes('uexcl.txt') == b'hop'
    os.remove('uexcl.txt')


def test_open_mode_order():
    # the mode characters may come in any order ('br' is 'rb')
    with open('uorder.txt', 'bw') as g:
        g.write(b'pre')
    with open('uorder.txt', 'ba') as g:
        g.write(b'cious\n')
    with open('uorder.txt', 'br') as g:
        assert g.read() == b'precious\n'
    with open('uorder.txt', 'tr') as f:
        assert f.read() == 'precious\n'
    with open('uorder.txt', '+r') as f:
        assert f.read(3) == 'pre'
    with open('uorder.txt', 'b+r') as g:
        assert g.read(3) == b'pre'
        g.write(b'C')
    assert rtext('uorder.txt') == 'preCious\n'
    with open('uorder.txt', 'tw') as f:
        f.write('x')
    with open('uorder.txt', '+a') as f:
        f.write('y')
    assert rtext('uorder.txt') == 'xy'
    os.remove('uorder.txt')
    with open('uorder.txt', 'bx') as g:
        g.write(b'hop')
    try:
        open('uorder.txt', 'tx')
        assert False
    except FileExistsError:
        pass
    os.remove('uorder.txt')
    with open('uorder.txt', 'tx') as f:
        f.write('hop')
    fd = os.open('uorder.txt', os.O_RDONLY)
    with os.fdopen(fd, 'br') as g:
        assert g.read() == b'hop'
    fd = os.open('uorder.txt', os.O_RDONLY)
    with os.fdopen(fd, 'tr') as f:
        assert f.read() == 'hop'
    os.remove('uorder.txt')


def _with_close_fails(name: str) -> int:
    with open(name, 'w') as f:
        f.write('abc')
        os.close(f.fileno())  # flush/close in __exit__ fails with EBADF
        return 1
    return 2


def test_with_exit_raises():
    # an exception from __exit__ (failing close/flush) can be caught
    caught = 0
    try:
        with open(outputfile, 'w') as f:
            f.write('abc')
            os.close(f.fileno())
    except OSError as e:
        assert e.errno == 9
        caught += 1
    # also after return from inside the block
    try:
        _with_close_fails(outputfile)
    except OSError as e:
        assert e.errno == 9
        caught += 1
    # an exception from __exit__ replaces the one from the body
    try:
        with open(outputfile, 'w') as f:
            f.write('abc')
            os.close(f.fileno())
            raise ValueError('body')
    except ValueError:
        assert False
    except OSError as e:
        assert e.errno == 9
        caught += 1
    # body exception still propagates when __exit__ succeeds
    try:
        with open(outputfile, 'w') as f:
            raise ValueError('body')
    except ValueError as e:
        assert str(e) == 'body'
        caught += 1
    assert f.closed
    if sys.platform.startswith('linux'):
        try:
            with open('/dev/full', 'w') as f:
                f.write('abc')
        except OSError as e:
            assert e.errno == 28
            caught += 1
        assert caught == 5
    else:
        assert caught == 4


def test_open_read_write_switch():
    # C stdio needs a seek between reading and writing (macOS, windows)
    with open('uswitch.bin', 'w+b') as g:
        g.write(b'12345')
        g.seek(1)
        assert g.read(2) == b'23'
        g.write(b'Z')
        assert g.read() == b'5'
        g.seek(0)
        assert g.read() == b'123Z5'
    with open('uswitch.bin', 'r+b') as g:
        g.write(b'A')
        assert g.read(2) == b'23'
        g.write(b'B')
        assert g.tell() == 4
        assert g.readline() == b'5'
    assert rbytes('uswitch.bin') == b'A23B5'
    with open('uswitch.txt', 'w+') as f:
        f.write('hello\n')
        f.seek(0)
        assert f.read() == 'hello\n'
        f.write('more')
        f.seek(0)
        assert f.readline() == 'hello\n'
        assert f.read() == 'more'
    assert rtext('uswitch.txt') == 'hello\nmore'
    os.remove('uswitch.bin')
    os.remove('uswitch.txt')


def test_newline_empty_splits_on_cr():
    # newline='': lines end at '\r', '\n' and '\r\n', untranslated
    with open('ucr.bin', 'wb') as g:
        g.write(b'a\rb\r\nc\n\rd')
    with open('ucr.bin', newline='') as f:
        assert f.readlines() == ['a\r', 'b\r\n', 'c\n', '\r', 'd']
    with open('ucr.bin', newline='') as f:
        assert [l for l in f] == ['a\r', 'b\r\n', 'c\n', '\r', 'd']
    with open('ucr.bin', newline='') as f:
        assert f.readline(3) == 'a\r'
        assert f.readline(2) == 'b\r'  # size limit between '\r' and '\n'
        assert f.readline() == '\n'
    with open('ucr.bin', newline='\n') as f:
        assert f.readlines() == ['a\rb\r\n', 'c\n', '\rd']
    os.remove('ucr.bin')


def test_readline_size_counts_characters():
    with open('usz.bin', 'wb') as g:
        g.write('\xe4\xf6\n\u20acx\r\ny'.encode())
    with open('usz.bin', encoding='utf-8') as f:
        assert f.readline(1) == '\xe4'
        assert f.readline(1) == '\xf6'
        assert f.readline(1) == '\n'
        assert f.readline(2) == '\u20acx'
        assert f.readline(1) == '\n'
        assert f.readline(0) == ''
        assert f.readline(5) == 'y'
    with open('usz.bin', encoding='utf-8', newline='') as f:
        assert f.readline(2) == '\xe4\xf6'
    os.remove('usz.bin')


def test_pending_cr_seek_tell():
    # '\r\n' is translated lazily: seek() must forget a pending '\r', and
    # tell() must count the '\n' that belongs to it
    with open('ucr2.bin', 'wb') as g:
        g.write(b'\nq\r')
    with open('ucr2.bin') as f:
        f.readline()
        f.readline()
        f.seek(0)
        assert f.readline() == '\n'
    with open('ucr2.bin', 'wb') as g:
        g.write(b'a\r\nb\r\n')
    with open('ucr2.bin') as f:
        f.readline()
        assert f.tell() == 3
        assert f.readline() == 'b\n'
        assert f.tell() == 6
        f.seek(3)
        assert f.read() == 'b\n'
    # .. also with lone '\n's (windows text mode ftell() counts each as '\r\n')
    with open('ucr2.bin', 'wb') as g:
        g.write(b'a\nbc\nd\x1ae\r\nf')
    with open('ucr2.bin') as f:
        assert f.readline() == 'a\n'
        assert f.tell() == 2
        assert f.readline() == 'bc\n'
        assert f.tell() == 5
        assert f.readline() == 'd\x1ae\n'  # (no ctrl-z eof)
        assert f.tell() == 10
        assert f.read() == 'f'
        f.seek(2)
        assert f.read() == 'bc\nd\x1ae\nf'
    # newline=None writes os.linesep
    with open('ucr2.bin', 'w') as f:
        assert f.write('a\nb\r\n') == 5
    with open('ucr2.bin', 'rb') as g:
        if sys.platform == 'win32':
            assert g.read() == b'a\r\nb\r\r\n'
        else:
            assert g.read() == b'a\nb\r\n'
    with open('ucr2.bin', 'w', newline='') as f:
        f.write('a\nb')
    with open('ucr2.bin', 'rb') as g:
        assert g.read() == b'a\nb'
    os.remove('ucr2.bin')


def test_text_seek_restrictions():
    # text files only seek to a tell() position or the end (cpython raises
    # io.UnsupportedOperation, which is an OSError, for relative seeks)
    with open('useek2.txt', 'wb') as g:  # no '\r\n' on windows
        g.write(b'hello world\n')
    with open('useek2.txt') as f:
        for i in range(4):
            error = ''
            try:
                if i == 0: f.seek(-6, 2)
                elif i == 1: f.seek(3, 1)
                elif i == 2: f.seek(-1)
                else: f.seek(0, 3)
            except OSError as e:
                error = e.__class__.__name__ + ': ' + str(e)
            except ValueError as e:
                error = 'ValueError: ' + str(e)
            if i == 0:
                assert error == "UnsupportedOperation: can't do nonzero end-relative seeks"
            elif i == 1:
                assert error == "UnsupportedOperation: can't do nonzero cur-relative seeks"
            elif i == 2:
                assert error == 'ValueError: negative seek position -1'
            else:
                assert error == 'ValueError: invalid whence (3, should be 0, 1 or 2)'
        f.seek(0, 2)
        assert f.read() == ''
        f.seek(6)
        f.seek(0, 1)
        assert f.read() == 'world\n'
    with open('useek2.txt', 'rb') as g:  # binary files may seek relatively
        g.seek(-6, 2)
        assert g.read() == b'world\n'
    os.remove('useek2.txt')


def test_utf8_sig():
    # a bom is written once, and skipped on reading
    with open('usig.txt', 'w', encoding='utf-8-sig') as f:
        f.write('h\u00e9')
    with open('usig.txt', 'rb') as g:
        assert g.read() == b'\xef\xbb\xbfh\xc3\xa9'
    with open('usig.txt', encoding='utf-8-sig') as f:
        assert f.read() == 'h\u00e9'
    # no bom: nothing is skipped
    with open('usig.txt', 'wb') as g:
        g.write(b'\xef\xbbx')
    with open('usig.txt', encoding='utf-8-sig', errors='replace') as f:
        assert f.read() == '\ufffdx'
    with open('usig.txt', 'wb') as g:
        g.write(b'ab')
    with open('usig.txt', encoding='utf-8-sig') as f:
        assert f.read() == 'ab'
    os.remove('usig.txt')


def test_open_invalid_mode():
    # as cpython, the mode is validated before anything is opened (fopen()
    # would truncate the file for 'wa', and ignore most other mistakes)
    with open('umode.txt', 'w') as f:
        f.write('precious\n')
    errors = []
    try:
        open('umode.txt', 'wa')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', 'rw')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', 'xa')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', 'rr')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', 'r ')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', 'r++')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', 'q')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', 'U')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', 'rU')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', '')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', '+')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', 'bt')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', 'wab')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', 'rbb')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', 'b')
    except ValueError as e:
        errors.append(str(e))
    assert errors == [
        'must have exactly one of create/read/write/append mode',
        'must have exactly one of create/read/write/append mode',
        'must have exactly one of create/read/write/append mode',
        "invalid mode: 'rr'",
        "invalid mode: 'r '",
        "invalid mode: 'r++'",
        "invalid mode: 'q'",
        "invalid mode: 'U'",
        "invalid mode: 'rU'",
        'Must have exactly one of create/read/write/append mode and at most one plus',
        'Must have exactly one of create/read/write/append mode and at most one plus',
        "can't have text and binary mode at once",
        'must have exactly one of create/read/write/append mode',
        "invalid mode: 'rbb'",
        'Must have exactly one of create/read/write/append mode and at most one plus',
    ]
    # before the other arguments, too
    try:
        open('umode.txt', 'rr', encoding='bogus')
    except ValueError as e:
        errors.append(str(e))
    try:
        open('umode.txt', 'rbt', encoding='latin-1')
    except ValueError as e:
        errors.append(str(e))
    assert errors[-2:] == ["invalid mode: 'rr'", "can't have text and binary mode at once"]
    with open('umode.txt') as f:
        assert f.read() == 'precious\n'
    # valid combinations
    with open('umode.txt', 'a+t') as f:
        assert f.mode == 'a+t'
    with open('umode.txt', 'r+b') as g:
        assert g.read() == nl(b'precious\n')
    os.remove('umode.txt')


def test_enter_exit_results():
    # __enter__ returns the file itself and __exit__ returns None
    f = open('eetest.txt', 'w')
    assert f.__enter__() is f
    f.write('hoi')
    assert f.__exit__() is None
    assert f.closed
    g = open('eetest.txt', 'rb')
    h = g.__enter__()
    assert h.read() == b'hoi'
    assert g.__exit__() is None
    assert g.closed
    os.remove('eetest.txt')


def test_open_buffering():
    # buffering as the third positional argument, as in cpython
    f = open('ubuf.txt', 'w', -1)
    f.write('x')
    f.close()
    with open('ubuf.txt', 'r', -1, 'utf-8', 'strict', None) as g:
        assert g.read() == 'x'
    with open('ubuf.txt', 'rb', -1) as h:
        assert h.read() == b'x'
    with open('ubuf.txt', buffering=1) as g:
        assert g.read() == 'x'
    # unbuffered text is not allowed; as cpython, the file is opened first
    errors = []
    try:
        open('ubuf.txt', 'r', 0)
    except ValueError as e:
        errors.append(str(e))
    with open('ubuf.txt') as g:
        assert g.read() == 'x'
    try:
        open('ubuf.txt', 'w', buffering=0)
    except ValueError as e:
        errors.append(str(e))
    assert errors == ["can't have unbuffered text I/O"] * 2
    assert os.stat('ubuf.txt').st_size == 0
    try:
        open(os.path.join('ubuf_nodir', 'x'), 'w', 0)
    except FileNotFoundError:
        errors.append('FileNotFoundError')
    assert errors[-1] == 'FileNotFoundError'
    # unbuffered binary: each write reaches the file at once
    with open('ubuf.txt', 'wb', 0) as h:
        h.write(b'abc')
        assert os.stat('ubuf.txt').st_size == 3
        h.write(b'd\ne')
        assert os.stat('ubuf.txt').st_size == 6
    with open('ubuf.txt', 'rb', 0) as h:
        assert h.read(1) == b'a'
        assert h.readline() == b'bcd\n'
        assert h.read() == b'e'
    # line buffered text: flushed at each newline (Windows has no line buffering)
    with open('ubuf.txt', 'w', 1) as g:
        g.write('ab')
        g.write('c\n')
        if sys.platform != 'win32':
            assert os.stat('ubuf.txt').st_size == 4
        g.write('d')
    assert os.stat('ubuf.txt').st_size == nl_size(5)
    # buffer sizes (and line buffering in binary mode, which cpython warns about)
    for size in [2, 4096, 1 << 20, -5]:
        with open('ubuf.txt', 'w', size) as g:
            g.write('hello\n' * 1000)
        with open('ubuf.txt', 'r', size) as g:
            assert g.readlines() == ['hello\n'] * 1000
    with open('ubuf.txt', 'rb', 1) as h:
        assert len(h.read()) == nl_size(6000, 1000)
    os.remove('ubuf.txt')


def nl_size(n, lines=1):
    # file size of text with 'lines' newlines (os.linesep on Windows)
    return n + lines * (len(os.linesep) - 1)


def closed_mode(g):
    m = g.mode
    g.close()
    return m


def test_binary_mode_normalised():
    # as cpython's FileIO.mode: a binary file reports 'rb', 'wb', 'ab' or 'xb'
    # (plus '+'), however the mode was spelled; a text file keeps it as given,
    # and its .buffer has the binary mode and the same name
    with open('bmode.bin', 'bw') as g:
        assert g.mode == 'wb'
    assert closed_mode(open('bmode.bin', 'br')) == 'rb'
    assert closed_mode(open('bmode.bin', 'rb')) == 'rb'
    assert closed_mode(open('bmode.bin', 'b+r')) == 'rb+'
    assert closed_mode(open('bmode.bin', 'rb+')) == 'rb+'
    assert closed_mode(open('bmode.bin', 'w+b')) == 'rb+'
    assert closed_mode(open('bmode.bin', 'ba')) == 'ab'
    assert closed_mode(open('bmode.bin', 'a+b')) == 'ab+'
    os.remove('bmode.bin')
    with open('bmode.bin', 'bx') as g:
        assert g.mode == 'xb'
    os.remove('bmode.bin')
    with open('bmode.bin', 'x+b') as g:
        assert g.mode == 'xb+'

    with open('bmode.bin') as f:
        assert f.mode == 'r'
        assert f.buffer.mode == 'rb'
        assert f.buffer.name == 'bmode.bin'
    with open('bmode.bin', 'tr') as f:
        assert f.mode == 'tr'
        assert f.buffer.mode == 'rb'
    with open('bmode.bin', 'w+') as f:
        assert f.mode == 'w+'
        assert f.buffer.mode == 'rb+'
    with open('bmode.bin', 'a') as f:
        assert f.buffer.mode == 'ab'

    fd = os.open('bmode.bin', os.O_RDWR)
    with os.fdopen(fd, 'w+b') as g:
        assert g.mode == 'rb+'
    fd = os.open('bmode.bin', os.O_RDONLY)
    with os.fdopen(fd, 'br') as g:
        assert g.mode == 'rb'
    fd = os.open('bmode.bin', os.O_RDWR)
    with os.fdopen(fd, 'r+') as f:
        assert f.mode == 'r+'
        assert f.buffer.mode == 'rb+'
    os.remove('bmode.bin')

    assert sys.stdin.buffer.mode == 'rb'
    assert sys.stdout.buffer.mode == 'wb'
    assert sys.stderr.buffer.name == '<stderr>'


def test_enter_closed():
    # 'with' on an already closed file raises ValueError
    f = open('ectest.txt', 'w')
    f.close()
    try:
        with f:
            assert False
        assert False
    except ValueError as e:
        assert str(e).startswith('I/O operation on closed file')
    g = open('ectest.txt', 'rb')
    g.close()
    try:
        with g:
            assert False
        assert False
    except ValueError as e:
        assert str(e).startswith('I/O operation on closed file')
    os.remove('ectest.txt')


def _rws_text(f):
    return (f.readable(), f.writable(), f.seekable())


def _rws_binary(f):
    return (f.readable(), f.writable(), f.seekable())


def _rws_closed_text(f):
    result = []
    for i in range(3):
        try:
            if i == 0:
                result.append(str(f.readable()))
            elif i == 1:
                result.append(str(f.writable()))
            else:
                result.append(str(f.seekable()))
        except ValueError as e:
            assert str(e) == 'I/O operation on closed file'
            result.append('VE')
    return ' '.join(result)


def _rws_closed_binary(f):
    result = []
    for i in range(3):
        try:
            if i == 0:
                result.append(str(f.readable()))
            elif i == 1:
                result.append(str(f.writable()))
            else:
                result.append(str(f.seekable()))
        except ValueError as e:
            assert str(e) == 'I/O operation on closed file'
            result.append('VE')
    return ' '.join(result)


def test_readable_writable_seekable():
    # as cpython: from the mode, and seekable() asks the os
    name = 'rwstest.txt'
    f = open(name, 'w')
    assert _rws_text(f) == (False, True, True)
    assert _rws_binary(f.buffer) == (False, True, True)
    f.close()
    assert _rws_closed_text(f) == 'False VE VE'
    f = open(name, 'r')
    assert _rws_text(f) == (True, False, True)
    assert _rws_binary(f.buffer) == (True, False, True)
    f.close()
    assert _rws_closed_text(f) == 'VE False VE'
    f = open(name, 'r+')
    assert _rws_text(f) == (True, True, True)
    f.close()
    assert _rws_closed_text(f) == 'VE VE VE'
    f = open(name, 'a')
    assert _rws_text(f) == (False, True, True)
    f.close()
    f = open(name, 'a+')
    assert _rws_text(f) == (True, True, True)
    f.close()
    f = open(name, 'w+')
    assert _rws_text(f) == (True, True, True)
    f.close()

    g = open(name, 'rb')
    assert _rws_binary(g) == (True, False, True)
    g.close()
    assert _rws_closed_binary(g) == 'VE False VE'
    g = open(name, 'wb')
    assert _rws_binary(g) == (False, True, True)
    g.close()
    assert _rws_closed_binary(g) == 'False VE VE'
    g = open(name, 'r+b')
    assert _rws_binary(g) == (True, True, True)
    g.close()
    assert _rws_closed_binary(g) == 'VE VE VE'
    g = open(name, 'ab')
    assert _rws_binary(g) == (False, True, True)
    g.close()
    g = open(name, 'w+b')
    assert _rws_binary(g) == (True, True, True)
    g.close()
    os.remove(name)

    x = open(name, 'x')
    assert _rws_text(x) == (False, True, True)
    x.close()
    os.remove(name)

    # a pipe is not seekable
    rfd, wfd = os.pipe()
    pr = os.fdopen(rfd)
    pw = os.fdopen(wfd, 'wb')
    assert _rws_text(pr) == (True, False, False)
    assert _rws_binary(pw) == (False, True, False)
    pw.close()
    pr.close()

    assert sys.stdin.readable() and not sys.stdin.writable()
    assert sys.stdout.writable() and not sys.stdout.readable()


def _text_op_error(f, op):
    try:
        if op == 0: f.read()
        elif op == 1: f.readline()
        elif op == 2: f.readlines()
        elif op == 3: next(iter(f))
        elif op == 4: f.write('x')
        elif op == 5: f.writelines(['x'])
        elif op == 6: f.truncate(0)
        elif op == 7: f.flush()
        elif op == 8: f.seek(0)
        elif op == 9: f.tell()
        elif op == 10: f.fileno()
        elif op == 11: f.isatty()
        else: f.__enter__()
    except StopIteration:
        return 'StopIteration'
    except OSError as e:
        return e.__class__.__name__ + ': ' + str(e)
    except ValueError as e:
        return 'ValueError: ' + str(e)
    return ''


def _binary_op_error(f, op):
    try:
        if op == 0: f.read()
        elif op == 1: f.readline()
        elif op == 2: f.readlines()
        elif op == 3: next(iter(f))
        elif op == 4: f.write(b'x')
        elif op == 5: f.writelines([b'x'])
        elif op == 6: f.truncate(0)
        elif op == 7: f.flush()
        elif op == 8: f.seek(0)
        elif op == 9: f.tell()
        elif op == 10: f.fileno()
        elif op == 11: f.isatty()
        else: f.__enter__()
    except StopIteration:
        return 'StopIteration'
    except OSError as e:
        return e.__class__.__name__ + ': ' + str(e)
    except ValueError as e:
        return 'ValueError: ' + str(e)
    return ''


def _fill(f, n: int) -> bytearray:  # (also takes a BytesIO, via file_binary)
    buf = bytearray(n)
    k = f.readinto(buf)
    return buf[:k]


def test_binary_readinto_read1():
    # binary files have readinto/readinto1/read1, as BytesIO and GzipFile
    with open('rinto.bin', 'wb') as w:
        w.write(b'abcdefgh')
        try:
            w.readinto(bytearray(2))
            assert False
        except OSError as e:
            assert str(e) == 'read'
        try:
            w.read1(2)
            assert False
        except OSError as e:
            assert str(e) == 'read1'
    f = open('rinto.bin', 'rb')
    b = bytearray(3)
    assert f.readinto(b) == 3 and b == bytearray(b'abc')
    assert f.readinto1(b) == 3 and b == bytearray(b'def')
    assert f.read1(1) == b'g'
    assert f.read1() == b'h'
    big = bytearray(5)
    assert f.readinto(big) == 0 and big == bytearray(5)
    assert f.readinto(bytearray()) == 0
    f.seek(6)
    assert f.readinto(big) == 2 and big == bytearray(b'gh\x00\x00\x00')
    try:
        f.readinto(b'xx')
        assert False
    except TypeError as e:
        assert str(e) == 'readinto() argument must be read-write bytes-like object, not bytes'
    f.close()
    try:
        f.readinto(bytearray(2))
        assert False
    except ValueError as e:
        assert str(e) == 'readinto of closed file'
    try:
        f.read1(2)
        assert False
    except ValueError as e:
        assert str(e) == 'read of closed file'
    with open('rinto.bin') as t:
        bb = bytearray(4)
        assert t.buffer.readinto(bb) == 4 and bb == bytearray(b'abcd')
    with open('rinto.bin', 'rb') as g:
        assert _fill(g, 4) == bytearray(b'abcd')
    assert _fill(io.BytesIO(b'12345'), 3) == bytearray(b'123')
    os.remove('rinto.bin')


def test_open_fd():
    # open() also takes a file descriptor (as os.fdopen); closing the file
    # closes it
    fd = os.open('openfd.txt', os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    f = open(fd, 'w', encoding='utf-8')
    assert f.fileno() == fd and str(f.name) == str(fd) and f.mode == 'w'
    assert f.write('fd é\nline2\n') == 11
    f.close()
    try:
        os.close(fd)
        assert False
    except OSError as e:
        assert e.errno == 9
    fd = os.open('openfd.txt', os.O_RDONLY)
    with open(fd) as g:
        assert g.readline() == 'fd é\n'
        assert g.readlines() == ['line2\n']
    fb = open(os.open('openfd.txt', os.O_RDONLY), 'rb')
    assert fb.mode == 'rb'
    assert fb.read(2) == b'fd'
    fb.close()
    os.remove('openfd.txt')
    r, w = os.pipe()
    pw = open(w, 'wb')
    pw.write(b'pipe\n')
    pw.close()
    pr = open(r)
    assert pr.read() == 'pipe\n'
    pr.close()
    try:
        open(-1)
        assert False
    except ValueError as e2:
        assert str(e2) == 'negative file descriptor'
    try:
        open(9999, 'rb')
        assert False
    except OSError as e3:
        assert e3.errno == 9


def test_line_buffering():
    # as CPython: True for text files opened with buffering=1
    f = open('lbuf.txt', 'w', buffering=1)
    assert f.line_buffering == True
    f.close()
    f = open('lbuf.txt', 'r', buffering=1)
    assert f.line_buffering == True
    f.close()
    f = open('lbuf.txt', 'a+', buffering=1)
    assert f.line_buffering == True
    f.close()
    for buffering in [-1, 4096]:
        f = open('lbuf.txt', 'w', buffering)
        assert f.line_buffering == False
        f.close()
    f = os.fdopen(os.open('lbuf.txt', os.O_WRONLY), 'w', 1)
    assert f.line_buffering
    f.close()
    f = os.fdopen(os.open('lbuf.txt', os.O_WRONLY), 'w')
    assert not f.line_buffering
    f.close()
    f = open(os.open('lbuf.txt', os.O_WRONLY), 'w', 1)
    assert f.line_buffering
    f.close()
    os.remove('lbuf.txt')
    # std streams: a terminal (and stderr always), unless python runs unbuffered
    for g in [sys.stdin, sys.stdout, sys.stderr]:
        assert g.line_buffering in (True, False)


def test_unsupported_operation():
    # as CPython: reading a file not opened for reading (or writing one not
    # opened for writing) raises io.UnsupportedOperation (an OSError) instead
    # of '[Errno 9] Bad file descriptor', and the closed-file messages match
    us = 'UnsupportedOperation: '
    cl = 'ValueError: I/O operation on closed file.'
    cl2 = 'ValueError: I/O operation on closed file'
    with open('unsup.txt', 'w') as f:
        f.write('hello\n')

    # text, open
    f = open('unsup.txt')
    errors = [_text_op_error(f, op) for op in range(13)]
    assert errors == ['', '', '', 'StopIteration', us + 'not writable', us + 'not writable', us + 'truncate'] + [''] * 6, str(errors)
    f.close()
    for i in range(3):
        if i == 0: f = open('unsup.txt', 'w')
        elif i == 1: f = open('unsup.txt', 'a')
        else: f = open('unsup.txt', 'r+')
        errors = [_text_op_error(f, op) for op in range(6)]
        if i < 2:
            assert errors == [us + 'not readable'] * 4 + ['', ''], str(errors)
        else:
            assert errors == ['', '', '', 'StopIteration', '', ''], str(errors)
        f.close()
    # text, closed
    for i in range(2):
        if i == 0: f = open('unsup.txt')
        else: f = open('unsup.txt', 'w')
        f.close()
        errors = [_text_op_error(f, op) for op in range(13)]
        assert errors == [cl] * 10 + [cl2, cl2, cl], str(errors)

    # binary, open
    b = open('unsup.txt', 'rb')
    errors = [_binary_op_error(b, op) for op in range(13)]
    assert errors[4:7] == [us + 'write', us + 'write', us + 'truncate'], str(errors)
    assert errors[7:] == [''] * 6, str(errors)
    b.close()
    for i in range(2):
        if i == 0: b = open('unsup.txt', 'wb')
        else: b = open('unsup.txt', 'ab')
        errors = [_binary_op_error(b, op) for op in range(6)]
        assert errors == [us + 'read'] * 4 + ['', ''], str(errors)
        b.close()
    # binary, closed (the mode check comes first for read and write)
    b = open('unsup.txt', 'rb')
    b.close()
    errors = [_binary_op_error(b, op) for op in range(13)]
    assert errors == ['ValueError: read of closed file', 'ValueError: readline of closed file', cl, cl,
                      us + 'write', cl, 'ValueError: truncate of closed file', cl,
                      'ValueError: seek of closed file', cl2, cl2, cl2, cl], str(errors)
    b = open('unsup.txt', 'wb')
    b.close()
    errors = [_binary_op_error(b, op) for op in range(13)]
    assert errors == [us + 'read', us + 'read', cl, cl,
                      'ValueError: write to closed file', cl, 'ValueError: truncate of closed file',
                      'ValueError: flush of closed file', 'ValueError: seek of closed file', cl2, cl2, cl2, cl], str(errors)
    os.remove('unsup.txt')


def test_closefd():
    name = os.path.join(testdata, 'closefd_tmp')
    with open(name, 'w') as f:
        f.write('hello\n')
    fd = os.open(name, os.O_RDONLY)
    f = open(fd, closefd=False)
    assert f.read(2) == 'he'
    f.close()
    assert f.closed
    os.lseek(fd, 0, 0)
    assert os.read(fd, 3) == b'hel'  # the fd is still open
    g = open(fd, 'rb', closefd=False)
    os.lseek(fd, 1, 0)
    assert g.read(2) == b'el'
    g.close()
    with open(fd, closefd=False) as h:
        assert h.fileno() == fd
    os.fstat(fd)
    h2 = open(fd, 'rb')  # closefd=True: closes the fd
    h2.close()
    closed = False
    try:
        os.fstat(fd)
    except OSError:
        closed = True
    assert closed
    msg = ''
    try:
        open(name, closefd=False)
    except ValueError as e:
        msg = str(e)
    assert msg == 'Cannot use closefd=False with file name'
    msg = ''
    try:
        open(name, 'rb', closefd=False)
    except ValueError as e:
        msg = str(e)
    assert msg == 'Cannot use closefd=False with file name'
    w = os.open(name, os.O_WRONLY | os.O_APPEND)
    wf = open(w, 'w', closefd=False)
    wf.write('more')
    wf.close()  # (flushed)
    os.write(w, b'!')
    os.close(w)
    with open(name) as f2:
        assert f2.read() == 'hello\nmore!'
    os.remove(name)


def test_read_after_eof_and_seekable():
    # data appended after a read hit the end is seen (no sticky eof)
    name = os.path.join(testdata, 'eof_tmp')
    w = open(name, 'w', newline='')  # (no '\r\n' on windows, for the binary reads)
    w.write('a\n')
    w.flush()
    r = open(name)
    assert r.read() == 'a\n'
    assert r.read() == ''
    w.write('b\n')
    w.flush()
    assert r.read() == 'b\n'
    w.write('c\n')
    w.flush()
    assert r.readline() == 'c\n'
    w.write('d\n')
    w.flush()
    assert [l for l in r] == ['d\n']
    rb = open(name, 'rb')
    assert rb.read() == b'a\nb\nc\nd\n'
    w.write('e\n')
    w.flush()
    assert rb.read() == b'e\n'
    rb.close()
    r.close()
    w.close()

    # truncate(-1) is an error, not truncate()
    f = open(name, 'r+b')
    err = 0
    try:
        f.truncate(-1)
    except OSError as e:
        err = e.errno
    assert err == 22
    f.seek(2)
    assert f.truncate() == 2
    f.close()
    assert os.path.getsize(name) == 2
    g = open(name, 'r+')
    err = 0
    try:
        g.truncate(-1)
    except OSError as e:
        err = e.errno
    assert err == 22
    g.close()
    assert os.path.getsize(name) == 2

    # binary seek checks whence first
    b = open(name, 'rb')
    msg = ''
    try:
        b.seek(0, 5)
    except ValueError as e:
        msg = str(e)
    assert msg == 'whence value 5 unsupported'
    b.close()

    # encoding='locale' (utf-8 mode)
    h = open(name, 'w', encoding='locale')
    h.write('h\xe9')
    h.close()
    hb = open(name, 'rb')
    assert hb.read() == b'h\xc3\xa9'
    hb.close()
    os.remove(name)

    if sys.platform == 'win32':
        return
    # seek/tell on a pipe: UnsupportedOperation (text), as CPython
    rfd, wfd = os.pipe()
    t = os.fdopen(rfd)
    msg = ''
    try:
        t.tell()
    except io.UnsupportedOperation as e:
        msg = str(e)
    assert msg == 'underlying stream is not seekable'
    msg = ''
    try:
        t.seek(0)
    except io.UnsupportedOperation as e:
        msg = str(e)
    assert msg == 'underlying stream is not seekable'
    t.close()
    wb = os.fdopen(wfd, 'wb')
    msg = ''
    try:
        wb.seek(0)
    except io.UnsupportedOperation as e:
        msg = str(e)
    assert msg == 'File or stream is not seekable.'
    wb.close()


def test_closefd_fd_state_line_buffering_sig():
    name = os.path.join(testdata, 'fdstate_tmp')
    w = open(name, 'wb')
    w.write(b'abcdefghij' * 3)
    w.close()
    # closefd=False: close() leaves the fd as it was (non-inheritable,
    # and where reading left it)
    fd = os.open(name, os.O_RDONLY)
    inh = os.get_inheritable(fd)
    f = open(fd, 'rb', closefd=False)
    assert f.read(2) == b'ab'
    f.close()
    assert os.get_inheritable(fd) == inh
    assert os.lseek(fd, 0, 1) == 30  # (read ahead to the end)
    os.close(fd)

    # buffering=1: flush after a '\n' or '\r', everything written so far
    g = open(name, 'w', buffering=1, newline='')  # (no '\r\n' on windows)
    g.write('a\r')
    assert os.path.getsize(name) == 2
    g.write('b\nc')
    assert os.path.getsize(name) == 5
    g.write('d')
    assert os.path.getsize(name) == 5
    g.close()
    assert os.path.getsize(name) == 6

    # utf-8-sig: the position after a bom is 0
    h = open(name, 'w', encoding='utf-8-sig')
    h.write('qr')
    h.close()
    h = open(name, encoding='utf-8-sig')
    assert h.tell() == 0
    assert h.read(1) == 'q'
    assert h.tell() == 4
    h.seek(0)
    assert h.tell() == 0
    h.close()
    h = open(name, 'r+', encoding='utf-8-sig')
    assert h.truncate() == 0
    h.close()
    assert os.path.getsize(name) == 0
    os.remove(name)


def test_read1_bom_only_next_closed():
    name = os.path.join(testdata, 'read1_tmp')
    # utf-8-sig: a file with only a bom is at 3 once read
    b = open(name, 'wb')
    b.write(b'\xef\xbb\xbf')
    b.close()
    g = open(name, encoding='utf-8-sig')
    assert g.tell() == 0
    assert g.read() == ''
    assert g.tell() == 3
    g.close()
    # next() on a closed binary reader
    rb = open(name, 'rb')
    rb.close()
    msg = ''
    try:
        next(rb)
    except ValueError as e:
        msg = str(e)
    assert msg == 'readline of closed file'
    os.remove(name)

    if sys.platform == 'win32':
        return
    # read1()/readinto1() give what a pipe has, without waiting for more
    r, w = os.pipe()
    fr = open(r, 'rb')
    os.write(w, b'hello')
    assert fr.read1(100) == b'hello'
    os.write(w, b'abc')
    ba = bytearray(10)
    assert fr.readinto1(ba) == 3
    assert ba[:3] == bytearray(b'abc')
    os.write(w, b'xyz')
    assert fr.read1() == b'xyz'
    os.close(w)
    assert fr.read1(10) == b''
    fr.close()

    if sys.platform != 'linux':
        return
    # SEEK_DATA/SEEK_HOLE (where the os has them)
    s = open(name, 'wb')
    s.write(b'abcdef')
    s.close()
    s = open(name, 'rb')
    assert s.seek(0, os.SEEK_HOLE) == 6
    assert s.seek(2, os.SEEK_DATA) == 2
    assert s.read() == b'cdef'
    s.close()
    os.remove(name)


def test_all():
    test_readable_writable_seekable()
    test_open_buffering()
    test_utf8_sig()
    test_seek_returns_position()
    test_open_exclusive()
    test_enter_exit_results()
    test_enter_closed()
    test_newline_empty_splits_on_cr()
    test_readline_size_counts_characters()
    test_pending_cr_seek_tell()
    test_text_seek_restrictions()
    test_open_unicode_name()
    test_open_encoding()
    test_open_utf8_sig()
    test_utf8_sig_seek()
    test_append_plus_starts_at_end()
    test_open_bad_args()
    test_open_invalid_mode()
    test_open_unknown_errors()
    test_open_mode_keyword()
    test_open_encoding_attributes()
    test_open_newline()
    test_read_chars_unicode()
    test_read_chars_invalid()
    test_read_chars_truncated()
    test_crlf_ignore()
    test_binary_read_negative()
    test_open_for()
    test_open_read()
    test_open_read2()
    test_open_readlines()
    test_open_readlines_hint()
    test_with_open_read()
    test_with_open_write()
    test_open_write()
    test_open_truncate()
    test_open_enter_exit()
    test_lineendings()
    test_open_directory_raises_oserror()
    test_closed_is_bool()
    test_use_after_close()
    test_buffer_shares_file()
    if sys.platform != 'win32':
        test_std_buffers()
        test_stderr_backslashreplace()
    test_open_mode_order()
    test_binary_mode_normalised()
    test_open_read_write_switch()
    test_with_exit_raises()
    test_unsupported_operation()
    test_binary_readinto_read1()
    test_open_fd()
    test_line_buffering()
    test_closefd()
    test_read_after_eof_and_seekable()
    test_closefd_fd_state_line_buffering_sig()
    test_read1_bom_only_next_closed()

if __name__ == '__main__':
    test_all()
