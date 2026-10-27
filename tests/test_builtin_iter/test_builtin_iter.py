import os

class MyIter:
    def __init__(self, container):
        self.container = container
        self.count = -1

    def next(self):
        self.count += 1
        if self.count < len(self.container):
            return self.container[self.count]
        raise StopIteration


class Container:
    def __init__(self):
        self.unit = list(range(3))

    def __getitem__(self, i):
        return self.unit[i]

    def __iter__(self):
        return MyIter(self)

    def __len__(self):
        return len(self.unit)


def iter_(x):
    return x.__iter__()


b = [1, 2, 3]


def ranged_iter(n):
    for i in range(n):
        yield i


def test_iter1():
    list_it = iter(b)
    assert next(list_it) == 1
    assert next(list_it) == 2
    assert next(list_it) == 3


def test_iter2():
    assert list(iter(b)) == [1, 2, 3]
    assert [y for y in "stroop"] == ['s', 't', 'r', 'o', 'o', 'p']
    assert sorted([n for n in {1: "1", 2: "2", 3: "3"}]) == [1,2,3]
    assert [z for z in [[1], [2], [3]]] == [[1], [2], [3]]
    assert sorted([m for m in set([1.0, 2.0, 3.0])]) == [1.0, 2.0, 3.0]


def test_file_iter():
    if os.path.exists("testdata"):
        testdata = "testdata"
    elif os.path.exists("../testdata"):
        testdata = "../testdata"
    else:
        testdata = "../../testdata"
    datafile = os.path.join(testdata, 'hoppa')
    assert [l for l in open(datafile)] == ['hop\n', 'hop\n', 'hoppa!\n']


def stop_iter(n, mode):
    if mode == 1:
        it = iter(range(n))
    else:
        it = ranged_iter(n)
    try:
        next(it)
        next(it)
        next(it)
        next(it)
    except StopIteration:
        return 'stopped'
    return 'not-stopped'


def test_stop_iter():
    assert stop_iter(3, mode=1) == 'stopped'
    assert stop_iter(3, mode=2) == 'stopped'
    assert stop_iter(4, mode=1) == 'not-stopped'
    assert stop_iter(4, mode=2) == 'not-stopped'


def firsts(its):
    for it in its:
        yield next(it)


def raise_stop():
    yield 1
    raise StopIteration


def caught_stop(its):
    for it in its:
        try:
            x = next(it)
        except StopIteration:
            x = -1
        yield x


def test_stop_iter_pep479():  # StopIteration escaping a generator becomes RuntimeError
    out = []
    try:
        for x in firsts([iter([1]), iter([0][1:]), iter([3])]):
            out.append(x)
        msg = 'no error'
    except RuntimeError as e:
        msg = str(e)
    assert msg == 'generator raised StopIteration'
    assert out == [1]

    try:
        list(raise_stop())
        msg = 'no error'
    except RuntimeError as e:
        msg = str(e)
    assert msg == 'generator raised StopIteration'

    try:
        list(next(iter([0][1:])) for x in range(2))
        msg = 'no error'
    except RuntimeError as e:
        msg = str(e)
    assert msg == 'generator raised StopIteration'

    assert list(caught_stop([iter([1]), iter([0][1:]), iter([3])])) == [1, -1, 3]


def test_class_iter():
    i = iter_(Container())
    try:
        while 1:
            y = i.next()
    except StopIteration:
        pass
    assert y == 2


class BertIter:
    def __init__(self):
        self.x = 4

    def __iter__(self):
        return self

    def __next__(self):
        self.x -= 1
        if self.x == 0:
            raise StopIteration
        return self.x

class Bert:
    def __init__(self):
        pass

    def __iter__(self):
        return BertIter()

class BertBoth:
    def __init__(self):
        self.x = 5

    def __iter__(self):
        return self

    def __next__(self):
        self.x -= 1
        if self.x == 0:
            raise StopIteration
        return self.x


def test_iter_correct():
    assert list(Bert()) == [3, 2, 1]  # separate iterator
    assert list(BertBoth()) == [4, 3, 2, 1]  # iterable is iterator


# __iter__ returning an iterator class that is defined later in the file
class Later:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return LaterIter(self.n)


class LaterSub(Later):
    pass


class LaterIter:
    def __init__(self, n):
        self.n = n
        self.i = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.i >= self.n:
            raise StopIteration
        self.i += 1
        return self.i


def iter_two(x):
    it = iter(x)
    a = next(it)
    return a + next(it)


def test_iter_later_class():
    assert list(Later(3)) == [1, 2, 3]
    assert list(LaterSub(2)) == [1, 2]
    assert [x * 2 for x in Later(2)] == [2, 4]
    assert sum(Later(4)) == 10
    it = iter(Later(3))
    assert next(it) == 1
    assert list(it) == [2, 3]
    assert iter_two(Later(5)) == 3


# iter() on an object whose __iter__ returns self
class SelfIter:
    def __init__(self, n):
        self.n = n
        self.i = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.i >= self.n:
            raise StopIteration
        self.i += 1
        return self.i * 10


def iter_sum(x):
    it = iter(x)
    a = next(it)
    return a + next(it)


