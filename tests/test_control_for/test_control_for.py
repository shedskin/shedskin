

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

def test_for_range_near_int_limits():
    # the loop counter used to overflow when stepping past the last value,
    # after which the loop never ended
    M = 9223372036854775807
    result = []
    for i in range(M - 3, M, 2):
        result.append(i)
    assert result == [M - 3, M - 1]
    result = []
    for i in range(-M + 2, -M - 1, -2):
        result.append(i)
    assert result == [-M + 2, -M]
    step = 3
    result = []
    for i in range(M - 5, M, step):
        if i == M - 5:
            continue
        result.append(i)
    assert result == [M - 2]
    assert [i for i in range(M - 3, M, 2)] == [M - 3, M - 1]
    assert list(range(M - 3, M, 2)) == [M - 3, M - 1]


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


def test_for_choice_none():
    # None has no pointer type of its own in C++ (NULL), so it cannot take
    # part in initializer-list deduction either
    result = []
    for s in [None, 'a']:
        result.append(s)
    assert result == [None, 'a']
    names = []
    for x in [ChoiceSub("sub"), None, ChoiceBase("base")]:
        names.append(x.name if x else '-')
    assert names == ["sub", "-", "base"]
    lens = []
    for l in [[1], None, [2, 3]]:
        lens.append(len(l) if l is not None else -1)
    assert lens == [1, -1, 2]


class HeteroBase:
    def name(self):
        return 'base'


class HeteroLeft(HeteroBase):
    def name(self):
        return 'left'


class HeteroRight(HeteroBase):
    def name(self):
        return 'right'


class HeteroMid(HeteroBase):
    def name(self):
        return 'mid'


def hetero_pair():
    return (HeteroLeft(), HeteroRight())


def hetero_gen(tup):
    for t in tup:
        yield t.name()


def test_for_hetero_tuple():
    # a tuple with elements of different classes (with a common base) is a
    # tuple2/tuple3 in C++, which could not be iterated over (E2)
    names = []
    for t in (HeteroLeft(), HeteroRight()):
        names.append(t.name())
    assert names == ['left', 'right']
    pair = (HeteroLeft(), HeteroRight())
    names = []
    for t in pair:
        names.append(t.name())
    for t in pair:
        names.append(t.name())
    assert names == ['left', 'right', 'left', 'right']
    triple = (HeteroLeft(), HeteroMid(), HeteroRight())
    assert [t.name() for t in triple] == ['left', 'mid', 'right']
    assert [t.name() for t in hetero_pair()] == ['left', 'right']
    assert sorted(t.name() for t in triple) == ['left', 'mid', 'right']
    assert list(hetero_gen(pair)) == ['left', 'right']
    assert list(hetero_gen(hetero_pair())) == ['left', 'right']
    found = ''
    for t in triple:
        if t.name() == 'mid':
            found = t.name()
            break
    else:
        found = 'none'
    assert found == 'mid'
    for t in pair:
        pass
    else:
        found = t.name()
    assert found == 'right'
    names = []
    for u in (HeteroLeft(), None):
        names.append(u.name() if u else '-')
    assert names == ['left', '-']


zip_calls: list[int] = []


def zip_arg(n):
    """Logs each call, to check that fast-path arguments are evaluated once."""
    zip_calls.append(n)
    return list(range(n))


def test_for_zip_args_evaluated_once():
    # regression test (#607): the FOR_IN_ZIP fast path used to expand its
    # arguments both in the length computation and in the assignments
    pairs = []
    for a, b in zip(zip_arg(3), zip_arg(4)):
        pairs.append((a, b))
    assert pairs == [(0, 0), (1, 1), (2, 2)]
    assert zip_calls == [3, 4]
    del zip_calls[:]
    assert [a + b for a, b in zip(zip_arg(2), zip_arg(5))] == [0, 2]
    assert zip_calls == [2, 5]
    del zip_calls[:]
    assert sum(a * b for a, b in zip(zip_arg(3), zip_arg(3))) == 5
    assert zip_calls == [3, 3]
    del zip_calls[:]


range_calls: list[str] = []


def range_arg(name, n):
    range_calls.append(name)
    return n


def test_for_range_args_evaluated_once():
    # regression test (#607): a variable range() step used to be re-read on
    # every iteration of the FAST_FOR fast path
    step = 3
    lo, hi = 1, 12
    result = []
    for i in range(lo, hi, step):
        step = 100
        lo = 50
        hi = 2
        result.append(i)
    assert result == [1, 4, 7, 10]
    step = -2
    assert [j for j in range(10, 0, step)] == [10, 8, 6, 4, 2]
    assert list(j for j in range(10, 0, step)) == [10, 8, 6, 4, 2]
    # bounds and step are evaluated once each, from left to right
    result = []
    for i in range(range_arg('lo', 0), range_arg('hi', 5), range_arg('step', 2)):
        result.append(i)
    assert result == [0, 2, 4]
    assert range_calls == ['lo', 'hi', 'step']


class Holder:
    def __init__(self):
        self.idx = 0
        self.name = ''
        self._val = 0
        self.sets = 0

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, v):
        self.sets += 1
        self._val = v


