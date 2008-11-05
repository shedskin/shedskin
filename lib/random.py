import math
import time

__all__ = ["Random","seed","random","uniform","randint","choice","sample",
           "randrange","shuffle","normalvariate","lognormvariate",
           "cunifvariate","expovariate","vonmisesvariate","gammavariate",
           "stdgamma","gauss","betavariate","paretovariate","weibullvariate",
           "getstate","setstate","jumpahead", "WichmannHill"]

# Constants
NV_MAGICCONST = 4 * math.exp(-0.5)/math.sqrt(2.0)
LOG4 = math.log(4.0)
SG_MAGICCONST = 1.0 + math.log(4.5)
BPF = 53        # Number of bits in a float
MAXWIDTH = 1L<<BPF
MAXINT = 0x7fffffff

# Mersenne Twister constants
N = 624  # Period parameters
M = 397
MATRIX_A = 0x9908b0dfL   # constant vector a
UPPER = 0x80000000L # most significant w-r bits
LOWER = 0x7fffffffL # least significant r bits

class Random:
    def __init__(self, a=-1): return 1
    def seed(self, a=-1): pass
    def random(self): return 1.0
    def _genrand_res53(self): return 1.0
    def _genrand_int32(self): return 1
    def _init_genrand(self, s): return 1
    def _init_by_array(self, init_key): return 1
    def getstate(self): return [1.0,1.0,1.0]
    def setstate(self, state): return 1
    def getrandbits(self, k): return 1
    def randrange(self, start, stop=1, step=1): return 1
    def randint(self, a, b): return 1
    def choice(self, seq): return seq[seq.__len__()]
    def shuffle(self, x): return x
    def sample(self, population, k): return [iter(population).next()]
    def uniform(self, a, b): return 1.0
    def normalvariate(self, mu, sigma): return 1.0
    def lognormvariate(self, mu, sigma): return 1.0
    def cunifvariate(self, mean, arc): return 1.0
    def expovariate(self, lambd): return 1.0
    def vonmisesvariate(self, mu, kappa): return 1.0
    def gammavariate(self, alpha, beta): return 1.0
    def stdgamma(self, alpha, ainv, bbb, ccc): return 1.0
    def gauss(self, mu, sigma): return 1.0
    def betavariate(self, alpha, beta): return 1.0
    def paretovariate(self, alpha): return 1.0
    def weibullvariate(self, alpha, beta): return 1.0

class WichmannHill(Random):
    def __init__(self, a=-1): return 1
    def seed(self, a=-1): pass
    def random(self): return 1.0
    def getstate(self): return [1.0,1.0,1.0]
    def setstate(self, state): return 1
    def jumpahead(self, n): return 1
    def __whseed(self, x=0, y=0, z=0): pass
    def whseed(self, a=-1): pass


_inst = Random()
def seed(a=-1): pass
def random(): return 1.0
def getstate(): return [1.0,1.0,1.0]
def setstate(state): return 1
def randrange(start, stop=1, step=1): return 1
def randint(a, b): return 1
def choice(seq): return seq[seq.__len__()]
def shuffle(x): return x
def sample(population, k): return [iter(population).next()]
def uniform(a, b): return 1.0
def normalvariate(mu, sigma): return 1.0
def lognormvariate(mu, sigma): return 1.0
def cunifvariate(mean, arc): return 1.0
def expovariate(lambd): return 1.0
def vonmisesvariate(mu, kappa): return 1.0
def gammavariate(alpha, beta): return 1.0
def stdgamma(alpha, ainv, bbb, ccc): return 1.0
def gauss(mu, sigma): return 1.0
def betavariate(alpha, beta): return 1.0
def paretovariate(alpha): return 1.0
def weibullvariate(alpha, beta): return 1.0
def getrandbits(k): return 1

