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

def test_all():
    test_gc()
    test_collect_generation()
    test_debug()
    test_freeze()
    test_is_finalized()
    test_count()
    test_threshold()

if __name__ == '__main__':
    test_all()
