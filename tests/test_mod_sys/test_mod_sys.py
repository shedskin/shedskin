import sys
import os


def test_sys():
    assert sys.version
    assert sys.platform
    assert sys.copyright
    assert sys.byteorder in ['little', 'big']
    assert (sys.version_info[0], sys.version_info[1]) >= (2, 4)
    sys.stdout.write(' ')
    sys.stderr.write(' ')

def test_version_consistency():
    # hexversion must decode to the same (major, minor) as version_info
    major = (sys.hexversion >> 24) & 0xff
    minor = (sys.hexversion >> 16) & 0xff
    assert (major, minor) == (sys.version_info[0], sys.version_info[1])

def test_recursionlimit():
    old = sys.getrecursionlimit()
    assert old > 0
    sys.setrecursionlimit(old + 500)
    assert sys.getrecursionlimit() == old + 500
    sys.setrecursionlimit(old)
    assert sys.getrecursionlimit() == old

def test_recursionlimit_invalid():
    # CPython raises ValueError for limit < 1; make sure we match
    # that instead of silently accepting a nonsensical limit
    old = sys.getrecursionlimit()
    for bad in (0, -1, -1000):
        try:
            sys.setrecursionlimit(bad)
            assert False, 'setrecursionlimit(%d) should have raised ValueError' % bad
        except ValueError:
            pass
    assert sys.getrecursionlimit() == old

def test_systemexit_large_code():
    # SystemExit.code should hold the full int, not truncate to 32 bits
    big = 2**31 + 5
    matched = False
    try:
        sys.exit(big)
    except SystemExit as e:
        matched = (e.code == big)
    assert matched

def test_intern():
    s = 'hello world'
    assert sys.intern(s) == s

def test_is_finalizing():
    assert sys.is_finalizing() == False

def test_encodings():
    assert sys.getdefaultencoding() == 'utf-8'
    assert sys.getfilesystemencoding() == 'utf-8'

def test_maxunicode():
    # maxunicode must be an honest upper bound for this implementation's
    # chr()/ord(): chr(maxunicode) must succeed, chr(maxunicode + 1) must not
    assert chr(sys.maxunicode)
    try:
        chr(sys.maxunicode + 1)
        assert False, 'chr() should have raised past maxunicode'
    except ValueError:
        pass

def test_executable():
    # note: 'assert sys.executable' would compile to a pointer check and
    # always pass; test the length explicitly instead
    if sys.argv:  # compiled binary
        assert len(sys.executable) > 0
    else:  # extension module: no C-level argv, executable is empty
        assert len(sys.executable) == 0

def test_float_info():
    # values for IEEE-754 double, which is what the default build uses
    fi = sys.float_info
    assert fi.radix == 2
    assert fi.rounds == 1
    assert fi.mant_dig == 53
    assert fi.dig == 15
    assert fi.max_exp == 1024
    assert fi.min_exp == -1021
    assert fi.max_10_exp == 308
    assert fi.min_10_exp == -307
    assert fi.max > 1e308
    assert 0.0 < fi.min < 1e-307
    # epsilon must be the actual gap at 1.0
    assert 1.0 + fi.epsilon > 1.0
    assert 1.0 + fi.epsilon / 2 == 1.0
    assert repr(fi).startswith('sys.float_info(max=')

def test_implementation():
    assert sys.implementation.name == 'shedskin'
    assert sys.implementation.version[0] == sys.version_info[0]
    assert sys.implementation.version[1] == sys.version_info[1]
    assert sys.implementation.hexversion == sys.hexversion
    assert repr(sys.implementation).startswith("namespace(name='shedskin'")

def test_encode_errors():
    assert sys.getfilesystemencodeerrors() in ('surrogateescape', 'surrogatepass')

def test_surrogateescape_roundtrip():
    # getfilesystemencodeerrors() says 'surrogateescape': a non-utf-8 byte
    # in argv, os.environ or a file name decodes to U+DC80..U+DCFF, and
    # must encode back to the same byte (so open(sys.argv[1]) works)
    if sys.platform == 'darwin':
        # APFS/HFS+ only accept valid utf-8 file names: creating 'a\xff'
        # fails with EILSEQ (errno 92) under CPython too, so the round
        # trip through the filesystem cannot be tested here
        return
    d = 'test_mod_sys_surrogates'
    if not os.path.exists(d):
        os.mkdir(d)
    path = os.path.join(d, 'a\udcff')
    f = open(path, 'w')
    f.write('hi')
    f.close()
    names = os.listdir(d)
    assert names == ['a\udcff']
    assert [ord(c) for c in names[0]] == [97, 0xdcff]
    f = open(os.path.join(d, names[0]))
    assert f.read() == 'hi'
    f.close()
    os.remove(path)
    os.rmdir(d)

def test_surrogateescape_error_message():
    # a surrogate-escaped byte in a file name must survive into the OSError
    # message (and, for an extension module, across the interpreter
    # boundary) rather than being mangled or raising a decode error
    try:
        f = open('test_mod_sys_missing_\udcff')
        f.close()
        assert False, 'open() should have raised'
    except OSError as e:
        assert '\udcff' in str(e)

def test_float_repr_style():
    assert sys.float_repr_style == 'short'

