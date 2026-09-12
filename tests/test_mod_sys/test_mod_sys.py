import sys


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
    assert sys.executable

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

def test_float_repr_style():
    assert sys.float_repr_style == 'short'

def test_orig_argv():
    # no interpreter in front of a compiled binary, so the full original
    # command line is exactly argv
    assert sys.orig_argv == sys.argv
    assert sys.orig_argv[0] == sys.executable

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
    test_float_repr_style()
    test_orig_argv()

if __name__ == '__main__':
    test_all()
