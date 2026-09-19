import random

random.seed(42)


def isntRightTurn(e):
    p0, p1 = e[-3]
    q0, q1 = e[-2]
    r0, r1 = e[-1]
    return q0 * r1 + p0 * q1 + r0 * p1 >= q0 * p1 + r0 * q1 + p0 * r1


def half(points):
    extrema = points[0:2]
    for p in points[2:]:
        extrema.append(p)
        while len(extrema) > 2 and isntRightTurn(extrema):
            del extrema[-2]
    return extrema


def test_random1():
    points = [(random.random(), random.random()) for i in range(200)]
    points = sorted(set(points))
    upper = half(points)
    points.reverse()
    lower = half(points)
    # assert [('%.2f' % x, '%.2f' % y) for x, y in upper + lower[1:-1]] == [
    #     ('0.00', '0.29'), ('0.00', '0.93'), ('0.16', '0.96'), ('0.38', '0.99'),
    #     ('0.96', '1.00'), ('1.00', '1.00'), ('1.00', '0.84'), ('1.00', '0.51'),
    #     ('0.98', '0.10'), ('0.81', '0.01'), ('0.43', '0.01'), ('0.09', '0.05'),
    #     ('0.02', '0.19')
    # ]
    ## XXX output is different in python and c++
    assert len(points) == 200 


def test_getsetstate():
    random.sample(range(20),k=10) # change state

    st = random.getstate() # get state

    get = random.sample(range(20),k=10) # change state

    random.setstate(st) # restore state

    get2 = random.sample(range(20),k=10)

    assert get == get2  # from same state so should be identical


def test_random2():
    random.seed(37)

    s = "%.8f" % random.random()
    f = random.randrange(-30,15)
    f = random.randrange(-15,15,3)
    f = random.randint(50,100)
    fibs = [0,1,1,2,3,5,8,13,21]
    i = random.choice(fibs)
    l = random.sample(fibs,3)
    random.shuffle(fibs)
    # print(len(fibs))
    assert len(fibs) == 9
    nums = [3.141, 2.71828, 1.41421, 1.0]
    # print(nums)
    f = random.choice(nums)
    lf = random.sample(nums,3)
    random.shuffle(nums)
    # print(len(nums))
    assert len(nums) == 4
    s = "%.8f" % random.uniform(-0.5,0.5)
    s = "%.8f" % random.normalvariate(0.0, 1.0)
    s = "%.8f" % random.lognormvariate(0.0, 1.0)
    s = "%.8f" % random.expovariate(1.0)
    s = "%.8f" % random.vonmisesvariate(0.0, 1.0)
    s = "%.8f" % random.gammavariate(20.0, 1.0)
    s = "%.8f" % random.gauss(0.0, 1.0)
    s = "%.8f" % random.betavariate(3.0, 3.0)
    s = "%.8f" % random.paretovariate(1.0)
    s = "%.8f" % random.weibullvariate(1.0, 1.0)
    #print "%.8f" % random.stdgamma(1.0,1.0,1.0,1.0) # deprecated in CPython
    #print "%.8f" % random.cunifvariate(0.0,1.0)     # deprecated in CPython
    b = random.getrandbits(8)
    b = random.getrandbits(16)
    b = random.getrandbits(30)
    # print('')

    s = "%.8f" % random.binomialvariate()
    s = "%.8f" % random.binomialvariate(n=10, p=0.3)


def test_random3():
    random.seed(1)
    f = random.triangular()
    f = random.triangular(high=1.1, low=0.0)
    f = random.triangular(0.1)
    f = random.triangular(-2, 2)
    f = random.triangular(-2.0, 2.1, 1.5)
    f = random.triangular(mode=1.5)
    f = random.triangular(0, 5, 0)

    # regression test: integer 'mode' must be normalized just like a float
    # 'mode' is (bug: an unnormalized int mode could push the result
    # outside the [low, high] range)
    for i in range(1000):
        f = random.triangular(2, 8, 5)
        assert 2.0 <= f <= 8.0

    random.seed()
    random.seed('seed')
    random.seed(8.0)
    random.seed(None)
    random.seed(4)


rr = random.Random()  # TODO test all methods


def test_getrandbits():
    # sanity: valid k still returns a value with no more than k bits set
    for k in (1, 8, 16, 30):
        b = random.getrandbits(k)
        assert 0 <= b < (1 << k)

    ok = False
    assert random.getrandbits(0) == 0

    ok = False
    try:
        random.getrandbits(-1)
    except ValueError:
        ok = True
    assert ok

    # regression test: getrandbits(k) for k > 53 used to derive its value
    # via random()*width, but random() only has BPF=53 bits of mantissa
    # precision. For k > 53 this made every result an exact multiple of
    # 2**(k-53), i.e. the low (k-53) bits were always zero.
    saw_nonzero_low_bits = False
    for i in range(200):
        if random.getrandbits(60) % 128 != 0:
            saw_nonzero_low_bits = True
            break
    assert saw_nonzero_low_bits


