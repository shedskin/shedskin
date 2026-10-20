
def test_basic_fstring():
    name = 'bert'
    half_age = 24
    s = f'{name} is {half_age*2} years old'
    assert s == 'bert is 48 years old'


def test_empty_fstring():
    s = f''
    assert s == ''
    assert len(s) == 0

    name = 'bert'
    assert f'{name}' + f'' == 'bert'


def test_fstring_none():
    assert f'{None}' == 'None'
    assert f'[{None}]' == '[None]'

    x = None
    assert f'{x}' == 'None'


def test_fstring_str_conversion():
    name = 'bert'
    assert f'{name!s}' == 'bert'
    assert f'{name!s} {name}' == 'bert bert'


def test_fstring_repr_conversion():
    name = 'bert'
    assert f'{name!r}' == "'bert'"
    assert f'{name!r} {name} {name!s}' == "'bert' bert bert"

    assert f'{42!r}' == '42'
    assert f'{1.5!r}' == '1.5'
    assert f'{True!r}' == 'True'
    assert f'{None!r}' == 'None'
    assert f'{[1, 2]!r}' == '[1, 2]'
    assert f'{(1, 2)!r}' == '(1, 2)'
    assert f'{ {1: 2} !r}' == '{1: 2}'
    assert f'{[name]!r}' == "['bert']"

    assert f'{Repred()!r}' == 'Repred()'


def test_fstring_self_documenting():
    # '{x=}' desugars to a '!r' conversion
    name = 'bert'
    age = 48
    assert f'{name=}' == "name='bert'"
    assert f'{age=}' == 'age=48'


def test_fstring_ascii_conversion():
    name = 'caf\u00e9'
    assert f'{name!a}' == "'caf\\xe9'"
    assert f'{"\u20ac"!a}' == "'\\u20ac'"
    assert f'{[name]!a}' == "['caf\\xe9']"
    assert f'{12!a}' == '12'
    assert f'<{None!a}>' == '<None>'
    assert f'{Repred()!a}' == 'Repred()'


class Repred:
    def __repr__(self):
        return 'Repred()'


def test_fstring_format_spec():
    x = 3.14159
    assert f'{x:f}' == '3.141590'
    assert f'{x:.2f}' == '3.14'
    assert f'{x:8.3f}' == '   3.142'
    assert f'{x:08.3f}' == '0003.142'
    assert f'{-x:08.3f}' == '-003.142'
    assert f'{x:+.1f}' == '+3.1'
    assert f'{x: .1f}' == ' 3.1'
    assert f'{-x:-.1f}' == '-3.1'
    assert f'{x:#.0f}' == '3.'
    assert f'{x:.0f}' == '3'
    assert f'{-0.0:.1f}' == '-0.0'
    assert f'{float("inf"):F}' == 'INF'
    assert f'{float("nan"):+08.2f}' == '+0000nan'
    assert f'[{x:.1f}|{x:.3f}]' == '[3.1|3.142]'
    # int and bool accept 'f'
    n = 7
    assert f'{n:.2f}' == '7.00'
    assert f'{-n:06.1f}' == '-007.0'
    assert f'{True:.1f}' == '1.0'
    # the spec applies after a conversion
    try:
        f'{x!r:.2f}'
        assert False
    except ValueError as e:
        assert str(e) == "Unknown format code 'f' for object of type 'str'"
    try:
        f'{[x]:.2f}'
        assert False
    except TypeError as e:
        assert str(e) == 'unsupported format string passed to list.__format__'
    try:
        f'{None:.2f}'
        assert False
    except TypeError as e:
        assert str(e) == 'unsupported format string passed to NoneType.__format__'


def test_fstring_format_spec_int():
    n = 42
    assert f'{n:d}' == '42'
    assert f'{n:5}' == '   42'
    assert f'{-n:05}' == '-0042'
    assert f'{n:+d}|{n: d}|{-n:-d}' == '+42| 42|-42'
    assert f'{0:+}' == '+0'
    assert f'{n:b}|{n:o}|{n:x}|{n:X}' == '101010|52|2a|2A'
    assert f'{n:#b}|{n:#o}|{n:#x}|{n:#X}|{n:#d}' == '0b101010|0o52|0x2a|0X2A|42'
    assert f'{-n:#010b}' == '-0b0101010'
    assert f'{-255:#06X}' == '-0X0FF'
    assert f'{n:+#x}' == '+0x2a'
    assert f'{0:#o}' == '0o0'
    assert f'{n:005}|{n:0}|{n:00}' == '00042|42|42'
    m = -9223372036854775807 - 1
    assert f'{m:x}' == '-8000000000000000'
    assert f'{m:#b}' == '-0b1' + 63 * '0'
    assert f'{65:c}|{65:5c}|{65:05c}' == 'A|    A|0000A'
    # the float presentation types
    assert f'{n:e}|{n:g}|{n:%}' == '4.200000e+01|42|4200.000000%'
    assert f'{n:08.1%}|{n:.1E}' == '04200.0%|4.2E+01'
    # bool: int.__format__, apart from an empty spec
    t = True
    assert f'{t}|{t:}|{t:d}|{t:5}|{t:#x}|{t:.1%}' == 'True|True|1|    1|0x1|100.0%'
    assert f'{False:+}' == '+0'
    # the same renderer as %-formatting
    for v in [0, 7, -7, 255, -256, 123456789]:
        assert f'{v:+08x}' == '%+08x' % v
        assert f'{v:#o}' == '%#o' % v
        assert f'{v: 6d}' == '% 6d' % v
        assert f'{v:#X}' == '%#X' % v
    # errors
    for i in range(3):
        try:
            if i == 0:
                f'{n:.2d}'
            elif i == 1:
                f'{n:05.1x}'
            else:
                f'{n:.0c}'
            assert False
        except ValueError as e:
            assert str(e) == 'Precision not allowed in integer format specifier'
    try:
        f'{n:s}'
        assert False
    except ValueError as e:
        assert str(e) == "Unknown format code 's' for object of type 'int'"
    try:
        f'{t:s}'
        assert False
    except ValueError as e:
        assert str(e) == "Unknown format code 's' for object of type 'bool'"
    try:
        f'{n:.2}'
        assert False
    except ValueError as e:
        assert str(e) == 'Precision not allowed in integer format specifier'
    try:
        f'{n:+c}'
        assert False
    except ValueError as e:
        assert str(e) == "Sign not allowed with integer format specifier 'c'"
    try:
        f'{n:#c}'
        assert False
    except ValueError as e:
        assert str(e) == "Alternate form (#) not allowed with integer format specifier 'c'"
    try:
        f'{-1:c}'
        assert False
    except OverflowError as e:
        assert str(e) == '%c arg not in range(0x110000)'
    try:
        f'{1.5:d}'
        assert False
    except ValueError as e:
        assert str(e) == "Unknown format code 'd' for object of type 'float'"
    try:
        f'{1.5:x}'
        assert False
    except ValueError as e:
        assert str(e) == "Unknown format code 'x' for object of type 'float'"