def test_iter_self():
    it = iter(SelfIter(3))
    assert next(it) == 10
    assert next(it) == 20
    assert list(it) == [30]
    assert iter_sum(SelfIter(3)) == 30
    b = BertIter()
    assert iter(b) is b
    assert list(iter(b)) == [3, 2, 1]


# an iterator class (__iter__ returning self) with subclasses: the base
# class must still be defined first
class CountIter:
    def __init__(self, n):
        self.n = n
        self.i = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.i >= self.n:
            raise StopIteration
        self.i += 1
        return self.i


class CountIterSub(CountIter):
    pass


class CountIterDouble(CountIter):
    def __next__(self):
        if self.i >= self.n:
            raise StopIteration
        self.i += 1
        return self.i * 2


def test_iter_self_subclass():
    assert list(CountIter(2)) == [1, 2]
    assert list(CountIterSub(3)) == [1, 2, 3]
    assert list(CountIterDouble(2)) == [2, 4]
    assert sum(CountIterDouble(3)) == 12
    assert [x + 1 for x in CountIterSub(2)] == [2, 3]


# regression test: a user-defined class whose name coincides with a
# builtin (Counter, defaultdict, ...) must not be mistaken for the
# actual builtin when its constructor is called, even though the
# builtin has a same-name/same-arity constructor
class Counter:
    def __init__(self, n):
        self.x = n

    def __iter__(self):
        return self

    def __next__(self):
        self.x -= 1
        if self.x == 0:
            raise StopIteration
        return self.x


class defaultdict:
    def __init__(self, a, b):
        self.a = a
        self.b = b


def test_class_name_shadows_builtin():
    assert list(Counter(5)) == [4, 3, 2, 1]
    d = defaultdict(3, 4)
    assert (d.a, d.b) == (3, 4)


def gen_from(xs):
    for x in xs:
        yield x


def gen_done(log):
    yield 1
    log.append('finished')


def gen_return(n):
    yield 1
    if n:
        return
    yield 2


def gen_div(xs):
    for x in xs:
        yield 10 // x


def gen_raise():
    yield 1
    raise KeyError('k')
    yield 2


class GenHolder:
    def __init__(self):
        self.xs = [4, 5]

    def items(self):
        for x in self.xs:
            yield x


def test_exhausted_generator():
    xs = [1, 2]
    g = gen_from(xs)
    assert list(g) == [1, 2]
    xs.append(3)
    assert list(g) == []
    assert sum(g) == 0
    assert sorted(g) == []
    assert not any(g)
    for x in g:
        assert False

    log = []
    d = gen_done(log)
    for v in d:
        pass
    for v in d:
        pass
    assert log == ['finished']

    r = gen_return(1)
    assert list(r) == [1]
    assert list(r) == []

    h = GenHolder()
    m = h.items()
    assert list(m) == [4, 5]
    h.xs.append(6)
    assert list(m) == []

    e = gen_from([7])
    assert next(e) == 7
    for i in range(2):
        try:
            next(e)
            assert False
        except StopIteration:
            pass


def test_generator_after_exception():
    g = gen_div([1, 0, 2, 5])
    out = []
    while True:
        try:
            out.append(next(g))
        except ZeroDivisionError:
            out.append(-1)
        except StopIteration:
            break
    assert out == [10, -1]
    assert list(g) == []

    r = gen_raise()
    assert next(r) == 1
    try:
        next(r)
        assert False
    except KeyError:
        pass
    try:
        next(r)
        assert False
    except StopIteration:
        pass
    assert list(r) == []


# an iterable class whose __iter__ returns iter(list) or yields: its pyiter
# base type must not come from other iter() uses in the program (sum, max..)
class IterLeaf:
    def __init__(self, n):
        self.n = n

class IterNode:
    def __init__(self):
        self.kids = [IterLeaf(1), IterLeaf(2)]
    def __iter__(self):
        return iter(self.kids)

class IterGenStr:
    def __iter__(self):
        yield 'a'
        yield 'b'
    def ints(self):
        yield 1

class IterFloats:
    def __init__(self):
        self.i = 0
    def __next__(self):
        self.i += 1
        if self.i > 3:
            raise StopIteration
        return self.i * 1.5
    def __iter__(self):
        return self

class IterUsesFloats:
    def __iter__(self):
        return IterFloats()

def test_iter_returned_elem_type():
    assert [k.n for k in IterNode()] == [1, 2]
    assert len(list(IterNode())) == 2
    assert sum([1]) == 1 and max([1]) == 1 and sorted([3, 1]) == [1, 3]
    assert list(IterGenStr()) == ['a', 'b']
    assert list(IterGenStr().ints()) == [1]
    assert list(IterUsesFloats()) == [1.5, 3.0, 4.5]


def test_all():
    test_iter1()
    test_iter2()
    test_file_iter()
    test_stop_iter()
    test_stop_iter_pep479()
    test_iter_correct()
    test_iter_later_class()
    test_iter_self()
    test_iter_self_subclass()
    test_class_name_shadows_builtin()
    test_exhausted_generator()
    test_generator_after_exception()
    test_iter_returned_elem_type()


if __name__ == '__main__':
    test_all()

