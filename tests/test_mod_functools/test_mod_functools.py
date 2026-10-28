import sys
from functools import reduce


def test_reduce():
    assert reduce(lambda a,b: a+b, [1,2,3]) == 6
    assert reduce(lambda a,b: a+b, iter((2,3))) == 5

    assert reduce(lambda a,b: a+b, [1,2,3], 7) == 13
    assert reduce(lambda a,b: a+b, iter((2,3)), 7) == 12

    assert reduce(lambda a,b: a+b, [[3,4],[5,6]]) == [3,4,5,6]
    assert reduce(lambda a,b: a+b, [[3,4],[5,6]], [1, 2]) == [1,2,3,4,5,6]

    a = [1]
    a = []
    assert reduce(lambda a,b: a+b, a, 7) == 7

    error = False
    try:
        reduce(lambda a,b: a+b, a)
    except TypeError as e:
        error = True
        assert str(e) == "reduce() of empty iterable with no initial value"
    assert error


def add(a, b):
    return a + b


def test_reduce_mixed():
    # initial of a different type than the elements/accumulator (issue 1014)
    assert reduce(lambda a, b: a if a else b, ["", "x"], None) == "x"
    assert reduce(lambda a, b: a if a else b, ["", ""], None) == ""
    assert reduce(lambda a, b: a + b, [1, 2], 0.5) == 3.5
    assert reduce(add, [1, 2], 0.5) == 3.5

    # accumulator and element types differ
    assert reduce(lambda acc, x: acc + [x], [1, 2, 3], [0]) == [0, 1, 2, 3]
    assert reduce(lambda acc, x: acc + len(x), ["ab", "cde"], 0) == 5
    assert reduce(lambda acc, k: acc + k, {"a": 1, "b": 2}, "") == "ab"

    if (sys.version_info[0], sys.version_info[1]) >= (3, 14):
        assert reduce(lambda a, b: a + b, [1, 2], initial=0.5) == 3.5
        assert reduce(add, [1, 2], initial=0.5) == 3.5


def test_all():
    test_reduce()
    test_reduce_mixed()


if __name__ == '__main__':
    test_all() 

