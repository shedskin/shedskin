import sys


def test_sys():
    assert sys.version
    assert sys.platform
    assert sys.copyright
    assert sys.byteorder in ['little', 'big']
    assert (sys.version_info[0], sys.version_info[1]) >= (2, 4)
    sys.stdout.write(' ')
    sys.stderr.write(' ')

def test_all():
    test_sys()

if __name__ == '__main__':
    test_all()
