"""
import chain: Eggs <- Foo <- Bar <- Spam

"""


from foo import Foo

from itertools import product

class Eggs:
    def __init__(self):
        self.foo = Foo()

    def name(self):
        return self.foo.name()


def test_imports():
    eggs = Eggs()
    # print(eggs.name())
    assert eggs.name() == "hello"


def test_product():
    '''redirected builtin functions (here, to itertools.__product2) and import-from'''

    a = list(product([1, 2], [3, 4]))
    assert a == [(1, 3), (1, 4), (2, 3), (2, 4)]


def test_all():
    test_imports()
    test_product()


if __name__ == "__main__":
    test_all()
