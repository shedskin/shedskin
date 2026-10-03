# extension module under test: compile with 'shedskin build -e richcmp',
# then run richcmp_main.py (see README.md)


class Full:
    # all six comparison methods
    def __init__(self, x):
        self.x = x

    def __eq__(self, other):
        return self.x == other.x

    def __ne__(self, other):
        return self.x != other.x

    def __lt__(self, other):
        return self.x < other.x

    def __le__(self, other):
        return self.x <= other.x

    def __gt__(self, other):
        return self.x > other.x

    def __ge__(self, other):
        return self.x >= other.x


class EqOnly:
    # '!=' falls back to the inverse of __eq__; the class is unhashable
    def __init__(self, x):
        self.x = x

    def __eq__(self, other):
        return self.x == other.x


class LtOnly:
    # 'a > b' falls back to the reflected 'b < a'
    def __init__(self, x):
        self.x = x

    def __lt__(self, other):
        return self.x < other.x


class EqHash:
    # __eq__ with __hash__: usable in sets and as dict keys
    def __init__(self, x):
        self.x = x

    def __eq__(self, other):
        return self.x % 10 == other.x % 10

    def __hash__(self):
        return self.x % 10


class Derived(EqHash):
    # only adds __lt__: keeps __eq__ and __hash__ of EqHash
    def __lt__(self, other):
        return self.x < other.x


if __name__ == '__main__':
    # make sure everything is called with the types used from richcmp_main.py
    a, b = Full(1), Full(2)
    a == b
    a != b
    a < b
    a <= b
    a > b
    a >= b
    EqOnly(1) == EqOnly(2)
    LtOnly(1) < LtOnly(2)
    EqHash(1) == EqHash(11)
    hash(EqHash(1))
    Derived(1) < Derived(2)
    Derived(1) == Derived(11)
