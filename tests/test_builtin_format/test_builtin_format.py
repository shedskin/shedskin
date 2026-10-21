# format() and the __format__ methods of builtin types


class Plain:
    def __str__(self):
        return 'Plain()'


def test_format():
    n = 42
    assert format(n) == '42'
    assert format(n, '') == '42'
    assert format(n, 'x') == '2a'
    assert format(-n, '+08b') == '-0101010'
    assert format(2.5) == '2.5'
    assert format(2.5, '.3f') == '2.500'
    assert format(0.125, '.1%') == '12.5%'
    assert format(True) == 'True'
    assert format(False, 'd') == '0'
    assert format('ab') == 'ab'
    assert format('ab', '4') == 'ab  '
    assert format(None) == 'None'
    assert format([1, 2]) == '[1, 2]'
    assert format(Plain()) == 'Plain()'
    # the spec can be computed at runtime
    spec = '0' + str(6) + '.' + str(2) + 'f'
    assert format(3.14159, spec) == '003.14'
    results = [format(n, spec) for spec in ['d', 'x', 'o', 'X', '5', '#b']]
    assert results == ['42', '2a', '52', '2A', '   42', '0b101010']
    try:
        format(n, '.2' + 'd')
        assert False
    except ValueError as e:
        assert str(e) == 'Precision not allowed in integer format specifier'
    try:
        format(Plain(), 'x')
        assert False
    except TypeError as e:
        assert str(e) == 'unsupported format string passed to Plain.__format__'
    try:
        format(None, 'x')
        assert False
    except TypeError as e:
        assert str(e) == 'unsupported format string passed to NoneType.__format__'


def test_format_methods():
    n = 255
    assert n.__format__('#x') == '0xff'
    assert (-7).__format__('03') == '-07'
    assert (2.5).__format__('08.3f') == '0002.500'
    assert (1.0).__format__('') == '1.0'
    assert True.__format__('') == 'True'
    assert True.__format__('+') == '+1'
    assert 'ab'.__format__('3') == 'ab '
    assert 'abc'.__format__('.1') == 'a'
    # same as format()
    for v in [0, 1, -12345]:
        assert v.__format__('+#o') == format(v, '+#o')
    for f in [0.5, -1e10]:
        assert f.__format__('e') == format(f, 'e')


def test_all():
    test_format()
    test_format_methods()


if __name__ == '__main__':
    test_all()
