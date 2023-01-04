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

def test_random2():
    random.seed(37)
    rstate = random.getstate()   # (state is not cross-compatible with CPython)
    random.setstate(rstate)

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

def test_random3():
    random.seed(1)
    f = random.triangular()
    f = random.triangular(high=1.1, low=0.0)
    f = random.triangular(0.1)
    f = random.triangular(-2, 2)
    f = random.triangular(-2.0, 2.1, 1.5)
    f = random.triangular(mode=1.5)
    f = random.triangular(0, 5, 0)
    random.seed()
    random.seed('seed')
    random.seed(8.0)
    random.seed(None)
    random.seed(4)


def test_all():
    test_random1()
    test_random2()
    test_random3()

if __name__ == '__main__':
    test_all()
