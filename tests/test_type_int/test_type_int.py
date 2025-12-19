# float.as_integer_ratio requires almost arbitrary-size arithmetic
# so we don't support int.as_integer_ratio either

def test_int():
    assert int("12") == 12
    assert int("ff", 16) == 255
    assert int("20", 8) == 16

    assert int(8.8) == 8
    assert int(7) == 7


def test_multiplication():
    assert 9 * 2 == 18
    assert -9 * 2 == -18


def test_division():
    assert 9 /  2 == 4.5
    assert 8 /  2 == 4.0
    assert 9 // 2 == 4


def test_is_integer():
    assert (-1).is_integer()
    assert (0).is_integer()
    assert (18).is_integer()


def test_bit_length():
    assert (-123456).bit_length() == 17
    assert (-8).bit_length() == 4
    assert (-1).bit_length() == 1

    assert (0).bit_length() == 0

    assert (1).bit_length() == 1
    assert (8).bit_length() == 4
    assert (123456).bit_length() == 17


def test_bit_count():
    assert (15).bit_count() == 4
#    assert (-15).bit_count() == 4  # in shedskin, we assume unsigned, otherwise hard to use for bitmasking..? (othelloN example) # TODO add warning


def test_all():
    test_int()
    test_division()
    test_multiplication()
    test_is_integer()
    test_bit_length()
    test_bit_count()


if __name__ == "__main__":
    test_all()

