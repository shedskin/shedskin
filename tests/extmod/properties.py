# extension module under test: compile with 'shedskin build -e properties',
# then run properties_main.py (see README.md)


class K:
    def __init__(self, a):
        self._a = a
        self._b = 1.5

    # a property with a setter
    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, v):
        self._a = v * 10

    # a read-only property
    @property
    def ro(self):
        return 'ro%d' % self._a

    # the old-style form: get_b and set_b stay methods
    def get_b(self):
        return self._b

    def set_b(self, v):
        self._b = v

    b = property(get_b, set_b)


class L(K):
    # inherits 'a' and 'b', and redefines 'ro'
    @property
    def ro(self):
        return 'L%d' % self._a


if __name__ == '__main__':
    # make sure everything is called with the types used from properties_main.py
    k = K(1)
    k.a = 2
    k.a
    k.ro
    k.b = 2.5
    k.b
    k.get_b()
    k.set_b(3.5)
    l = L(3)
    l.a = 4
    l.a
    l.ro
    l.b
