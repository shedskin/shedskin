# extension module under test: compile with 'shedskin build -e typeslots',
# then run typeslots_main.py (see README.md)


def square(n):
    return n * n


class Applier:
    # __call__ takes a function, so it cannot be exported (translate warns
    # about this): no tp_call slot should be generated for it
    def __init__(self, x):
        self.x = x

    def __call__(self, f):
        return f(self.x)

    def __repr__(self):
        return 'Applier(%d)' % self.x

    def __str__(self):
        return 'applier %d' % self.x

    def value(self):
        return self.x


class Scaler:
    # an exportable __call__
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, n):
        return n * self.factor


if __name__ == '__main__':
    # make sure everything is called with the types used from typeslots_main.py
    a = Applier(3)
    a(square)
    repr(a)
    str(a)
    a.value()
    Scaler(2)(5)
