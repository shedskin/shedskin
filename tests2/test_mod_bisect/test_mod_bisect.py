import bisect



def test_bisect():
    xs = [1, 2, 3, 4, 5, 6, 6, 7]
    n = 4
    assert bisect.bisect_left(xs, n) == 3
    assert bisect.bisect_left(xs, n, 0) == 3
    assert bisect.bisect_left(xs, n, 0, len(xs)) == 3
    assert bisect.bisect_right(xs, n) == 4
    assert bisect.bisect(xs, n) == 4

    bisect.insort_left(xs, n)
    assert xs == [1, 2, 3, 4, 4, 5, 6, 6, 7]

    bisect.insort_right(xs, n)
    assert xs == [1, 2, 3, 4, 4, 4, 5, 6, 6, 7]

    bisect.insort(xs, n)
    assert xs == [1, 2, 3, 4, 4, 4, 4, 5, 6, 6, 7]



class Pair:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def val(self):
        return (self.x, self.y)

    def __repr__(self):
        return "Pair(%s, %s)" % (self.x, self.y)

    def __lt__(self, other):
        return self.x + self.y < other.x + other.y

    def __eq__(self, other):
        return self.x + self.y == other.x + other.y



def test_bisect_insort():
    pairs = [[18, 6], [28, 5], [35, 26], [31, 28], [3, 3], [32, 37], [11, 17], [28, 29]]
    items = []
    for pair in pairs:
        bisect.insort(items, Pair(pair[0], pair[1]))

    assert items[0].val == (3,3)
    assert items[-1].val == (32, 37)
    assert [i.val for i in items] == [(3, 3), (18, 6), (11, 17), (28, 5), (28, 29), (31, 28), (35, 26), (32, 37)]
    


def test_all():
    test_bisect()
    test_bisect_insort()
    

if __name__ == '__main__':
    test_all() 