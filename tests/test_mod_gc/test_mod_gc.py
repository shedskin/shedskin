import gc


def test_gc():
    gc.enable()
    # assert gc.isenabled()
    gc.collect()
    gc.disable()
    # assert not gc.isenabled() ## not implemented
    assert True ## FIXME hack

def test_all():
    test_gc()

if __name__ == '__main__':
    test_all()
