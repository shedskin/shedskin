
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


def test_all():
    test_basic_fstring()
    test_empty_fstring()
    test_fstring_none()
    test_fstring_str_conversion()
    test_fstring_repr_conversion()
    test_fstring_self_documenting()
    test_fstring_ascii_conversion()


if __name__ == '__main__':
    test_all()
