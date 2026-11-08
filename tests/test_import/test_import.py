"""
import chain: Eggs <- Foo <- Bar <- Spam

"""


from foo import Foo
from boo.quotes import get_quote

from itertools import product

from pak.sub import subsub # contains relative imports
from pak.sub.subsub import deep # plain module with relative imports

from boo import quotes as bq # aliased submodule ('from x import y as z')
from pak import hier as ph
import os.path as op # aliased dotted module ('import x.y as z')

import util_funcs
from util_funcs import shout



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
    assert deep.deepest() == [40, 40, 30, 30, 25, 25, 19]


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


def apply_int(fn, x):
    return fn(x)


def apply_spam(fn, x):
    return fn(x)


func_global = util_funcs.inc
func_from = shout


class FuncHolder:
    def __init__(self, fn):
        self.fn = fn


def test_imported_function_as_value():
    '''function from another module passed around (typedef in header)'''

    assert apply_int(util_funcs.inc, 1) == 2
    assert func_global(41) == 42
    assert func_from('abc') == 'ABC'
    assert FuncHolder(util_funcs.shout).fn('xy') == 'XY'
    assert apply_spam(util_funcs.spam_name, util_funcs.make_spam()) == 'hello!'


def test_all():
    test_imports()
    test_relative_imports()
    test_product()
    test_import_from_nested()
    test_import_submodule_as()
    test_imported_function_as_value()


if __name__ == "__main__":
    test_all()