def test_orig_argv():
    # orig_argv always mirrors argv: a compiled binary has no interpreter
    # options in front, and an extension module receives no C-level argv
    # at all (sys is initialized with argc=0), leaving both lists empty
    assert sys.orig_argv == sys.argv
    if sys.argv:  # compiled binary
        assert sys.orig_argv[0] == sys.executable
    else:  # extension module
        assert len(sys.orig_argv) == 0

def test_maxsize():
    # maxsize is the largest value of the native int type: 2**63-1 for
    # the default 64-bit int, 2**31-1 for a 32-bit build
    assert sys.maxsize in (2**31 - 1, 2**63 - 1)
    assert sys.maxsize > 0
    assert sys.maxsize % 2 == 1
    # the corresponding minimum is representable and one bit larger
    # in magnitude
    assert -sys.maxsize - 1 < -sys.maxsize
    assert sys.maxsize.bit_length() in (31, 63)
    assert 'maxsize=%d' % sys.maxsize == 'maxsize=' + str(sys.maxsize)

def test_std_streams():
    # inspect the standard streams without reading from stdin, since
    # the test may run without an attached input
    assert sys.stdin.fileno() == 0
    assert sys.stdout.fileno() == 1
    assert sys.stderr.fileno() == 2
    assert sys.stdin.name == '<stdin>'
    assert sys.stdout.name == '<stdout>'
    assert sys.stderr.name == '<stderr>'
    assert not sys.stdin.closed
    assert not sys.stdout.closed
    assert not sys.stderr.closed
    assert sys.stdin.isatty() in (True, False)
    assert sys.stdin is not sys.stdout
    assert sys.stdout is not sys.stderr

def test_std_streams_originals():
    # __stdin__ and friends hold the streams the program started with
    assert sys.__stdin__ is sys.stdin
    assert sys.__stdout__ is sys.stdout
    assert sys.__stderr__ is sys.stderr
    assert sys.__stdout__.fileno() == 1
    assert sys.__stderr__.name == '<stderr>'

def test_flags():
    fl = sys.flags
    assert fl.debug == 0
    assert fl.inspect == 0
    assert fl.interactive == 0
    assert fl.optimize in (0, 1, 2)
    assert fl.verbose == 0
    assert fl.quiet in (0, 1)
    assert fl.isolated in (0, 1)
    assert fl.hash_randomization in (0, 1)
    assert fl.utf8_mode in (0, 1)
    assert fl.int_max_str_digits >= -1
    assert fl.dev_mode in (True, False)
    assert fl.safe_path in (True, False)
    assert repr(fl).startswith('sys.flags(debug=0, inspect=0, ')

def test_int_info():
    ii = sys.int_info
    assert ii.bits_per_digit > 0
    assert ii.sizeof_digit * 8 >= ii.bits_per_digit
    assert ii.default_max_str_digits >= 0
    assert ii.str_digits_check_threshold == 640
    assert repr(ii).startswith('sys.int_info(bits_per_digit=')

def test_hash_info():
    hi = sys.hash_info
    assert hi.width in (32, 64, 128)
    assert hi.imag == 1000003
    assert hash(float('inf')) == hi.inf
    assert len(hi.algorithm) > 0
    assert hi.hash_bits > 0
    assert hi.seed_bits >= 0
    assert hi.cutoff >= 0
    assert repr(hi).startswith('sys.hash_info(width=')

def test_getsizeof():
    # a container's own buffer is counted..
    small = [1, 2]
    big = [1, 2]
    for i in range(1000):
        big.append(i)
    assert sys.getsizeof(big) > sys.getsizeof(small) + 1000
    assert sys.getsizeof('a' * 1000) > sys.getsizeof('a') + 900
    assert sys.getsizeof(b'a' * 1000) > sys.getsizeof(b'a') + 900
    assert sys.getsizeof(tuple(big)) > sys.getsizeof((1, 2)) + 1000
    d = {1: 2}
    s = {1}
    for i in range(1000):
        d[i] = i
        s.add(i)
    assert sys.getsizeof(d) > sys.getsizeof({1: 2}) + 1000
    assert sys.getsizeof(s) > sys.getsizeof({1}) + 1000
    # ..but not the objects it refers to
    assert sys.getsizeof(['a']) == sys.getsizeof(['a' * 1000])
    assert sys.getsizeof({1: 'a'}) == sys.getsizeof({1: 'a' * 1000})
    # other objects
    assert sys.getsizeof(1) > 0
    assert sys.getsizeof(1.0) > 0
    assert sys.getsizeof(1, -1) == sys.getsizeof(1)
    assert sys.getsizeof(small, -1) == sys.getsizeof(small)

def test_all():
    test_sys()
    test_version_consistency()
    test_recursionlimit()
    test_recursionlimit_invalid()
    test_systemexit_large_code()
    test_intern()
    test_is_finalizing()
    test_encodings()
    test_maxunicode()
    test_executable()
    test_float_info()
    test_implementation()
    test_encode_errors()
    test_surrogateescape_roundtrip()
    test_surrogateescape_error_message()
    test_float_repr_style()
    test_orig_argv()
    test_maxsize()
    test_std_streams()
    test_std_streams_originals()
    test_flags()
    test_int_info()
    test_hash_info()
    test_getsizeof()

if __name__ == '__main__':
    test_all()