def test_fstring_format_spec_float():
    x = 3.5
    assert f'{x:}|{x:8}|{-x:08}|{x:+}' == '3.5|     3.5|-00003.5|+3.5'
    assert f'{1e16:}|{1e16:08}|{-0.0:}|{1e-05:}' == '1e+16|0001e+16|-0.0|1e-05'
    inf = float('inf')
    assert f'{inf:08}|{float("nan"):.3}|{-inf:+.3}' == '00000inf|nan|-inf'
    # omitted type with a precision: 'g'-like, at least one decimal
    assert f'{100.0:.3}|{1234.0:.3}|{1.0:.3}|{0.0:.3}' == '1e+02|1.23e+03|1.0|0.0'
    assert f'{9.99:.2}|{99.99:.3}|{12.0:.1}|{0.5:.0}' == '1e+01|1e+02|1e+01|0.5'
    assert f'{0.0001:.3}|{0.00001234:.2}|{123456789.0:.3}' == '0.0001|1.2e-05|1.23e+08'
    assert f'{1.0:.0}|{0.0:.0}|{1e16:.17}' == '1e+00|0e+00|1e+16'
    assert f'{1e16:#}|{5e-05:#}|{1e16:#08}|{1.5e300:#}' == '1.e+16|5.e-05|001.e+16|1.5e+300'
    assert f'{1.0:#}|{1.0:#.3}|{1.0:#.0}|{100.0:#.3}|{1e-05:#.3}' == '1.0|1.00|1.e+00|1.00e+02|1.00e-05'
    # e, E, g, G and %
    assert f'{x:e}|{x:.2E}|{1e-10:g}|{1e20:G}' == '3.500000e+00|3.50E+00|1e-10|1E+20'
    assert f'{0.25:%}|{0.25:.1%}|{0.25:08.1%}|{-0.0:%}' == '25.000000%|25.0%|00025.0%|-0.000000%'
    assert f'{inf:%}|{-inf:+08.1%}' == 'inf%|-000inf%'
    assert f'{1.5:#g}|{x:#.0e}|{99.99:#.2g}|{99.99:#.2G}|{-9.99:#08.2g}' == '1.50000|4.e+00|1.0e+02|1.0E+02|-000010.'
    assert f'{99.99:#.2}|{9.99:#.2}|{0.000099999:#.2}|{0.00099999:#.2}' == '1.0e+02|1.0e+01|0.00010|0.0010'
    for v in [0.5, -2.0, 1e10, 123.456, 1e-7]:
        assert f'{v:+012.3e}' == '%+012.3e' % v
        assert f'{v:#.4g}' == '%#.4g' % v


def test_fstring_format_spec_str():
    s = 'abc'
    assert f'{s:}|{s:s}|{s:5}|{s:5s}|{s:2}' == 'abc|abc|abc  |abc  |abc'
    assert f'{s:.2}|{s:5.2s}|{s:05}|{s:0}|{"":3}' == 'ab|ab   |abc00|abc|   '
    assert f'{s!r:7}' == "'abc'  "
    for i in range(2):
        try:
            if i == 0:
                f'{s:+5}'
            else:
                f'{s:-}'
            assert False
        except ValueError as e:
            assert str(e) == 'Sign not allowed in string format specifier'
    try:
        f'{s: 5}'
        assert False
    except ValueError as e:
        assert str(e) == 'Space not allowed in string format specifier'
    try:
        f'{s:#5}'
        assert False
    except ValueError as e:
        assert str(e) == 'Alternate form (#) not allowed in string format specifier'
    try:
        f'{s:d}'
        assert False
    except ValueError as e:
        assert str(e) == "Unknown format code 'd' for object of type 'str'"


def test_all():
    test_basic_fstring()
    test_empty_fstring()
    test_fstring_none()
    test_fstring_str_conversion()
    test_fstring_repr_conversion()
    test_fstring_self_documenting()
    test_fstring_ascii_conversion()
    test_fstring_format_spec()
    test_fstring_format_spec_int()
    test_fstring_format_spec_float()
    test_fstring_format_spec_str()


if __name__ == '__main__':
    test_all()
