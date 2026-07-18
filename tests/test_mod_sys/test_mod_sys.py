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

def test_all():
    test_sys()
    test_version_consistency()
    test_recursionlimit()
    test_intern()
    test_is_finalizing()
    test_encodings()
    test_maxunicode()
    test_executable()

if __name__ == '__main__':
    test_all()
