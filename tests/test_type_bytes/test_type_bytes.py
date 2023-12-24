# TODO hex(bytes_per_sep), bytes.fromhex

# bytes

def test_capitalize():
    assert b'bla bla'.capitalize() == b'Bla bla'

def test_center():
    assert b'bla'.center(10) == b'   bla    '
    assert b'bla'.center(10, b'-') == b'---bla----'

def test_count():
    assert b'blaa'.count(b'a') == 2
    assert b'blaabla'.count(b'aa') == 1

def test_encode(): pass

def test_endswith():
    assert b'bla'.endswith(b'la')
    assert not b'bla'.endswith(b'xx')

def test_expandtabs():
    assert b'bla\tbla'.expandtabs() == b'bla     bla'

def test_find():
    assert b'bla'.find(b'la') == 1
    assert b'bla'.find(b'ba') == -1

def test_index():
    assert b'bla'.index(b'la') == 1
    assert b'bla'.index(b'bl') == 0

def test_isalnum():
    assert b'bla'.isalnum()
    assert b'123'.isalnum()
    assert b'12a'.isalnum()
    assert not ''.isalnum()

def test_isalpha():
    assert b'bla'.isalpha()
    assert not b'123'.isalpha()
    assert not b''.isalpha()

def test_isascii():
    assert b'bla'.isascii()
    assert not b'\xf0'.isascii()
    assert b''.isascii()

def test_isdigit():
    assert not b'bla'.isdigit()
    assert b'123'.isdigit()
    assert not b''.isdigit()

def test_islower():
    assert not b'BLA'.islower()
    assert b'bla'.islower()
    assert not b''.islower()

def test_isspace():
    assert not b'bla'.isspace()
    assert b'   '.isspace()
    assert not b''.isspace()

def test_istitle():
    assert not b'bla'.istitle()
    assert b'Bla'.istitle()
    assert not b''.istitle()
    assert b"This Is A Title".istitle()
    assert not b"This is not a title".istitle()

def test_isupper():
    assert b'BLA'.isupper()
    assert not b'bla'.isupper()
    assert not b''.isupper()

def test_join():
    assert b'-'.join([b'a', b'b', b'c']) == b"a-b-c"

def test_ljust():
    assert b'bla'.ljust(8) == b'bla     '
    assert b'bla'.ljust(6, b'+') == b'bla+++'

def test_lower():
    assert b'BLA'.lower() == b'bla'

def test_lstrip():
    assert b' bla'.lstrip() == b'bla'

def test_maketrans(): pass

def test_partition():
    assert b"a and b and c".partition(b"and") == (b'a ', b'and', b' b and c')
    assert b'aa-bb-cc'.partition(b'-') ==  (b'aa', b'-', b'bb-cc')

def test_removeprefix(): pass

def test_removesuffix(): pass

def test_replace():
    assert b'bla'.replace(b'la', b'bla') == b'bbla'

def test_rfind():
    assert b'bla'.rfind(b'la') == 1
    assert b'bla'.rfind(b'ba') == -1

def test_rindex():
    assert b'bla'.rindex(b'la') == 1
    assert b'bla'.rindex(b'bl') == 0

def test_rjust():
    assert b'bla'.rjust(8) == b'     bla'
    assert b'bla'.rjust(6, b'-') ==  b'---bla'

def test_rpartition():
    assert b"a and b and c".rpartition(b"and") ==  (b'a and b ', b'and', b' c')
    assert b'aa-bb-cc'.rpartition(b'-')

def test_rsplit():
    assert b'bla'.rsplit(b'l') == [b'b', b'a']
    assert b'b l a'.rsplit() == [b'b', b'l', b'a']
    assert b'haajaaja'.rsplit(b'aa') == [b'h', b'j', b'ja']

def test_rstrip():
    assert b'bla'.rstrip(b'a') == b'bl'

def test_split():
    assert b'bla'.split(b'l') == [b'b', b'a']
    assert b'b l a'.split() == [b'b', b'l', b'a']
    assert b'haajaaja'.split(b'aa') == [b'h', b'j', b'ja']
    assert b"hoei hoei".split() == [b'hoei', b'hoei']
    assert b"hoei hoei\\n".split() == [b'hoei', b'hoei\\n']

