# 219.py
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
    assert repr(string.printable) == '\'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\\\'()*+,-./:;<=>?@[\\\\]^_`{|}~ \\t\\n\\r\\x0b\\x0c\''
    assert string.punctuation == '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    assert repr(string.whitespace) == "' \\t\\n\\r\\x0b\\x0c'"

if __name__ == '__main__':
    test_string_module()
