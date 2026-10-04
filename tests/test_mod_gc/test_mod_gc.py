import copy
import gc


def test_gc():
    gc.enable()
    assert gc.isenabled()
    assert gc.collect() >= 0  # shedskin always reports zero
    gc.disable()
    assert not gc.isenabled()
    gc.enable()
    assert gc.isenabled()

def test_collect_generation():
    for gen in (0, 1, 2):
        assert gc.collect(gen) >= 0
    assert gc.collect(generation=1) >= 0

def test_debug():
    old = gc.get_debug()
    assert gc.DEBUG_STATS == 1
    assert gc.DEBUG_COLLECTABLE == 2
    assert gc.DEBUG_UNCOLLECTABLE == 4
    assert gc.DEBUG_SAVEALL == 32
    assert gc.DEBUG_LEAK == gc.DEBUG_COLLECTABLE | gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_SAVEALL
    gc.set_debug(gc.DEBUG_STATS | gc.DEBUG_COLLECTABLE)
    assert gc.get_debug() == 3
    gc.set_debug(old)
    assert gc.get_debug() == old

def test_freeze():
    n = gc.get_freeze_count()
    assert n >= 0
    gc.freeze()
    assert gc.get_freeze_count() >= n  # shedskin always reports zero
    gc.unfreeze()
    assert gc.get_freeze_count() == 0

class Foo:
    pass

def test_is_finalized():
    assert not gc.is_finalized(Foo())
    assert not gc.is_finalized([1, 2])
    assert not gc.is_finalized(1)

def test_count():
    count = gc.get_count()
    assert len(count) == 3
    for c in count:
        assert c >= 0

def test_threshold():
    old = gc.get_threshold()
    assert len(old) == 3

    gc.set_threshold(1000, 20, 30)
    assert gc.get_threshold() == (1000, 20, 30)

    gc.set_threshold(1234)  # other thresholds unchanged
    assert gc.get_threshold() == (1234, 20, 30)

    gc.set_threshold(4321, 21)
    assert gc.get_threshold() == (4321, 21, 30)

    gc.set_threshold(old[0], old[1], old[2])
    assert gc.get_threshold() == old

class Scalars:  # only scalars: allocated as pointer-free
    def __init__(self, i, f):
        self.i = i
        self.f = f
        self.b = i % 2 == 0
        self.z = complex(f, i)

class Mixed:  # also contains pointers: must be scanned
    def __init__(self, i):
        self.i = i
        self.s = 'mixed%d' % i
        self.l = [i, i + 1]

class ScalarBase:  # only scalars, but a subclass adds a pointer
    def __init__(self, i):
        self.i = i

class PointerChild(ScalarBase):
    def __init__(self, i):
        ScalarBase.__init__(self, i)
        self.s = 'child%d' % i

def churn():
    total = 0
    for i in range(200000):
        total += len(str(i) + 'x')
    return total

def test_pointer_free_objects():
    scalars = [Scalars(i, i * 0.5) for i in range(1000)]
    mixed = [Mixed(i) for i in range(1000)]
    children = [PointerChild(i) for i in range(1000)]
    copies = [copy.copy(s) for s in scalars[:10]]

    # referenced objects must survive collections
    for rnd in range(3):
        assert churn() > 0
        gc.collect()

    for i in range(1000):
        s = scalars[i]
        assert s.i == i
        assert s.f == i * 0.5
        assert s.b == (i % 2 == 0)
        assert s.z == complex(i * 0.5, i)
        assert mixed[i].s == 'mixed%d' % i
        assert mixed[i].l == [i, i + 1]
        assert children[i].i == i
        assert children[i].s == 'child%d' % i
    for i in range(10):
        assert copies[i].i == i
        assert copies[i].z == complex(i * 0.5, i)


def test_all():
    test_gc()
    test_collect_generation()
    test_debug()
    test_freeze()
    test_is_finalized()
    test_count()
    test_threshold()
    test_pointer_free_objects()

if __name__ == '__main__':
    test_all()
