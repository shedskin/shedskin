
# many examples from: https://levelup.gitconnected.com/python-unfolding-the-power-of-fold-bdfbdf14e63

def sum1(xs):
    result = 0
    for x in xs:
        result += x
    return result

def product1(xs):
    result = 1
    for x in xs:
        result *= x
    return result

def concat1(xs):
    result = ""
    for x in xs:
        result += str(x)
    return result

def dictify1(xs):
    result = {}
    for k, v in xs:
        result.update({k: v})
    return result

def reduce(func, seq, initial=0):
    res = func(initial, seq[0])
    for i in range(len(seq)-1):
        res = func(res, seq[i+1])
    return res

def fold(func, iterable, initial):
    result = initial
    for item in iterable:
        result = func(result, item)
    return result

def sum2(xs):
    return fold(lambda acc, item: acc + item, xs, 0)

def product2(xs):
    return fold(lambda acc, item: acc * item, xs, 1)

def concat2(xs):
    return fold(lambda acc, item: acc + str(item), xs, "")

# def dictify2(xs):
#     return fold(lambda acc, item: {**acc, item[0]: item[1]}, xs, {})


xs = [1, 2, 3, 4, 5]

def test_sum():
    assert sum(xs) == 15
    assert sum1(xs) == 15
    assert sum2(xs) == 15

def test_product():
    assert product1(xs) == 120
    assert product2(xs) == 120

def test_concat():
    assert concat1(xs) == '12345'
    # assert concat2(xs) == '12345' ## this doesn't work

def test_reduce():
    add = lambda x,y: x+y
    assert reduce(add, xs) == 15
    assert reduce(add, xs, 5) == 20

# def test_dictify():
#     xs = [("A", 1), ("B", 2), ("C", 3)]
#     assert dictify1(xs) == {'A': 1, 'B': 2, 'C': 3}
#     assert dictify2(xs) == {'A': 1, 'B': 2, 'C': 3}


def test_all():
    test_concat()
    # test_dictify()
    test_product()
    test_reduce()
    test_sum()

if __name__ == '__main__':
    test_all() 
