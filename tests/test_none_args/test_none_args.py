# explicitly passing None for a library argument whose (CPython) default is
# None should behave the same as omitting it (#1490)

import bisect
import collections
import io
import itertools
import random


def test_bisect():
    a = [1, 2, 3, 4, 5]
    assert bisect.bisect(a, 3, hi=None) == 3
    assert bisect.bisect_left(a, 3, 0, None) == 2
    assert bisect.bisect_right(a, 3, 1, None) == 3
    assert bisect.bisect_left(a, 3, lo=1, hi=None) == 2
    bisect.insort(a, 3, hi=None)
    assert a == [1, 2, 3, 3, 4, 5]
    bisect.insort_left(a, 0, 0, None)
    assert a == [0, 1, 2, 3, 3, 4, 5]


def test_str():
    s = 'abcabc'
    assert s.find('c', None, None) == 2
    assert s.find('c', 3, None) == 5
    assert s.rfind('a', None, None) == 3
    assert s.index('b', 2, None) == 4
    assert s.rindex('b', None) == 4
    assert s.count('a', None, None) == 2
    assert s.count('a', 1, None) == 1
    assert s.startswith('a', None, None)
    assert s.endswith('c', None, None)
    assert s.endswith('c', 1, None)
    assert not s.startswith('a', 1, None)


def test_bytes():
    b = b'abcabc'
    assert b.find(b'c', None, None) == 2
    assert b.count(b'a', 1, None) == 1
    assert b.endswith(b'c', 2, None)
    assert b.rfind(b'a', None) == 3


def test_file():
    with open('none_args.txt', 'w') as f:
        f.write('line1\nline2\nline3\n')
    with open('none_args.txt') as f:
        assert f.read(None) == 'line1\nline2\nline3\n'
    with open('none_args.txt', 'r+b') as g:
        g.seek(6)
        g.truncate(None)
    with open('none_args.txt') as f:
        assert f.read() == 'line1\n'


def test_io():
    st = io.StringIO('line1\nline2\n')
    assert st.read(None) == 'line1\nline2\n'
    st.seek(3)
    st.truncate(None)
    assert st.getvalue() == 'lin'
    bt = io.BytesIO(b'abcdef')
    assert bt.read(None) == b'abcdef'


def test_random():
    random.seed(1)
    for i in range(10):
        assert random.randrange(1, None) == 0
        assert random.randrange(5, None) in range(5)


def test_deque():
    d = collections.deque([1, 2, 3], maxlen=None)
    d.append(4)
    assert list(d) == [1, 2, 3, 4]
    e = collections.deque([1, 2, 3], None)
    e.appendleft(0)
    assert list(e) == [0, 1, 2, 3]


def test_round():
    assert round(2.5, None) == 2
    assert str(round(2.567, None)) == '3'
    assert round(2.567, 1) == 2.6


def test_itertools():
    assert [k for k, g in itertools.groupby('aab', None)] == ['a', 'b']
    assert [(k, list(g)) for k, g in itertools.groupby([1, 1, 2], key=None)] == [(1, [1, 1]), (2, [2])]
    assert [k for k, g in itertools.groupby('xxy', lambda c: c == 'x')] == [True, False]


def test_unchanged():
    # None meaning something other than 'omitted' must still work
    assert ' a b '.split(None) == ['a', 'b']
    assert 'a b c'.split(None, 1) == ['a', 'b c']
    assert {'a': 'b'}.pop('c', None) is None
    assert {'a': 'b'}.get('c', None) is None
    dd = collections.defaultdict(str)
    assert dd.pop('c', None) is None
    assert str(None) == 'None'
    assert str(object=None) == 'None'
    assert 'x' + str(None) == 'xNone'


def test_all():
    test_bisect()
    test_str()
    test_bytes()
    test_file()
    test_io()
    test_random()
    test_deque()
    test_round()
    test_itertools()
    test_unchanged()


if __name__ == '__main__':
    test_all()
