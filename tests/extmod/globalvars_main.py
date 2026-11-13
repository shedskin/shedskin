# tests for the globalvars extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against globalvars.py under CPython, to verify
# the checks themselves.

import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    # globalvars.py sits next to this script, so make sure the compiled module
    # comes first on the path (and check that we actually got it below)
    sys.path.insert(0, os.path.join(HERE, 'build'))

import globalvars

if not PURE:
    assert not globalvars.__file__.endswith('.py'), globalvars.__file__


def raises(exc, func, *args):
    try:
        func(*args)
    except exc:
        return True
    return False


def test_0_initial():  # runs first (sorted)
    assert globalvars.counter == 0
    assert globalvars.name == 'start'
    assert globalvars.items == [1]


def test_changed_by_compiled_code():
    # 0921-B4: these used to keep their values from import time
    n = globalvars.bump()
    assert globalvars.counter == n
    assert globalvars.name == 'bumped %d' % n
    from globalvars import counter
    assert counter == n


def test_changed_from_python():
    globalvars.counter = 10
    assert globalvars.counter == 10
    assert globalvars.get_counter() == 10  # compiled code sees the new value
    globalvars.name = 'set'
    assert globalvars.get_name() == 'set'
    globalvars.items = [4, 5]
    assert globalvars.get_items() == [4, 5]
    globalvars.ratio = 3  # int converts to float, as for attributes
    assert globalvars.half_ratio() == 1.5


def test_errors():
    if not PURE:
        # a global variable has a fixed C++ type, and cannot be deleted
        counter = globalvars.counter
        assert raises(TypeError, setattr, globalvars, 'counter', 'str')
        assert globalvars.counter == counter
        assert raises(AttributeError, delattr, globalvars, 'counter')
    # other module attributes behave as usual
    globalvars.other = 1
    assert globalvars.other == 1
    del globalvars.other
    assert not hasattr(globalvars, 'other')


def test_module():
    assert isinstance(globalvars, types.ModuleType)
    assert globalvars.__name__ == 'globalvars'
    names = dir(globalvars)
    for name in ['counter', 'name', 'items', 'ratio', 'bump']:
        assert name in names, name


def test_star_import():
    # 1113-B9: the globals are not in the module dict, which 'import *' used
    ns = {}
    exec('from globalvars import *', ns)
    for name in ['counter', 'name', 'items', 'ratio', 'bump']:
        assert name in ns, name
    assert ns['counter'] == globalvars.counter
    assert '_private' not in ns
    assert '_private' in dir(globalvars)
    assert '__all__' not in dir(globalvars)


def test_main_only():
    # 1113-B10: the main block does not run on import
    assert not hasattr(globalvars, 'main_only')
    assert 'main_only' not in dir(globalvars)


if __name__ == '__main__':
    tests = [(name, f) for (name, f) in sorted(globals().items()) if name.startswith('test_')]
    for name, f in tests:
        f()
    print('%s: %d tests passed (%s)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod'))
