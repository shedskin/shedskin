# TODO maketrans, translate
# str

def test_capitalize():
    assert 'bla bla'.capitalize() == 'Bla bla'

def test_casefold():
    assert 'BLA'.casefold()

def test_center():
    assert 'bla'.center(10) == '   bla    '
    assert 'bla'.center(10, '-') == '---bla----'

def test_count():
    assert 'blaa'.count('a') == 2
    assert 'blaabla'.count('aa') == 1

    assert "hoooi".count("o") == 3
    assert "hoooi".count("o", 2) == 2
    assert "hoooi".count("o", 0, -2) == 2


# def test_encode():
#     assert 'astring'.encode('utf-8') == b'astring'

def test_endswith():
    assert 'bla'.endswith('la')
    assert not 'bla'.endswith('xx')

def test_expandtabs():
    assert 'bla\tbla'.expandtabs() == 'bla     bla'

def test_find():
    assert 'bla'.find('la') == 1
    assert 'bla'.find('ba') == -1

def test_format(): pass

def test_format_map(): pass

def test_index():
    assert 'bla'.index('la') == 1
    assert 'bla'.index('bl') == 0

def test_isalnum():
    assert 'bla'.isalnum()
    assert '123'.isalnum()
    assert '12a'.isalnum()
    assert not ''.isalnum()

def test_isalpha():
    assert 'bla'.isalpha()
    assert not '123'.isalpha()
    assert not ''.isalpha()

def test_isascii():
    assert 'bla'.isascii()
    assert not '\xf0'.isascii()
    assert ''.isascii()

def test_isdecimal():
    assert not 'bla'.isdecimal()
    assert '123'.isdecimal()
    assert not ''.isdecimal()

def test_isdigit():
    assert not 'bla'.isdigit()
    assert '123'.isdigit()
    assert not ''.isdigit()

def test_isidentifier():
    assert 'Bla_'.isidentifier()
    assert not '9bla'.isidentifier()
    assert not ''.isidentifier()

def test_islower():
    assert not 'BLA'.islower()
    assert 'bla'.islower()
    assert not ''.islower()

def test_isnumeric():
    assert not 'bla'.isnumeric()
    assert '123'.isnumeric()
    assert not ''.isnumeric()

def test_isprintable():
    assert 'bla'.isprintable()
    assert chr(200).isprintable()
    assert ''.isprintable()

def test_isspace():
    assert not 'bla'.isspace()
    assert '   '.isspace()
    assert not ''.isspace()

def test_istitle():
    assert not 'bla'.istitle()
    assert 'Bla'.istitle()
    assert not ''.istitle()
    assert "This Is A Title".istitle()
    assert not "This is not a title".istitle()

def test_isupper():
    assert 'BLA'.isupper()
    assert not 'bla'.isupper()
    assert not ''.isupper()

def test_join():
    assert '-'.join(['a', 'b', 'c']) == "a-b-c"

def test_ljust():
    assert 'bla'.ljust(8) == 'bla     '
    assert 'bla'.ljust(6, '+') == 'bla+++'

def test_lower():
    assert 'BLA'.lower() == 'bla'

def test_lstrip():
    assert ' bla'.lstrip() == 'bla'

def test_maketrans(): pass

def test_partition():
    assert "a and b and c".partition("and") == ('a ', 'and', ' b and c')
    assert 'aa-bb-cc'.partition('-') ==  ('aa', '-', 'bb-cc')

def test_removeprefix(): pass

def test_removesuffix(): pass

def test_replace():
    assert 'bla'.replace('la', 'bla') == 'bbla'
    assert "aaaa".replace("a", "b", 2) == 'bbaa'
    assert "aaaa".replace("a", "b", -1) == 'bbbb'

    assert "1, 3, 5".replace(",", "") == '1 3 5'
    assert "1, 3, 5".replace(",", "", -1) == '1 3 5'
    assert "1, 3, 5".replace(",", "", 0) == '1, 3, 5'
    assert "1, 3, 5".replace(",", "", 1) == '1 3, 5'

def test_rfind():
    assert 'bla'.rfind('la') == 1
    assert 'bla'.rfind('ba') == -1

def test_rindex():
    assert 'bla'.rindex('la') == 1
    assert 'bla'.rindex('bl') == 0

def test_rjust():
    assert 'bla'.rjust(8) == '     bla'
    assert 'bla'.rjust(6, '-') ==  '---bla'

def test_rpartition():
    assert "a and b and c".rpartition("and") == ('a and b ', 'and', ' c')
    assert 'aa-bb-cc'.rpartition('-')

def test_rsplit():
    assert 'bla'.rsplit('l') == ['b', 'a']
    assert 'b l a'.rsplit() == ['b', 'l', 'a']
    assert 'haajaaja'.rsplit('aa') == ['h', 'j', 'ja']

def test_rstrip():
    assert 'bla'.rstrip('a') == 'bl'

