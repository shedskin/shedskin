"""
import chain: Eggs <- Foo <- Bar <- Spam

"""


from foo import Foo
from boo.quotes import get_quote

from itertools import product

from pak.sub import subsub # contains relative imports



class Eggs:
    def __init__(self):
        self.foo = Foo()

    def name(self):
        return self.foo.name()


def test_imports():
    eggs = Eggs()
    # print(eggs.name())
    assert eggs.name() == "hello"


def test_relative_imports():
    assert subsub.diepst() == [40, 30, 19, 25, 40, 30, 19, 25]


def test_product():
    '''redirected builtin functions (here, to itertools.__product2) and import-from'''

    a = list(product([1, 2], [3, 4]))
    assert a == [(1, 3), (1, 4), (2, 3), (2, 4)]


def test_import_from_nested():
    assert get_quote() == 'quote here'


def test_all():
    test_imports()
    test_relative_imports()
    test_product()
    test_import_from_nested()


if __name__ == "__main__":
    test_all()
