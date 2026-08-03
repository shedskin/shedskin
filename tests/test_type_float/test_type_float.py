# float.as_integer_ratio requires almost arbitrary-size arithmetic

class MyFloat:
    def __init__(self, f):
        self.f = f

    def __float__(self):
        return self.f

class MyFloat2:
    def __init__(self, f):
        self.f = f

    def __index__(self):
        return int(self.f)


def test_float():
    x = 1.0
    assert x == 1.0

    y = 1.0
    y += 2.0
    assert y > 2.5

    assert float('+1.23') == 1.23
    assert float('-1.23') == -1.23
    assert float(1) == 1.0
    assert float(7.8) == 7.8

    assert float(MyFloat(17.7)) == 17.7
    assert float(MyFloat2(17.7)) == 17.0


def test_division():
    assert 9.3 / 3.1 == 3.0
    assert -1.1 / 11 == -0.1

    assert 9 / 3.0 == 3.0
    assert 9 / 3.0 == 3

    assert -1.1 / 11 == -0.1

    assert 7.7 // 7.0 == 1


def test_multiplication():
    assert 2.5 * 4.0 == 10.0
    assert 2.5 * -4.0 == -10.0


def test_inf():
    assert float(" \n iNf") == float('inf')
    float("INF") == float('inf')
    float(" -inf") == float('-inf')
    float("NaN") == float('nan')
    float("-nan") == float('-nan')
    float("infinity") == float('inf')
    float("-infinITY") == float('-inf')


def test_is_integer():
    assert (17.0).is_integer()
    assert not (17.5).is_integer()


def test_from_number():
    assert float.from_number(18) == 18.0
    assert float.from_number(18.87) == 18.87

    assert float.from_number(MyFloat(18.87)) == 18.87
    assert float.from_number(MyFloat2(18.87)) == 18


def test_hex_fromhex():
    s = (17.123).hex()
    assert float.fromhex(s) == 17.123


def test_repr_roundtrip():
    # repr must print the shortest decimal string that reads back as the very
    # same double; a fixed 16 significant digits is neither shortest nor always
    # enough, and dropped the last digit of e.g. 2 ** 0.5
    for x in [0.1, 1 / 3, 2 ** 0.5, 0.1 + 0.2, 1e300, 5e-324, 1e-320,
              1.2345678901234568e+17, -2.5, 100.0, 0.0, -0.0]:
        assert float(repr(x)) == x

    assert repr(2 ** 0.5) == '1.4142135623730951'
    assert repr(0.1) == '0.1'
    assert repr(0.1 + 0.2) == '0.30000000000000004'
    assert repr(1.2345678901234568e+17) == '1.2345678901234568e+17'


def test_repr_formatting():
    # str and repr of a float are the same function, and the switch between
    # fixed and scientific notation happens at these exact points
    assert repr(1e15) == '1000000000000000.0'
    assert repr(1e16) == '1e+16'
    assert repr(0.0001) == '0.0001'
    assert repr(1e-05) == '1e-05'

    assert repr(0.0) == '0.0'
    assert repr(-0.0) == '-0.0'
    assert repr(1.0) == '1.0'
    assert repr(-2.5) == '-2.5'
    assert repr(1e100) == '1e+100'
    assert repr(1e-320) == '1e-320'

    assert str(1.0) == repr(1.0)
    assert str(1e16) == repr(1e16)

    assert repr(float('inf')) == 'inf'
    assert repr(float('-inf')) == '-inf'
    assert repr(float('nan')) == 'nan'


def test_all():
    test_float()
    test_inf()
    test_is_integer()
    test_from_number()
    test_division()
    test_multiplication()
    test_hex_fromhex()
    test_repr_roundtrip()
    test_repr_formatting()


if __name__ == "__main__":
    test_all()
