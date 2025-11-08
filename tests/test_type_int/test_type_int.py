

def test_int():
    assert int("12") == 12
    assert int("ff", 16) == 255
    assert int("20", 8) == 16

def test_division():
    assert 9 /  2 == 4.5
    assert 9 // 2 == 4


def test_is_integer():
    assert (-1).is_integer()
    assert (0).is_integer()
    assert (18).is_integer()


def test_as_integer_ratio():
    assert int.as_integer_ratio(18) == (18, 1)
    assert int.as_integer_ratio(0) == (0, 1)


def test_all():
    test_int()
    test_division()
    test_is_integer()
    test_as_integer_ratio()


if __name__ == "__main__":
    test_all()

