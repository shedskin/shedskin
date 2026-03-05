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


def test_to_bytes():  # TODO signed, overflow
    assert (65).to_bytes() == b'A'

    assert (300).to_bytes(length=2) == b'\x01,'
    assert (300).to_bytes(length=2, byteorder='big') == b'\x01,'
    assert (300).to_bytes(length=2, byteorder='little') == b',\x01'

    error = ''
    try:
        (-1).to_bytes()
    except OverflowError as e:
        error = str(e)
    assert error == "can't convert negative int to unsigned"

    assert (-1).to_bytes(signed=True) == b'\xff'


def test_from_bytes():  # TODO iterable bytes, incorrect nr of args (for builtin!?), signed, overflow
    assert int.from_bytes(b'A') == 65
    assert int.from_bytes(b'BCD') == 4342596
    assert int.from_bytes(b'BCD', byteorder='little') == 4473666

    assert int.from_bytes(b'\xff') == 255
#    assert int.from_bytes(b'\xff', signed=True) == -1


def test_all():
    test_int()
    test_division()
    test_multiplication()
    test_is_integer()
    test_bit_length()
    test_bit_count()
    test_to_bytes()
    test_from_bytes()


if __name__ == "__main__":
    test_all()

