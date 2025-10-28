

def test_int():
    assert int("12") == 12
    assert int("ff", 16) == 255
    assert int("20", 8) == 16

def test_int_division():
    assert 9 /  2 == 4.5
    assert 9 // 2 == 4


def test_int_is_integer():
    assert (-1).is_integer()
    assert (0).is_integer()
    assert (18).is_integer()


def test_all():
    test_int()
    test_int_division()
    test_int_is_integer()


if __name__ == "__main__":
    test_all()

