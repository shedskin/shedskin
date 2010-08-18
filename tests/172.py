

import random

# --- module-level functions
random.seed(37)
rstate = random.getstate()   # (state is not cross-compatible with CPython)
random.setstate(rstate)
for i in range(25):
    print "%.8f" % random.random()
    print random.randrange(-30,15)
    print random.randrange(-15,15,3)
    print random.randint(50,100)
    fibs = [0,1,1,2,3,5,8,13,21]
    print fibs
    print random.choice(fibs)
    print random.sample(fibs,3)
    random.shuffle(fibs)
    print fibs
    nums = [3.141, 2.71828, 1.41421, 1.0]
    print nums
    print random.choice(nums)
    print random.sample(nums,3)
    random.shuffle(nums)
    print nums
    print "%.8f" % random.uniform(-0.5,0.5)
    print "%.8f" % random.normalvariate(0.0, 1.0)
    print "%.8f" % random.lognormvariate(0.0, 1.0)
    print "%.8f" % random.expovariate(1.0)
    print "%.8f" % random.vonmisesvariate(0.0, 1.0)
    print "%.8f" % random.gammavariate(20.0, 1.0)
    print "%.8f" % random.gauss(0.0, 1.0)
    print "%.8f" % random.betavariate(3.0, 3.0)
    print "%.8f" % random.paretovariate(1.0)
    print "%.8f" % random.weibullvariate(1.0, 1.0)
    #print "%.8f" % random.stdgamma(1.0,1.0,1.0,1.0) # deprecated in CPython
    #print "%.8f" % random.cunifvariate(0.0,1.0)     # deprecated in CPython
    print random.getrandbits(8)
    print random.getrandbits(16)
    print random.getrandbits(30)
    print ''

# --- (test set for RNGs)
def runrng(r):
    print "%.8f" % r.random()
    print r.randrange(0,10)
    print r.randrange(-10,10,2)
    print r.randint(-5,5)
    fibs = [0,1,1,2,3,5,8,13,21]
    print fibs
    print r.choice(fibs)
    print r.sample(fibs,4)
    r.shuffle(fibs)
    print fibs
    nums = [3.141, 2.71828, 1.41421, 1.0]
    print nums
    print random.choice(nums)
    print random.sample(nums,1)
    random.shuffle(nums)
    print nums
    print "%.8f" % r.uniform(-0.5,0.5)
    print "%.8f" % r.normalvariate(0.0, 1.0)
    print "%.8f" % r.lognormvariate(0.0, 1.0)
    print "%.8f" % r.expovariate(1.0)
    print "%.8f" % r.vonmisesvariate(0.0, 1.0)
    print "%.8f" % r.gammavariate(20.0, 1.0)
    print "%.8f" % r.gauss(0.0, 1.0)
    print "%.8f" % r.betavariate(3.0, 3.0)
    print "%.8f" % r.paretovariate(1.0)
    print "%.8f" % r.weibullvariate(1.0, 1.0)
    #print "%.8f" % r.stdgamma(1.0, 1.0, 1.0, 1.0) # deprecated in CPython
    #print "%.8f" % r.cunifvariate(0.0, 1.0)       # deprecated in CPython
    print ''

# --- random.Random (Mersenne Twister)
mt = random.Random()
mt.seed()
mt.seed(79)
mtstate = mt.getstate()   # (state is not cross-compatible with CPython)
mt.setstate(mtstate)
#mt.jumpahead(1000000)    # (not yet supported)
for i in range(25): runrng(mt)

# --- random.WichmannHill
wh = random.WichmannHill()
wh.seed()
wh.seed(86)
wh.whseed()
wh.whseed(41)
whstate = wh.getstate()   # (state is not cross-compatible with CPython)
wh.setstate(whstate)
wh.jumpahead(1000000)
for i in range(25): runrng(wh)


