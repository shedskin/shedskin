# tests for the inherited extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against inherited.py under CPython, to verify
# the checks themselves.

import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    sys.path.insert(0, os.path.join(HERE, 'build'))

import inherited

if not PURE:
    assert not inherited.__file__.endswith('.py'), inherited.__file__

from inherited import Node, Leaf, Twig, make

# the base class itself
n = Node()
assert n.other is None
n.other = Leaf()
assert type(n.other) is Leaf

# a subclass that never assigns the attribute itself
leaf = Leaf()
assert leaf.other is None and leaf.label == 'node'
leaf.other = Leaf()
assert type(leaf.other) is Leaf
leaf.other = None
assert leaf.other is None
leaf.label = 'x'
assert leaf.label == 'x'

# two levels down
t = Twig()
assert t.other is None and t.depth == 2
t.other = Twig()
assert type(t.other) is Twig
assert make().other.depth == 2

# wrong types are still refused
if not PURE:
    for obj in (leaf, t):
        try:
            obj.other = 3
        except TypeError:
            pass
        else:
            raise AssertionError('accepted an int')

# pickling goes through __reduce__/__setstate__
leaf.other = Leaf()
leaf2 = pickle.loads(pickle.dumps(leaf))
assert type(leaf2.other) is Leaf and leaf2.label == 'x'
t2 = pickle.loads(pickle.dumps(t))
assert type(t2.other) is Twig and t2.depth == 2

print('inherited: all tests passed')