def test_for_subscript_targets():
    # subscript targets cannot be assigned directly by the fast
    # enumerate/zip/dict.items loops (these fall back to the generic loop)
    d = {}
    l = [0, 0]
    seen1 = []

    for i, d["k"] in enumerate(["x", "y"]):
        seen1.append((i, d["k"]))
    assert seen1 == [(0, "x"), (1, "y")]

    seen2 = []
    for l[0], s in enumerate(["x", "y"]):
        seen2.append((l[0], s))
    assert seen2 == [(0, "x"), (1, "y")]
    assert l == [1, 0]

    seen3 = []
    for i, d["k"] in enumerate("ab"):
        seen3.append((i, d["k"]))
    assert seen3 == [(0, "a"), (1, "b")]

    seen4 = []
    for i, d["k"] in zip([1, 2], ["x", "y"]):
        seen4.append((i, d["k"]))
    assert seen4 == [(1, "x"), (2, "y")]

    seen5 = []
    for l[0], l[1] in zip([1, 2], [3, 4]):
        seen5.append(l[:])
    assert seen5 == [[1, 3], [2, 4]]

    seen6 = []
    for i, s, l[0] in zip([1, 2], ["x", "y"], [5, 6]):
        seen6.append((i, s, l[0]))
    assert seen6 == [(1, "x", 5), (2, "y", 6)]

    seen7 = []
    for i, l[1], s in zip([1, 2], [7, 8], ["x", "y"]):
        seen7.append((i, l[1], s))
    assert seen7 == [(1, 7, "x"), (2, 8, "y")]

    seen8 = []
    for l[0], s in {3: "a"}.items():
        seen8.append((l[0], s))
    for i, d["k"] in {4: "b"}.items():
        seen8.append((i, d["k"]))
    assert seen8 == [(3, "a"), (4, "b")]

    # nested
    seen9 = []
    for (i, l[0]), j in zip([(1, 2), (3, 4)], [5, 6]):
        seen9.append((i, l[0], j))
    assert seen9 == [(1, 2, 5), (3, 4, 6)]

    seen10 = []
    for n, (i, l[0]) in enumerate([(1, 2), (3, 4)]):
        seen10.append((n, i, l[0]))
    assert seen10 == [(0, 1, 2), (1, 3, 4)]

    # comprehensions
    assert [(i, d["k"]) for i, d["k"] in enumerate(["x", "y"])] == [(0, "x"), (1, "y")]
    assert [(i, d["k"]) for i, d["k"] in zip([1, 2], ["x", "y"])] == [(1, "x"), (2, "y")]
    assert [(l[0], s) for l[0], s in {3: "a"}.items()] == [(3, "a")]
    assert sum(l[1] for i, l[1] in enumerate([10, 20])) == 30
    assert d["k"] == "y"


def test_for_attribute_targets():
    h = Holder()
    seen11 = []

    for h.idx, h.name in enumerate(["x", "y"]):
        seen11.append((h.idx, h.name))
    assert seen11 == [(0, "x"), (1, "y")]

    seen12 = []
    for h.idx, h.name in zip([1, 2], ["x", "y"]):
        seen12.append((h.idx, h.name))
    assert seen12 == [(1, "x"), (2, "y")]

    seen13 = []
    for h.idx, h.name in {3: "a"}.items():
        seen13.append((h.idx, h.name))
    assert seen13 == [(3, "a")]

    assert [(h.idx, h.name) for h.idx, h.name in enumerate(["u"])] == [(0, "u")]

    # properties: the setter has to be called
    seen14 = []
    for h.val, h.name in enumerate(["x", "y"]):
        seen14.append((h.val, h.name))
    assert seen14 == [(0, "x"), (1, "y")]
    assert h.sets == 2

    seen15 = []
    for h.name, h.val in zip(["x", "y"], [7, 8]):
        seen15.append((h.val, h.name))
    assert seen15 == [(7, "x"), (8, "y")]
    assert h.sets == 4

    seen16 = []
    for h.val, h.name in {5: "a"}.items():
        seen16.append((h.val, h.name))
    assert seen16 == [(5, "a")]
    assert h.sets == 5

    seen17 = []
    for h.val, h.name in [(6, "q")]:
        seen17.append((h.val, h.name))
    assert seen17 == [(6, "q")]
    assert h.sets == 6

    assert [(h.val, h.name) for h.name, h.val in zip(["x", "y"], [8, 9])] == [(8, "x"), (9, "y")]
    assert h.sets == 8


def test_all():
    test_for_range()
    test_for_range_near_int_limits()
    test_for_chain()
    test_for_tuple()
    test_for_fn()
    test_for_enumerate()
    test_for_enumerate_shadowed()
    test_for_zip_shadowed()
    test_for_range_shadowed()
    test_for_zip_args_evaluated_once()
    test_for_range_args_evaluated_once()
    test_for_break()
    test_for_continue()
    test_for_else()
    test_for_choice_mixed_numeric()
    test_for_choice_mixed_subclass()
    test_for_choice_none()
    test_for_hetero_tuple()
    test_for_subscript_targets()
    test_for_attribute_targets()

if __name__ == '__main__':
    test_all() 


