def test_operators():
    a = 5
    b = 10
    assert a > 0 and b < 20
    assert a > 5 or b < 20
    assert not a == b
    assert a != b


def test_logic_all():
    assert not all([1, 1, 0 , 1, 0])
    assert all([True, True])
    assert all("   ")
    assert all("")
    assert not all([0, 1])
    assert all([])
    assert not all(set([0, 1]))
    assert all({})


def test_logic_any():
    assert any([True, False, False])
    assert any("  ")
    assert not any("")
    assert any([1, 2])
    assert not any([])
    assert any(set([1, 2]))


def test_and():
    assert 1 and 1
    assert 1 and 1 and 1 and 1


def test_or():
    assert (0 or 1)
    assert (1 or 0)


def test_not_or():
    true = False
    if ((not 0) or 0):  # mixed bool/int, but works as condition (not assigned to var)
        true = True
    assert true


def test_and_or():
    assert (0 or 0 or 1) and 1


def test_misc():
    ax = [1]
    ax = []
    bx = [2]
    assert (0 or 5 or 4)
    assert not (0 or 0)
    assert 1 > 2 or 3 < 4
    assert ax or bx
    assert [0, 1][(ax or None) is None]
    assert bx or None
    assert None or bx
    assert 1 and 4
    assert 4 and 1
    assert not (bx and [])


def test_all():
    test_operators()
    test_logic_all()
    test_logic_any()
    test_or()
    test_not_or()
    test_and_or()
    test_misc()
    test_and()


if __name__ == '__main__':
    test_all()