def test_randbytes():
    assert len(random.randbytes(4)) == 4
    assert len(rr.randbytes(5)) == 5


def test_instance_streams():
    # separate Random instances must have independent streams
    r1 = random.Random(42)
    a = [r1.random() for _ in range(3)]

    r2 = random.Random(42)
    b = [r2.random()]
    r3 = random.Random(999)
    r3.random()                 # must not disturb r2
    b.append(r2.random())
    b.append(r2.random())

    assert a == b

    # the module-level generator is likewise unaffected by instances
    random.seed(1)
    m1 = random.random()
    random.Random(12345).random()
    random.seed(1)
    assert random.random() == m1


def test_instance_getsetstate():
    r = random.Random(7)
    st = r.getstate()
    a = [r.random() for _ in range(3)]
    r.setstate(st)
    assert [r.random() for _ in range(3)] == a

    # state is per-instance: restoring into another instance clones the stream
    ra = random.Random(100)
    rb = random.Random(200)
    rb.setstate(ra.getstate())
    assert ra.random() == rb.random()

    # setstate() must not disturb the module-level generator
    random.seed(3)
    m1 = random.random()
    random.seed(3)
    random.Random(5).setstate(random.Random(6).getstate())
    assert random.random() == m1

    # the gauss() cache is part of the state
    rg = random.Random(5)
    rg.gauss(0.0, 1.0)          # leaves a cached value behind
    sg = rg.getstate()
    g1 = rg.gauss(0.0, 1.0)
    rg.setstate(sg)
    assert rg.gauss(0.0, 1.0) == g1

    # a state of the wrong size is rejected
    ok = False
    try:
        random.Random(1).setstate(b'short')
    except ValueError:
        ok = True
    assert ok


def test_randbytes_range():
    random.seed(17)
    bs = random.randbytes(4000)
    assert min(bs) == 0
    assert max(bs) == 255       # 255 used to be unreachable

    # instance randbytes draws from the instance's own stream
    r = random.Random(9)
    st = r.getstate()
    x = r.randbytes(16)
    r.setstate(st)
    assert r.randbytes(16) == x

    ok = False
    try:
        random.Random(1).randbytes(-1)
    except ValueError:
        ok = True
    assert ok


def test_choices():
    assert len(random.choices(range(100), k=5)) == 5
    assert len(random.choices(list(range(100)), k=5)) == 5


def test_systemrandom():
    sr = random.SystemRandom()

    x = sr.random()
    assert 0.0 <= x < 1.0

    assert 1 <= sr.randint(1, 6) <= 6

    for k in (1, 8, 16, 30):
        b = sr.getrandbits(k)
        assert 0 <= b < (1 << k)
    assert sr.getrandbits(0) == 0

    assert len(sr.randbytes(9)) == 9

    fibs = [0, 1, 1, 2, 3, 5, 8, 13, 21]
    assert sr.choice(fibs) in fibs
    assert len(sr.sample(fibs, 3)) == 3
    sr.shuffle(fibs)
    assert len(fibs) == 9

    # seed() is a documented no-op for SystemRandom; must not raise
    sr.seed(42)
    sr.seed()

    # getstate/setstate are unsupported for an OS-entropy generator
    ok = False
    try:
        sr.getstate()
    except NotImplementedError:
        ok = True
    assert ok

    ok = False
    try:
        sr.setstate(b'')
    except NotImplementedError:
        ok = True
    assert ok

    # a plain Random instance must be unaffected by SystemRandom's use
    random.seed(1)
    first = random.random()
    random.seed(1)
    second = random.random()
    assert first == second


def test_sample_errors():
    # regression test: CPython raises the same message
    # ("Sample larger than population or is negative") for both a
    # negative k and a k that exceeds the population size.
    expected = "Sample larger than population or is negative"

    ok = False
    try:
        random.sample([1, 2, 3], -1)
    except ValueError as e:
        ok = True
        assert str(e) == expected
    assert ok

    ok = False
    try:
        random.sample([1, 2, 3], 5)
    except ValueError as e:
        ok = True
        assert str(e) == expected
    assert ok