def test_splitlines():
    assert b"ab\ncd\r\nef\rghi\n".splitlines() == [b'ab', b'cd', b'ef', b'ghi']
    assert b"ab\ncd\r\nef\rghi\n".splitlines(1) == [b'ab\n', b'cd\r\n', b'ef\r', b'ghi\n']

def test_startswith():
    assert b'bla'.startswith(b'bla')
    assert not b'bla'.startswith(b'xx')

def test_strip():
    assert b'bla  '.strip() == b'bla'
    assert b'**bla**'.strip(b'*') == b'bla'


def test_swapcase():
    assert b'bLa'.swapcase() == b'BlA'

def test_title():
    assert b'bla bla'.title() == b'Bla Bla'

def test_translate(): pass

def test_upper():
    assert b'bla'.upper() == b'BLA'

def test_zfill():
    assert b'bla'.zfill(10) == b'0000000bla'

def heuk(x):
    return    

def test_bytes_cmp():
    assert b"hoei\\n" != b"hoei\n"
    assert b'aap' < b'blup'
    assert b'aap' <= b'blup'
    assert b'bla' != b'blup'
    assert b'bla' == b'bla'
    assert b'bla' != b'blup'
    assert b'bla'*2 == b'blabla'
    assert b'bla'*3 == b'blablabla'
    assert b'bla' + b'bla' == b'blabla'
    assert b'bla' + b'bla' == b'blabla'
    assert b'bla'[1:] == b'la'
    assert b'bla'[1:] == b'la'
    assert b'bla'[1] == ord('l')
    assert b'bla'[::-1] == b'alb'
    assert b'bla'[::-1] == b'alb'
    assert b'blup' >= b'aap'
    assert 2 * b'bla' == b'blabla'
    assert 3 * b'bla' == b'blablabla'
    assert list(b'aap') == [ord('a'), ord('a'), ord('p')]
    assert list(sorted([b'blup', b'aap'])) == [b'aap', b'blup']

def test_bytes_concat():
    assert b"x" + b"x" + b"x" == b"xxx"

def test_bytes_hash():
    bdict = {
        b'bla': 18,
        b'blup': 19,
    }
    assert hash(b'bla')
    assert list(sorted(bdict.items())) == [(b'bla', 18), (b'blup', 19)]
    assert set([b'blup'])


def test_bytes_builtin():
    assert bytes() == b''
    assert bytes([1, 2, 3]) == b'\x01\x02\x03'
    assert bytes(set([1])) == b'\x01'
    assert bytes(0) == b''
    assert bytes(4) == b'\x00\x00\x00\x00'
    assert bytes(7) == b'\x00\x00\x00\x00\x00\x00\x00'
    assert bytes(b"hop") == b'hop'
    assert bytes(bytes(7)) == b'\x00\x00\x00\x00\x00\x00\x00'
    assert bytes(bytearray(7)) == b'\x00\x00\x00\x00\x00\x00\x00'

    assert b"hop %s" % b"hup" == b'hop hup'
    assert int(b"123") == 123


def test_format():
    t = (18, b'waf')
    assert (b'%d hup %s!' % t) == b'18 hup waf!'

    d = {b'aap': 8, b'bert': 9}
    assert (b'hoho %(aap)d, %(bert)d' % d) == b'hoho 8, 9'

    d2 = {b'aap': b'acht', b'bert': b'negen'}
    assert (b'hoho %(aap)s, %(bert)s' % d2) == b'hoho acht, negen'


def test_all():
    test_bytes_cmp()
    test_bytes_concat()
    test_capitalize()
    test_center()
    test_count()
    test_encode()
    test_endswith()
    test_expandtabs()
    test_find()
    test_format()
    test_index()
    test_isalnum()
    test_isalpha()
    test_isascii()
    test_isdigit()
    test_islower()
    test_isspace()
    test_istitle()
    test_isupper()
    test_join()
    test_ljust()
    test_lower()
    test_lstrip()
    test_maketrans()
    test_partition()
    test_removeprefix()
    test_removesuffix()
    test_replace()
    test_rfind()
    test_rindex()
    test_rjust()
    test_rpartition()
    test_rsplit()
    test_rstrip()
    test_split()
    test_splitlines()
    test_startswith()
    test_strip()
    test_swapcase()
    test_title()
    test_translate()
    test_upper()
    test_zfill()
    test_bytes_hash()
    test_bytes_builtin()


if __name__ == "__main__":
    test_all()


