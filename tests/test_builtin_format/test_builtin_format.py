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


def test_format_complex():
    c = 1+2j
    assert format(c) == '(1+2j)'
    assert format(c, '10') == '    (1+2j)'
    assert format(c, '<10') == '(1+2j)    '
    assert format(c, '.2f') == '1.00+2.00j'
    assert format(c, '+.1e') == '+1.0e+00+2.0e+00j'
    assert format(c, ' ') == '( 1+2j)'
    assert format(c, '#') == '(1.+2.j)'
    assert format(c, '.3') == '(1+2j)'
    assert format(c, '*^14.2f') == '**1.00+2.00j**'
    assert format(2j, '') == '2j'
    assert format(-2j, '8') == ' (-0-2j)'
    assert format(2j, '+') == '+2j'
    assert format(complex(-0.0, 1), 'z') == '(0+1j)'
    assert format(complex(0.0, -0.0), 'z') == '0j'
    assert format(12345.5-1e20j, ',') == '(12,345.5-1e+20j)'
    assert format(12345.5+1j, '_.1f') == '12_345.5+1.0j'
    assert format(1.23456789+9.87654321j, 'g') == '1.23457+9.87654j'
    assert format(complex(float('nan'), float('-inf')), 'F') == 'NAN-INFj'
    assert f'{(1+2j):.2f}' == '1.00+2.00j'
    assert '{:>12}'.format(1+2j) == '      (1+2j)'
    assert (1+2j).__format__('.1f') == '1.0+2.0j'
    for spec, msg in [('010', 'Zero padding is not allowed in complex format specifier'),
                      ('0>12', 'Zero padding is not allowed in complex format specifier'),
                      ('=12', "'=' alignment flag is not allowed in complex format specifier"),
                      ('%', "Unknown format code '%' for object of type 'complex'"),
                      ('d', "Unknown format code 'd' for object of type 'complex'")]:
        try:
            format(c, spec)
            assert False
        except ValueError as e:
            assert str(e) == msg


def test_format_huge():
    x = 1.5
    for spec, msg in [('99999999999999999999', 'Too many decimal digits in format string'),
                      ('9223372036854775808', 'Too many decimal digits in format string'),
                      ('.99999999999999999999f', 'Too many decimal digits in format string'),
                      ('.18446744073709551617f', 'Too many decimal digits in format string'),
                      ('.3000000000f', 'precision too big'),
                      ('.2147483647g', 'precision too big'),
                      ('.2147482624', 'precision too big')]:
        try:
            format(x, spec)
            assert False
        except ValueError as e:
            assert str(e) == msg
    try:
        f'{x:99999999999999999999}'
        assert False
    except ValueError as e:
        assert str(e) == 'Too many decimal digits in format string'
    try:
        format(1, '.3000000000f')
        assert False
    except ValueError as e:
        assert str(e) == 'precision too big'
    try:
        format(1+2j, '.3000000000f')
        assert False
    except ValueError as e:
        assert str(e) == 'precision too big'
    try:
        format('abc', '.99999999999999999999')
        assert False
    except ValueError as e:
        assert str(e) == 'Too many decimal digits in format string'
    assert format('abc', '.9223372036854775807') == 'abc'
    # large but valid precisions (a stream would use the stack)
    assert len(format(x, '.10000000f')) == 10000002
    assert len(format(x, '#.10000000g')) == 10000001
    assert len('%.10000000e' % x) == 10000006
    for fmt, msg in [('%99999999999999999999d', 'width too big'),
                     ('%.99999999999999999999f', 'precision too big'),
                     ('%.3000000000f', 'precision too big'),
                     ('%.2147482624f', 'precision too big')]:
        try:
            fmt % x
            assert False
        except ValueError as e:
            assert str(e) == msg


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
    test_format_complex()
    test_format_huge()
    test_format_methods()


if __name__ == '__main__':
    test_all()
