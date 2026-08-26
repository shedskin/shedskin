"""Local variables/parameters may shadow builtin names; using such a
shadowed name must behave like an ordinary local variable, not trigger
compiler special-casing keyed on the name string alone."""


def test_sum_shadowed():
    sum = 1.0
    for x in [2.0, 3.0, 4.0]:
        sum = sum + x
    assert sum == 10.0


def test_max_shadowed():
    max = 12
    assert max == 12


def test_open_shadowed():
    open = True
    if open:
        assert True
    else:
        assert False


def test_pow_shadowed():
    pow = 2
    z = 3
    y = z ** pow
    assert y == 9


def use_arg_shadows_builtin(len):
    return len + 1


def test_arg_shadows_builtin():
    assert use_arg_shadows_builtin(5) == 6


def test_all():
    test_sum_shadowed()
    test_max_shadowed()
    test_open_shadowed()
    test_pow_shadowed()
    test_arg_shadows_builtin()


if __name__ == "__main__":
    test_all()
