# string; what about str.*?

import string


def test_string_module():
    assert string.ascii_letters == 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    assert string.ascii_lowercase == 'abcdefghijklmnopqrstuvwxyz'
    assert string.ascii_uppercase == 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    assert string.capwords('ik haat smurven') == 'Ik Haat Smurven'
    assert string.digits == '0123456789'
    assert string.hexdigits == '0123456789abcdefABCDEF'
    assert string.octdigits == '01234567'
    assert string.whitespace == ' \t\n\r\x0b\x0c'

    # locale-dependent
    assert '.' in string.punctuation
    assert 'a' in string.printable


def test_all():
    test_string_module()


if __name__ == '__main__':
    test_all()
