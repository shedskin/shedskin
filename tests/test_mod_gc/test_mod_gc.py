import gc


def test_gc():
    gc.enable()
    assert gc.isenabled()
    assert gc.collect() >= 0  # shedskin always reports zero
    gc.disable()
    assert not gc.isenabled()
    gc.enable()
    assert gc.isenabled()

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
    test_count()
    test_threshold()

if __name__ == '__main__':
    test_all()
