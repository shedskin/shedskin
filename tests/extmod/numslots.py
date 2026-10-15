# extension module under test: compile with 'shedskin build -e numslots',
# then run numslots_main.py (see README.md)


class Mod:
    # a modulo is required: pow(a, n, m) only
    def __init__(self, x):
        self.x = x

    def __pow__(self, n, m):
        return Mod(pow(self.x, n, m))


class Pow:
    # no modulo: a ** n and pow(a, n) only
    def __init__(self, x):
        self.x = x

    def __pow__(self, n):
        return Pow(self.x ** n)


class ModDefault:
    # optional modulo: all three spellings
    def __init__(self, x):
        self.x = x

    def __pow__(self, n, m=1000):
        return ModDefault(pow(self.x, n, m))


if __name__ == '__main__':
    # make sure everything is called with the types used from numslots_main.py
    pow(Mod(3), 4, 5).x
    (Pow(3) ** 4).x
    pow(Pow(3), 4).x
    (ModDefault(3) ** 4).x
    pow(ModDefault(3), 4, 5).x
