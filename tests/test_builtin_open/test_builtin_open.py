import os


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

     with open(crlf_txt, "w") as f5:
         f5.write("hello world\r\n")
         f5.write("bye\r\n")

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
                error = 'OSError: ' + str(e)
            except ValueError as e:
                error = 'ValueError: ' + str(e)
            if i == 0:
                assert error == "OSError: can't do nonzero end-relative seeks"
            elif i == 1:
                assert error == "OSError: can't do nonzero cur-relative seeks"
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


def test_all():
    test_utf8_sig()
    test_seek_returns_position()
    test_open_exclusive()
    test_enter_exit_results()
    test_newline_empty_splits_on_cr()
    test_readline_size_counts_characters()
    test_pending_cr_seek_tell()
    test_text_seek_restrictions()
    test_open_unicode_name()
    test_open_encoding()
    test_open_utf8_sig()
    test_open_bad_args()
    test_open_invalid_mode()
    test_open_unknown_errors()
    test_open_mode_keyword()
    test_open_encoding_attributes()
    test_open_newline()
    test_read_chars_unicode()
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
    test_open_mode_order()
    test_open_read_write_switch()


if __name__ == '__main__':
    test_all()
