# float.as_integer_ratio requires almost arbitrary-size arithmetic
# so we don't support int.as_integer_ratio either

def test_int():
    assert int("12") == 12
    assert int("ff", 16) == 255
    assert int("20", 8) == 16

    assert int(8.8) == 8
    assert int(7) == 7


def test_division():
    assert 9 /  2 == 4.5
    assert 9 // 2 == 4


def test_is_integer():
    assert (-1).is_integer()
    assert (0).is_integer()
    assert (18).is_integer()


def test_bit_length():  # TODO should work also via int-expr.bit_length..? same for the others
    assert int.bit_length(-123456) == 17
    assert int.bit_length(-8) == 4
    assert int.bit_length(-1) == 1

    assert int.bit_length(0) == 0

    assert int.bit_length(1) == 1
    assert int.bit_length(8) == 4
    assert int.bit_length(123456) == 17


def test_all():
    test_int()
    test_division()
    test_is_integer()
    test_bit_length()


if __name__ == "__main__":
    test_all()

