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


def test_all():
    test_iter1()
    test_iter2()
    test_file_iter()
    test_stop_iter()
    test_iter_correct()
    test_iter_later_class()
    test_iter_self()
    test_iter_self_subclass()
    test_class_name_shadows_builtin()


if __name__ == '__main__':
    test_all()

