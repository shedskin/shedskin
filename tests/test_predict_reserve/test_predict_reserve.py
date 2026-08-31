"""Regression test for the __SS_LIST_RESERVE codegen path used by
--predict.  Built with CMDLINE_OPTIONS --predict (see CMakeLists.txt),
so this exercises the __ss_lcstat-tracking branch of the macro; the
plain build of the rest of the test suite exercises the fixed-size
reserve() branch. Covers both call sites in cpp.py: the fastfor path
(range()) and the general iteration path (iterating a container).
"""


def test_predict_reserve_fastfor():
    assert [i * i for i in range(6)] == [0, 1, 4, 9, 16, 25]


def test_predict_reserve_general_iter():
    xs = [1, 2, 3, 4, 5]
    assert [x * 2 for x in xs if x > 1] == [4, 6, 8, 10]


def squares(n):
    return [i * i for i in range(n)]


def test_predict_reserve_repeated_calls():
    # calling the same comprehension repeatedly exercises the
    # static ListSiteStat persisting across calls at this call site
    assert squares(3) == [0, 1, 4]
    assert squares(3) == [0, 1, 4]
    assert squares(4) == [0, 1, 4, 9]


def test_all():
    test_predict_reserve_fastfor()
    test_predict_reserve_general_iter()
    test_predict_reserve_repeated_calls()


if __name__ == '__main__':
    test_all()
