# extension module under test: compile with 'shedskin build -e threads',
# then run threads_main.py (see README.md)

# threads are not supported: an extension module can only be used from the
# thread that imported it, and raises RuntimeError in any other thread


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def norm2(self):
        return self.x * self.x + self.y * self.y

    def __repr__(self):
        return 'Point(%d, %d)' % (self.x, self.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return self.x * 31 + self.y


def work(n):
    # enough garbage for a collection or two
    total = 0
    for i in range(n):
        total += len(str(i) * 3)
    return total


if __name__ == '__main__':
    p = Point(1, 2)
    print(p.norm2(), repr(p), p + p, p == p, hash(p))
    print(work(1000))