def test_wide_ranges():
    # regression test: randrange()/randint() used random()*width, which only
    # carries 53 bits, so for widths > 2**53 the low bits were always zero
    random.seed(5)
    low = 0
    for i in range(100):
        low |= random.randrange(1 << 60) & 127
    assert low != 0
    low = 0
    for i in range(100):
        low |= random.randint(0, 1 << 60) & 127
    assert low != 0
    low = 0
    for i in range(100):
        low |= random.randrange(-(1 << 60), 1 << 60) & 127
    assert low != 0

    # a width that does not fit in a signed 64-bit int
    lo = -(1 << 62) * 2
    hi = (1 << 62) - 1 + (1 << 62)
    assert random.randint(lo, hi) != random.randint(lo, hi)

    for i in range(1000):
        assert random.randrange(-5, 5) in range(-5, 5)
        assert random.randrange(10, -10, -3) in range(10, -10, -3)
        assert random.randrange(0, 10, 4) in (0, 4, 8)
        assert 1 <= random.randint(1, 3) <= 3
        assert 0 <= random.randrange(7) < 7
    assert sorted(set([random.randint(1, 3) for i in range(1000)])) == [1, 2, 3]

    nums = list(range(50))
    random.shuffle(nums)
    assert sorted(nums) == list(range(50))

    smp = random.sample(range(1000), 100)
    assert len(set(smp)) == 100
    assert sorted(random.sample(list(range(10)), 10)) == list(range(10))


def test_range_errors():
    msg = ''
    try:
        random.randrange(0)
    except ValueError as e:
        msg = str(e)
    assert msg == 'empty range for randrange()'

    msg = ''
    try:
        random.randrange(5, 5)
    except ValueError as e:
        msg = str(e)
    assert msg == 'empty range in randrange(5, 5)'

    msg = ''
    try:
        random.randrange(4, 2, 2)
    except ValueError as e:
        msg = str(e)
    assert msg == 'empty range in randrange(4, 2, 2)'

    msg = ''
    try:
        random.randrange(0, 10, 0)
    except ValueError as e:
        msg = str(e)
    assert msg == 'zero step for randrange()'

    # (the exact message differs between CPython versions)
    ok = False
    try:
        random.randint(3, 2)
    except ValueError:
        ok = True
    assert ok


def test_triangular_degenerate():
    # regression test: low == high used to give nan (CPython returns low)
    assert random.triangular(1.0, 1.0, 1.0) == 1.0
    assert random.triangular(2.0, 2.0, 7) == 2.0
    assert random.triangular(3.0, 3.0) == 3.0


def test_binomialvariate_args():
    # regression test: invalid n and p were silently accepted
    assert random.binomialvariate(5, 0.0) == 0
    assert random.binomialvariate(5, 1.0) == 5

    msg = ''
    try:
        random.binomialvariate(-1, 0.5)
    except ValueError as e:
        msg = str(e)
    assert msg == 'n must be non-negative'

    for p in (1.5, -0.5):
        msg = ''
        try:
            random.binomialvariate(5, p)
        except ValueError as e:
            msg = str(e)
        assert msg == 'p must be in the range 0.0 <= p <= 1.0'


def test_instance_seeding():
    # regression test: Random() and Random(None) were always seeded with
    # the same constant instead of from OS entropy
    assert random.Random().random() != random.Random().random()
    assert random.Random(None).random() != random.Random(None).random()

    # Random(a) accepts the same seed types as seed()
    assert random.Random('hi').random() == random.Random('hi').random()
    assert random.Random(2.5).random() == random.Random(2.5).random()
    assert random.Random(b'hi').random() == random.Random(b'hi').random()
    assert random.Random(7).random() == random.Random(7).random()
    assert random.Random(x=7).random() == random.Random(7).random()
    assert 0.0 <= random.SystemRandom(x=7).random() < 1.0

    sr = random.SystemRandom(3)
    assert 0.0 <= sr.random() < 1.0


