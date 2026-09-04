"""
import chain: Eggs <- Foo <- Bar <- Spam

"""


from foo import Foo
from boo.quotes import get_quote

from itertools import product

from pak.sub import subsub # contains relative imports

from boo import quotes as bq # aliased submodule ('from x import y as z')
from pak import hier as ph
import os.path as op # aliased dotted module ('import x.y as z')



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


def test_import_submodule_as():
    '''submodule imported under an alias'''

    assert bq.get_quote() == 'quote here'
    assert ph.inhier() == 25
    assert op.splitext('meuk.txt')[1] == '.txt'


def test_all():
    test_imports()
    test_relative_imports()
    test_product()
    test_import_from_nested()
    test_import_submodule_as()


if __name__ == "__main__":
    test_all()
