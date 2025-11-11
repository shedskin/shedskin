# float.as_integer_ratio requires almost arbitrary-size arithmetic

def test_float():
    x = 1.0
    assert x == 1.0

    y = 1.0
    y += 2.0
    assert y > 2.5

    assert float('+1.23') == 1.23
    assert float('-1.23') == -1.23
    assert float(1) == 1.0


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


def test_all():
    test_float()
    test_inf()
    test_is_integer()
    test_from_number()


if __name__ == "__main__":
    test_all()
