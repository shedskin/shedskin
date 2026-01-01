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

#    def __iter__(self):
#        return self

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


def test_all():
    test_iter1()
    test_iter2()
    test_file_iter()
    test_stop_iter()
    test_iter_correct()


if __name__ == '__main__':
    test_all()

