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
    except TypeError:
        error = True
    assert error


def test_all():
    test_reduce()


if __name__ == '__main__':
    test_all() 

