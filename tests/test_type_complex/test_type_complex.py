

def test_complex():
    a = complex(1, 2)
    assert a.imag == 2.0
    assert a.real == 1.0

    c = complex(7.1, 4.7)
    # assert c == (7.1 + 4.7j)
    assert c.real == 7.1
    assert c.imag == 4.7

    d = complex(7)
    assert d.real
    assert d.imag == 0.0
    assert d.real == 7.0

    e = c + d
    assert e.real == 14.1
    assert e.imag == 4.7

    f = 1.2 + complex()
    assert f.real == 1.2
    assert f.imag == 0.0

    g = complex() + 1.3
    assert g.real == 1.3
    assert g.imag == 0.0

    c += complex(7, 1.0)
    assert c.real == 14.1
    assert c.imag == 5.7

    h = complex(7, 4) * complex(9, 5) * complex(7, 4)
    assert h.real == 17.0
    assert h.imag == 669.0

    assert h.conjugate().real == 17.0
    assert h.conjugate().imag == -669.0

    assert "%.8f" % abs(h) == '669.21595916'

    assert hash(h) == 669002024


def test_from_string():
    assert complex(" 2.4+0j") == complex(2.4)
    assert complex("2.4") == complex(2.4)
    assert complex(" .4j") == complex(0, .4)
    assert complex("1-j") == complex(1, -1)
    assert complex("-10-j") == complex(-10, -1)
    assert complex("+10.1+2.4j") == complex(10.1, 2.4)
    assert complex("+j") == complex(0, 1)
    assert complex("-j") == complex(0, -1)
    assert complex("j") == complex(0, 1)
    assert complex("0j") == complex(0, 0)


class PI:
    def __complex__(self):
        return 3+4j

class PI2:
    def __float__(self):
        return 3.14

class PI3:
    def __index__(self):
        return 27


def test_from_class():
    assert complex(PI()) == 3+4j
    assert complex(PI2()) == complex(3.14, 0)
    assert complex(PI3()) == 27+0j


def test_from_number():
    assert complex.from_number(18) == 18+0j
    assert complex.from_number(18.8) == 18.8+0j
    assert complex.from_number(8+9j) == 8+9j

    assert complex.from_number(PI()) == 3+4j

    assert complex.from_number(PI2()) == complex(3.14, 0)
    assert complex.from_number(PI2()) == 3.14

    assert complex.from_number(PI3()) == 27+0j
    assert complex.from_number(PI3()) == 27


def test_all():
    test_complex()
    test_from_string()
    test_from_class()
    test_from_number()


if __name__ == "__main__":
    test_all()

