# complex attributes must be typed even when complex() is never called
# (otherwise complex.__init__ is not analyzed), so keep 'complex(' out of here


def test_attributes():
    z = 3 + 4j
    assert z.real == 3.0
    assert z.imag == 4.0
    assert z.conjugate() == 3 - 4j
    assert abs(z.conjugate()) == 5.0


def parts(c):
    return c.real, c.imag


def test_function():
    assert parts(1.5j) == (0.0, 1.5)
    assert parts(2 - 1j) == (2.0, -1.0)


def test_all():
    test_attributes()
    test_function()


if __name__ == "__main__":
    test_all()