def test_split():
    assert 'bla'.split('l') == ['b', 'a']
    assert 'b l a'.split() == ['b', 'l', 'a']
    assert 'haajaaja'.split('aa') == ['h', 'j', 'ja']
    assert "hoei hoei".split() == ['hoei', 'hoei']
    assert "hoei hoei\\n".split() == ['hoei', 'hoei\\n']
    assert "aaaa".split("a", 2) == ['', '', 'aa']
    assert "aaaa".split("a", -1) == ['', '', '', '', '']

def test_splitlines():
    assert "ab\ncd\r\nef\rghi\n".splitlines() == ['ab', 'cd', 'ef', 'ghi']
    assert "ab\ncd\r\nef\rghi\n".splitlines(1) == ['ab\n', 'cd\r\n', 'ef\r', 'ghi\n']

def test_startswith():
    assert 'bla'.startswith('bla')
    assert not 'bla'.startswith('xx')

    assert "hoi".startswith("ho", 0)
    assert "hoi".startswith("ho", 0, 3)
    assert "hoi".startswith("ho", 0, -1)
    assert "hoi".endswith("oi")
    assert "hoi".endswith("oi", 0, 3)
    assert "hoi".endswith("ho", 0, -1)
    assert "hoi".endswith("ho", -3, 2)
    assert not "hoi".startswith(":", 3)
    assert "hoi:".startswith(":", 3)

def test_strip():
    assert 'bla  '.strip() == 'bla'
    assert '**bla**'.strip('*') == 'bla'

def test_swapcase():
    assert 'bLa'.swapcase() == 'BlA'

def test_title():
    assert 'bla bla'.title() == 'Bla Bla'

def test_translate(): pass

def test_upper():
    assert 'bla'.upper() == 'BLA'

def test_zfill():
    assert 'bla'.zfill(10) == '0000000bla'

def heuk(x):
    return    

def test_str_cmp():
    assert "hoei\\n" != "hoei\n"
    assert 'aap' < 'blup'
    assert 'aap' <= 'blup'
    assert 'bla' != 'blup'
    assert 'bla' == 'bla'
    assert 'bla' != 'blup'
    assert 'bla'*2 == 'blabla'
    assert 'bla'*3 == 'blablabla'
    assert 'bla'+'bla' == 'blabla'
    assert 'bla'+'bla' == 'blabla'
    assert 'bla'[1:] == 'la'
    assert 'bla'[1:] == 'la'
    assert 'bla'[1] == 'l'
    assert 'bla'[1] == 'l'
    assert 'bla'[::-1] == 'alb'
    assert 'bla'[::-1] == 'alb'
    assert 'blup' >= 'aap'
    assert 2*'bla' == 'blabla'
    assert 3*'bla' == 'blablabla'
    assert list('aap') == ['a', 'a', 'p']
    assert list(sorted(['blup', 'aap'])) == ['aap', 'blup']


def test_str_concat():
    assert "x" + "x" + "x" == "xxx"


def test_str_overload():
    # locally overloading builtin definition
    str = "4"
    t = ("aha", 2)
    str, x = t
    assert not heuk("aha")


def test_special_characters():
    ss = "\u91cf\u5b50\u529b\u5b66"

    initial = (
        "         \n"
        "         \n"
        " rnbqkbnr\n"
        " pppppppp\n"
        " ........\n"
        " ........\n"
        " ........\n"
        " ........\n"
        " PPPPPPPP\n"
        " RNBQKBNR\n"
        "         \n"
        "         \n"
    )


    uni_pieces = {
        "R": "♜",
        "N": "♞",
        "B": "♝",
        "Q": "♛",
        "K": "♚",
        "P": "♟",
        "r": "♖",
        "n": "♘",
        "b": "♗",
        "q": "♕",
        "k": "♔",
        "p": "♙",
        ".": "·",
    }

    assert initial.strip() == 'rnbqkbnr\n pppppppp\n ........\n ........\n ........\n ........\n PPPPPPPP\n RNBQKBNR'
    assert uni_pieces['k'] == "♔"
    assert ss == '量子力学'

def test_str_id():
    foo_a = "foo"
    foo_b = "foo"
    foo_c = "foo"
    assert id(foo_a) == id(foo_b) == id(foo_c)


def test_all():
    test_str_cmp()
    test_str_concat()
    test_str_overload()
    test_capitalize()
    test_casefold()
    test_center()
    test_count()
    # test_encode()
    test_endswith()
    test_expandtabs()
    test_find()
    test_format()
    test_format_map()
    test_index()
    test_isalnum()
    test_isalpha()
    test_isascii()
    test_isdecimal()
    test_isdigit()
    test_isidentifier()
    test_islower()
    test_isnumeric()
    test_isprintable()
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
    test_special_characters()
    test_str_id()


if __name__ == "__main__":
    test_all()
    