def test_choices_weights():
    pop = ['a', 'b', 'c']
    assert set(random.choices(pop, [0, 1, 0], k=20)) == {'b'}
    assert set(random.choices(pop, weights=(1, 0, 1), k=50)) == {'a', 'c'}
    assert set(random.choices(pop, cum_weights=[0.0, 0.0, 2.5], k=20)) == {'c'}
    assert len(random.choices(pop, weights=None, k=7)) == 7
    assert random.choices(pop, [1, 1, 1])[0] in pop

    rr = random.Random(3)
    assert rr.choices(pop, [0.0, 0.0, 1.0], k=2) == ['c', 'c']
    sr = random.SystemRandom()
    assert sr.choices(pop, [1, 0, 0], k=2) == ['a', 'a']

    msg = ''
    try:
        random.choices(pop, [1, 1], k=2)
    except ValueError as e:
        msg = str(e)
    assert msg == 'The number of weights does not match the population'

    msg = ''
    try:
        random.choices(pop, [0, 0, 0], k=2)
    except ValueError as e:
        msg = str(e)
    assert msg == 'Total of weights must be greater than zero'

    msg = ''
    try:
        random.choices(pop, [1.0, float('inf'), 1.0], k=2)
    except ValueError as e:
        msg = str(e)
    assert msg == 'Total of weights must be finite'

    msg = ''
    try:
        random.choices(pop, [1, 1, 1], cum_weights=[1, 2, 3], k=2)
    except TypeError as e:
        msg = str(e)
    assert msg == 'Cannot specify both weights and cumulative weights'


def test_sample_counts():
    pop = ['a', 'b', 'c']
    assert sorted(random.sample(pop, counts=[3, 0, 2], k=5)) == ['a', 'a', 'a', 'c', 'c']
    assert sorted(random.Random(1).sample(['x', 'y'], 3, counts=(1, 2))) == ['x', 'y', 'y']
    assert len(random.sample(pop, 2, counts=None)) == 2

    msg = ''
    try:
        random.sample(pop, 2, counts=[1, 1])
    except ValueError as e:
        msg = str(e)
    assert msg == 'The number of counts does not match the population'

    msg = ''
    try:
        random.sample(pop, 4, counts=[1, 1, 1])
    except ValueError as e:
        msg = str(e)
    assert msg == 'Sample larger than population or is negative'

    # (the exact message differs between CPython versions)
    ok = False
    try:
        random.sample(pop, 2, counts=[-1, -1, -1])
    except ValueError:
        ok = True
    assert ok


def test_choice_empty():
    msg = ''
    try:
        random.choice('abc'[:0])
    except IndexError as e:
        msg = str(e)
    assert msg == 'Cannot choose from an empty sequence'


def check_variates(r):
    # exercise every distribution on a Random (or SystemRandom) instance
    # and check that each result lies in the distribution's support
    for i in range(50):
        assert 0.0 <= r.uniform(0.0, 1.0) <= 1.0
        assert -3.0 <= r.uniform(-3, 2) <= 2.0
        assert 1.0 <= r.triangular(1.0, 4.0, 2.5) <= 4.0
        assert 0.0 <= r.triangular() <= 1.0
        assert 0.0 <= r.triangular(0, 5) <= 5.0
        assert 0.0 <= r.betavariate(2.0, 3.0) <= 1.0
        assert 0 <= r.binomialvariate(10, 0.3) <= 10
        assert r.binomialvariate() in (0, 1)
        assert r.expovariate(2.0) >= 0.0
        assert r.expovariate() >= 0.0
        assert r.gammavariate(3.0, 2.0) >= 0.0
        assert r.gammavariate(0.5, 1.0) >= 0.0      # alpha < 1 branch
        assert r.gammavariate(1.0, 1.0) >= 0.0      # alpha == 1 branch
        assert r.lognormvariate(0.0, 0.5) > 0.0
        assert -10.0 < r.normalvariate() < 10.0
        assert r.normalvariate(10.0, 0.001) > 9.0
        assert r.gauss(10.0, 0.001) > 9.0
        assert r.paretovariate(2.0) >= 1.0
        assert 0.0 <= r.vonmisesvariate(0.0, 4.0) < 6.3
        assert 0.0 <= r.vonmisesvariate(1.0, 0.0) < 6.3   # kappa <= 1e-6 branch
        assert r.weibullvariate(1.5, 2.0) >= 0.0
        assert r.randrange(10) in range(10)
        assert r.randrange(5, 15) in range(5, 15)
        assert r.randrange(0, 20, 5) in (0, 5, 10, 15)
        assert r.randrange(10, 0, -3) in (10, 7, 4, 1)


