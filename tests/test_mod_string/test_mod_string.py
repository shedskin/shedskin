# string; what about str.*?

import string


def test_string_module():
    assert string.ascii_letters == 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    assert string.ascii_lowercase == 'abcdefghijklmnopqrstuvwxyz'
    assert string.ascii_uppercase == 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    assert string.capwords('ik haat smurven') == 'Ik Haat Smurven'
    assert string.capwords('a,b,,c', sep=',') == 'A,B,,C'
    assert string.capwords('  hello   wORLD  ') == 'Hello World'
    assert string.capwords('a\tb\nc') == 'A B C'
    assert string.capwords('a b', sep=None) == 'A B'
    assert string.capwords('aXb--cDe--', '--') == 'Axb--Cde--'
    assert string.capwords('') == ''
    assert string.capwords('', ',') == ''
    assert string.capwords('\xe9lan VITAL \xc9\xc9') == '\xc9lan Vital \xc9\xe9'
    try:
        string.capwords('anything', sep='')
        assert False, 'expected ValueError'
    except ValueError:
        pass
    assert string.digits == '0123456789'
    assert string.hexdigits == '0123456789abcdefABCDEF'
    assert string.octdigits == '01234567'
    assert string.whitespace == ' \t\n\r\x0b\x0c'

    # fixed ascii constants, whatever the locale is (see Lib/string.py)
    assert string.punctuation == '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    assert len(string.punctuation) == 32
    assert string.printable == (string.digits + string.ascii_lowercase +
                                string.ascii_uppercase + string.punctuation +
                                string.whitespace)
    assert len(string.printable) == 100
    for c in string.printable:
        assert ord(c) < 128


def test_all():
    test_string_module()


if __name__ == '__main__':
    test_all()
