
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
    assert [n for n in {1: "1", 2: "2", 3: "3"}] == [1,2,3]
    assert [z for z in [[1], [2], [3]]] == [[1], [2], [3]]
    assert sorted([m for m in set([1.0, 2.0, 3.0])]) == [1.0, 2.0, 3.0]


def test_file_iter():
    assert [l for l in open("testdata/hoppa")] == ['hop\n', 'hop\n', 'hoppa!\n']

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



def test_all():
    test_iter1()
    test_iter2()
    test_file_iter()
    test_stop_iter()

if __name__ == '__main__':
    test_all()