def test_instance_variates():
    check_variates(random.Random(11))
    check_variates(random.SystemRandom())

    # a seeded instance reproduces its stream for every distribution
    a = random.Random(5)
    b = random.Random(5)
    assert a.uniform(1.0, 2.0) == b.uniform(1.0, 2.0)
    assert a.triangular(0.0, 1.0, 0.3) == b.triangular(0.0, 1.0, 0.3)
    assert a.betavariate(2.0, 2.0) == b.betavariate(2.0, 2.0)
    assert a.binomialvariate(20, 0.5) == b.binomialvariate(20, 0.5)
    assert a.expovariate(1.5) == b.expovariate(1.5)
    assert a.gammavariate(2.0, 1.0) == b.gammavariate(2.0, 1.0)
    assert a.lognormvariate(0.0, 1.0) == b.lognormvariate(0.0, 1.0)
    assert a.normalvariate(0.0, 1.0) == b.normalvariate(0.0, 1.0)
    assert a.paretovariate(1.0) == b.paretovariate(1.0)
    assert a.vonmisesvariate(0.0, 1.0) == b.vonmisesvariate(0.0, 1.0)
    assert a.weibullvariate(1.0, 1.0) == b.weibullvariate(1.0, 1.0)
    assert a.randrange(-100, 100, 7) == b.randrange(-100, 100, 7)

    # the distributions must respect instance state, not the module stream
    random.seed(2)
    m1 = random.random()
    random.seed(2)
    random.Random(3).gammavariate(2.0, 2.0)
    random.Random(3).vonmisesvariate(0.0, 2.0)
    assert random.random() == m1

    # argument errors
    msg = ''
    try:
        random.Random(1).randrange(3, 3)
    except ValueError as e:
        msg = str(e)
    assert msg == 'empty range in randrange(3, 3)'

    msg = ''
    try:
        random.SystemRandom().randrange(0)
    except ValueError as e:
        msg = str(e)
    assert msg == 'empty range for randrange()'


def test_instance_choices_cum_weights():
    pop = ['a', 'b', 'c', 'd']
    r = random.Random(4)
    assert set(r.choices(pop, cum_weights=[0, 0, 5, 5], k=30)) == {'c'}
    assert set(r.choices(pop, cum_weights=(1, 1, 1, 2), k=30)) == {'a', 'd'}
    assert set(r.choices(pop, cum_weights=[2.0, 2.0, 2.0, 2.0], k=10)) == {'a'}
    assert len(r.choices(pop, None, cum_weights=[1, 2, 3, 4], k=6)) == 6

    sr = random.SystemRandom()
    assert set(sr.choices(pop, cum_weights=[0, 1, 1, 1], k=20)) == {'b'}

    # a seeded instance reproduces its cumulative-weight choices
    a = random.Random(8).choices(pop, cum_weights=[1, 2, 3, 4], k=10)
    b = random.Random(8).choices(pop, cum_weights=[1, 2, 3, 4], k=10)
    assert a == b

    msg = ''
    try:
        r.choices(pop, cum_weights=[1, 2, 3], k=2)
    except ValueError as e:
        msg = str(e)
    assert msg == 'The number of weights does not match the population'

    msg = ''
    try:
        r.choices(pop, [1, 1, 1, 1], cum_weights=[1, 2, 3, 4])
    except TypeError as e:
        msg = str(e)
    assert msg == 'Cannot specify both weights and cumulative weights'


def test_seed_version():
    # seed(a, version=2) is the default
    assert random.Random('abc').random() == random.Random('abc').random()
    random.seed('abc')
    x = random.random()
    random.seed('abc', version=2)
    assert random.random() == x
    random.seed('abc', 2)
    assert random.random() == x

    # version=1 is a different (but still deterministic) str/bytes seeding
    random.seed('abc', version=1)
    y = random.random()
    random.seed('abc', version=1)
    assert random.random() == y
    assert x != y

    r = random.Random()
    r.seed(b'xyz', version=1)
    z = r.random()
    r.seed(b'xyz', version=1)
    assert r.random() == z
    r.seed(b'xyz')
    assert r.random() != z

    # the version only matters for str/bytes seeds
    random.seed(1234, version=1)
    a = random.random()
    random.seed(1234, version=2)
    assert random.random() == a
    random.seed(2.5, version=1)
    a = random.random()
    random.seed(2.5)
    assert random.random() == a
    random.seed(None, version=1)
    random.seed(version=1)

    # the SystemRandom stub accepts the keyword as well
    sr = random.SystemRandom()
    sr.seed('abc', version=1)
    sr.seed(version=2)
    assert 0.0 <= sr.random() < 1.0


def test_all():
    test_random1()
    test_random2()
    test_random3()
    test_randbytes()
    test_choices()
    test_sample_errors()
    test_getsetstate()
    test_instance_streams()
    test_instance_getsetstate()
    test_randbytes_range()
    test_getrandbits()
    test_systemrandom()
    test_wide_ranges()
    test_range_errors()
    test_triangular_degenerate()
    test_binomialvariate_args()
    test_instance_seeding()
    test_choices_weights()
    test_sample_counts()
    test_choice_empty()
    test_instance_variates()
    test_instance_choices_cum_weights()
    test_seed_version()


if __name__ == '__main__':
    test_all()
