# 219.py
# string; what about str.*?

import string

letters = string.ascii_letters
lowercase = string.ascii_lowercase
uppercase = string.ascii_uppercase
punctuation = string.punctuation
printable = string.printable

## string.ascii_letters changingg to letters_b after compilaton!

letters_a = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
letters_b = 'abcdefghijklmnopqrstuvwxyzªµºßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ'
lowercase_cpp = 'abcdefghijklmnopqrstuvwxyzªµºßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'
uppercase_cpp = 'ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ'
punctuation_cpp = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~¡¢£¤¥¦§¨©«¬\xad®¯°±´¶·¸»¿×÷'
printable_cpp = '0123456789abcdefghijklmnopqrstuvwxyzªµºßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~¡¢£¤¥¦§¨©«¬\xad®¯°±´¶·¸»¿×÷ \t\n\r\x0b\x0c'

def test_string_module():
    assert string.ascii_letters == letters
    assert string.ascii_lowercase == lowercase
    assert string.ascii_uppercase == uppercase
    assert string.capwords('ik haat smurven') == 'Ik Haat Smurven'
    assert string.digits == '0123456789'
    assert string.hexdigits == '0123456789abcdefABCDEF'
    assert string.octdigits == '01234567'
    # assert repr(string.printable) == repr(printable)
    assert string.punctuation == punctuation
    assert repr(string.whitespace) == "' \\t\\n\\r\\x0b\\x0c'"

def test_all():
    test_string_module()

if __name__ == '__main__':
    test_all()
