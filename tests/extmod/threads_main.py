# tests for the threads extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against threads.py under CPython, to verify
# the checks themselves (where every call simply works, in any thread).

import os
import pickle
import subprocess
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    sys.path.insert(0, os.path.join(HERE, 'build'))

import threads

if not PURE:
    assert not threads.__file__.endswith('.py'), threads.__file__

N = 200000
MSG = 'can only be used from the thread that imported it'


def in_thread(f):
    """run f() in another thread, return its result or the exception"""
    result = []

    def run():
        try:
            result.append(f())
        except BaseException as e:
            result.append(e)

    t = threading.Thread(target=run)
    t.start()
    t.join()
    return result[0]


def check_other_thread(f, expected):
    r = in_thread(f)
    if PURE:
        assert r == expected, r
    else:
        assert isinstance(r, RuntimeError) and MSG in str(r), repr(r)


def test_importing_thread():
    p = threads.Point(3, 4)
    assert p.norm2() == 25
    assert repr(p) == 'Point(3, 4)'
    assert threads.work(N) == sum(len(str(i) * 3) for i in range(N))


def test_other_thread():
    p = threads.Point(3, 4)
    q = threads.Point(3, 4)

    def set_x():
        q.x = 5
        return q.x

    check_other_thread(lambda: threads.work(N), sum(len(str(i) * 3) for i in range(N)))
    check_other_thread(lambda: threads.work(10), 30)  # no collection needed
    check_other_thread(lambda: threads.Point(1, 2).x, 1)  # tp_new
    check_other_thread(lambda: p.norm2(), 25)  # method
    check_other_thread(lambda: p.y, 4)  # getter
    check_other_thread(lambda: repr(p), 'Point(3, 4)')  # tp_repr
    check_other_thread(lambda: (p + p).x, 6)  # nb_add
    check_other_thread(lambda: p == p, True)  # tp_richcompare
    check_other_thread(lambda: hash(p), 97)  # tp_hash
    check_other_thread(lambda: pickle.dumps(p) and 1, 1)  # __reduce__
    check_other_thread(set_x, 5)  # setter
    assert q.x == (5 if PURE else 3)

    # still fine in the importing thread
    assert p.norm2() == 25
    assert threads.work(N) == sum(len(str(i) * 3) for i in range(N))


def test_imported_in_other_thread():
    # the importing thread decides: here a worker thread imports and uses the
    # module, and the main thread may not use it
    code = '''if 1:
        import sys, threading
        sys.path.insert(0, sys.argv[1])
        if sys.argv[2] == '--py':
            sys.path.insert(0, sys.argv[3])
        mod = []
        def run():
            import threads
            mod.append(threads)
            assert threads.work(200000) > 0
            assert threads.Point(3, 4).norm2() == 25
        t = threading.Thread(target=run)
        t.start()
        t.join()
        try:
            print(mod[0].work(10))
        except RuntimeError as e:
            print('RuntimeError:', e)
    '''
    out = subprocess.run(
        [sys.executable, '-c', code, os.path.join(HERE, 'build'), '--py' if PURE else '', HERE],
        capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr
    if PURE:
        assert out.stdout.strip() == '30', out.stdout
    else:
        assert out.stdout.startswith('RuntimeError:') and MSG in out.stdout, out.stdout


if __name__ == '__main__':
    tests = [(name, f) for (name, f) in sorted(globals().items()) if name.startswith('test_')]
    for name, f in tests:
        f()
    print('%s: %d tests passed (%s)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod'))
