

xs = range(10)

seq = [(1,2), (3,4)]

cube = [(1,2),(3,4),(5,6)]

def hoei(cube):
    x = None
    for pos in cube:
        x = pos
    return x


def test_for_range():
    result = []
    for i in xs:
        result.append(i)
    assert result == [0,1,2,3,4,5,6,7,8,9]

def test_for_chain():
    assert [x + y for x in range(2) for y in range(3)] == [0, 1, 2, 1, 2, 3]
    assert list(x + y for x in range(3) for y in range(4)) == [0, 1, 2, 3, 1, 2, 3, 4, 2, 3, 4, 5] 
    assert [x+y+z  for x in range(2) for y in range(2) for z in range(2)] == [0, 1, 1, 2, 1, 2, 2, 3]

def test_for_tuple():
    result = []
    for i in seq:
        result.append(i)
    assert result == seq

def test_for_fn():
    assert hoei(cube) == (5,6)

def test_for_enumerate():
    result_i = []
    result_o = []
    for i, o in enumerate(cube):
        result_i.append(i)
        result_o.append(o)
    assert result_i == [0,1,2]
    assert result_o == cube

def fake_enumerate(items):
    """Not the builtin 'enumerate': pairs each item with itself."""
    result = []
    for x in items:
        result.append((x, x))
    return result


def call_with_shadowed_enumerate(items, enumerate):
    """'enumerate' is a parameter here, shadowing the builtin locally, so
    calling it must call whatever was passed in, not the real builtin."""
    result = []
    for a, b in enumerate(items):
        result.append((a, b))
    return result


def test_for_enumerate_shadowed():
    # regression test: a local 'enumerate' (parameter, in this case) must
    # not be treated as the builtin
    assert call_with_shadowed_enumerate(['x', 'y', 'z'], fake_enumerate) == [
        ('x', 'x'),
        ('y', 'y'),
        ('z', 'z'),
    ]


def fake_zip(a, b):
    """Not the builtin 'zip': pairs each element of 'a' with itself."""
    result = []
    for x in a:
        result.append((x, x))
    return result


def call_with_shadowed_zip(a, b, zip):
    """'zip' is a parameter here, shadowing the builtin locally."""
    result = []
    for x, y in zip(a, b):
        result.append((x, y))
    return result


def test_for_zip_shadowed():
    # regression test: a local 'zip' (parameter) must not be treated as
    # the builtin
    assert call_with_shadowed_zip([1, 2, 3], ['a', 'b', 'c'], fake_zip) == [
        (1, 1),
        (2, 2),
        (3, 3),
    ]


def fake_range(n):
    """Not the builtin 'range': counts down from n-1 to 0 instead of up."""
    result = []
    i = n - 1
    while i >= 0:
        result.append(i)
        i -= 1
    return result


def call_with_shadowed_range(n, range):
    """'range' is a parameter here, shadowing the builtin locally."""
    result = []
    for i in range(n):
        result.append(i)
    return result


def test_for_range_shadowed():
    # regression test: a local 'range' (parameter) must not be treated as
    # the builtin
    assert call_with_shadowed_range(5, fake_range) == [4, 3, 2, 1, 0]


def test_for_break():
    xs = range(10)
    x = 0
    for i in xs:
        if i > 5:
            x = i
            break
    assert x == 6

def test_for_continue():
    xs = []
    for i in range(10):
        if i == 5:
            continue
        xs.append(i)
    assert xs == [0, 1, 2, 3, 4, 6, 7, 8, 9]


def test_for_else():
    xs = []
    for i in range(6):
        xs.append(1)
    else:
        xs.append(2)
    assert xs == [1, 1, 1, 1, 1, 1, 2]



def test_for_choice_mixed_numeric():
    # inline list literal for-loops ('fast choice iter') used to fail to
    # compile when the elements had different concrete types, since the
    # generated C++ relied on 'auto' initializer-list deduction
    total = 0.0
    for x in [1, 2.5, 3]:
        total += x
    assert total == 6.5


class ChoiceBase:
    def __init__(self, name):
        self.name = name


class ChoiceSub(ChoiceBase):
    pass


def test_for_choice_mixed_subclass():
    base = ChoiceBase("base")
    sub = ChoiceSub("sub")
    names = []
    for x in [base, sub]:
        names.append(x.name)
    assert names == ["base", "sub"]


def test_all():
    test_for_range()
    test_for_chain()
    test_for_tuple()
    test_for_fn()
    test_for_enumerate()
    test_for_enumerate_shadowed()
    test_for_zip_shadowed()
    test_for_range_shadowed()
    test_for_break()
    test_for_continue()
    test_for_else()
    test_for_choice_mixed_numeric()
    test_for_choice_mixed_subclass()

if __name__ == '__main__':
    test_all() 


