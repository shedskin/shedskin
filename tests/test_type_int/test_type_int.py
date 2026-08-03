# float.as_integer_ratio requires almost arbitrary-size arithmetic
# so we don't support int.as_integer_ratio either


class MyInt:
    def __init__(self, val):
        self.val = val

    def __index__(self):
        return self.val


def test_int():
    assert int("12") == 12
    assert int("ff", 16) == 255
    assert int("20", 8) == 16

    assert int(8.8) == 8
    assert int(7) == 7

    assert int(MyInt(19)) == 19

    error = ''
    try:
        int(float('-inf'))
    except OverflowError as e:
        error = str(e)
    assert error == "cannot convert float infinity to integer"

    error = ''
    try:
        int(float('nan'))
    except ValueError as e:
        error = str(e)
    assert error == "cannot convert float NaN to integer"


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

    # a float-based floor(log2(x))+1 rounds the argument on the way in and
    # reports 63 for the first of these, and 64 for the last
    assert (4611686018427387903).bit_length() == 62
    assert (4611686018427387904).bit_length() == 63
    assert (9223372036854775807).bit_length() == 63
    assert (-9223372036854775807 - 1).bit_length() == 64


def test_bit_count():
    assert (15).bit_count() == 4
#    assert (-15).bit_count() == 4  # in shedskin, we assume unsigned, otherwise hard to use for bitmasking..? (othelloN example) # TODO add warning


def test_power():
    assert 2 ** 3 == 8
    assert 2 ** 0 == 1
    assert 10 ** 2 == 100
    assert pow(2, 10) == 1024

    # a negative exponent makes python return a float, so shedskin retypes a
    # negative *literal* exponent to keep the result (and its type) the same;
    # 2 ** 3 must stay an int, so this cannot simply always be a float
    assert 10 ** -1 == 0.1
    assert 2 ** -1 == 0.5
    assert 2 ** -3 == 0.125
    assert pow(10, -1) == 0.1
    assert (2 ** -1) + 0.25 == 0.75

    assert 2.0 ** -1 == 0.5
    assert 2.0 ** 2 == 4.0

    # exponents that are not literals stay int ** int, where shedskin has no
    # value to inspect; it raises rather than returning a wrong int
    e = 3
    assert 2 ** e == 8


def test_str_extremes():
    # the most negative int has no representable negation, so formatting it by
    # negating first used to walk off the front of the digit cache: str()
    # produced "-0" and the bin/hex/oct prefixes came out doubly signed
    assert str(-9223372036854775807 - 1) == '-9223372036854775808'
    assert str(9223372036854775807) == '9223372036854775807'
    assert hex(-9223372036854775807 - 1) == '-0x8000000000000000'
    assert oct(-9223372036854775807 - 1) == '-0o1000000000000000000000'
    assert bin(-9223372036854775807 - 1) == '-0b' + '1' + '0' * 63

    assert str(-1) == '-1'
    assert hex(-255) == '-0xff'
    assert oct(-8) == '-0o10'
    assert bin(-10) == '-0b1010'


def test_to_bytes():
    assert (0).to_bytes() == b'\x00'
    assert (0).to_bytes(signed=True) == b'\x00'

    assert (65).to_bytes() == b'A'

    assert (300).to_bytes(length=2) == b'\x01,'
    assert (300).to_bytes(length=2, byteorder='big') == b'\x01,'
    assert (300).to_bytes(length=2, byteorder='little') == b',\x01'

    error = ''
    try:
        (256*256).to_bytes(length=2)
    except OverflowError as e:
        error = str(e)
    assert error == "int too big to convert"

    assert (-1).to_bytes(signed=True) == b'\xff'
    assert (-128).to_bytes(signed=True) == b'\x80'
    assert (-129).to_bytes(length=2, signed=True) == b'\xff\x7f'

    error = ''
    try:
        (-129).to_bytes(signed=True)
    except OverflowError as e:
        error = str(e)
    assert error == "int too big to convert"

    assert (-255).to_bytes(length=2, signed=True) == b'\xff\x01'
    assert (-256).to_bytes(length=2, signed=True) == b'\xff\x00'
    assert (-257).to_bytes(length=2, signed=True) == b'\xfe\xff'

    assert (0xffffffff).to_bytes(length=4) == b'\xff\xff\xff\xff'
    assert (0xffffffff).to_bytes(length=5) == b'\x00\xff\xff\xff\xff'

    assert (0xabcdabcd).to_bytes(length=4) == b'\xab\xcd\xab\xcd'
    assert (0xabcdabcd).to_bytes(length=5) == b'\x00\xab\xcd\xab\xcd'


def test_from_bytes():
    assert int.from_bytes(b'') == 0
    assert int.from_bytes(b'', signed=True) == 0

    assert int.from_bytes(b'A') == 65

    assert int.from_bytes(b'BCD') == 4342596
    assert int.from_bytes(b'BCD', byteorder='little') == 4473666

    assert int.from_bytes(b'\xff') == 255
    assert int.from_bytes(b'\xff', signed=True) == -1

    assert int.from_bytes(b'\x80', signed=True) == -128
    assert int.from_bytes(b'\xff\x7f', signed=True) == -129

    assert int.from_bytes(b'\xff\x01', signed=True) == -255
    assert int.from_bytes(b'\xff\x00', signed=True) == -256
    assert int.from_bytes(b'\xfe\xff', signed=True) == -257

    assert int.from_bytes(b'\xff\x00') == 0xff00
    assert int.from_bytes(b'\xfe\xff') == 0xfeff

    assert int.from_bytes(b'\xff\xff\xff\xff') == 0xffffffff
    assert int.from_bytes(b'\xff\xff\xff') == 0xffffff

    assert int.from_bytes(b'\xee\xdd\xcc\xbb') == 0xeeddccbb
    assert int.from_bytes(b'\x80\x80\x80') == 0x808080

    # iterable bytes
    assert int.from_bytes([255]) == 255
    assert int.from_bytes([255], signed=True) == -1
    assert int.from_bytes([66, 67, 68]) == 4342596


def test_all():
    test_int()
    test_division()
    test_multiplication()
    test_is_integer()
    test_bit_length()
    test_bit_count()
    test_power()
    test_str_extremes()
    test_to_bytes()
    test_from_bytes()


if __name__ == "__main__":
    test_all()

