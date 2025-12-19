# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)

import math
import time

NV_MAGICCONST = 1.0
LOG4 = 1.0
SG_MAGICCONST = 1.0
BPF = 1
MAXWIDTH = 1
MAXINT = 1
N = 1
M = 1
MATRIX_A = 1
UPPER = 1
LOWER = 1

class Random:
    def __init__(self, a=-1): return 1
    def seed(self, a=None):
        a.__hash__()
    def random(self): return 1.0
    def getstate(self): return [1.0,1.0,1.0]
    def setstate(self, state): pass
    def randrange(self, start, stop=1, step=1): return 1
    def randint(self, a, b): return 1
    def randbytes(self, n): return b''
    def getrandbits(self, k): return 1
    def choice(self, seq): return seq[seq.__len__()]
    def choices(self, seq, k=1): return [seq[seq.__len__()]]
    def shuffle(self, x): pass
    def sample(self, population, k): return [iter(population).__next__()]
    def uniform(self, a, b): return 1.0
    def triangular(self, low=0.0, high=1.0, mode=None): return 1.0
    def normalvariate(self, mu=0.0, sigma=1.0): return 1.0
    def lognormvariate(self, mu, sigma): return 1.0
    def cunifvariate(self, mean, arc): return 1.0
    def expovariate(self, lambd=1.0): return 1.0
    def vonmisesvariate(self, mu, kappa): return 1.0
    def gammavariate(self, alpha, beta): return 1.0
    def stdgamma(self, alpha, ainv, bbb, ccc): return 1.0
    def gauss(self, mu=0.0, sigma=1.0): return 1.0
    def betavariate(self, alpha, beta): return 1.0
    def paretovariate(self, alpha): return 1.0
    def weibullvariate(self, alpha, beta): return 1.0
    def binomialvariate(self, n=1, p=0.5): return 1


_inst = Random()
def seed(a=None):
    _inst.seed(a)
def random(): return 1.0
def getstate(): return [1.0,1.0,1.0]
def setstate(state): pass
def randrange(start, stop=1, step=1): return 1
def randint(a, b): return 1
def randbytes(n): return b''
def getrandbits(k): return 1
def choice(seq): return seq[seq.__len__()]
def choices(seq, k=1): return [seq[seq.__len__()]]
def shuffle(x): pass
def sample(population, k): return [iter(population).__next__()]
def uniform(a, b): return 1.0
def triangular(low=0.0, high=1.0, mode=None): return 1.0
def normalvariate(mu=0.0, sigma=1.0): return 1.0
def lognormvariate(mu, sigma): return 1.0
def cunifvariate(mean, arc): return 1.0
def expovariate(lambd=1.0): return 1.0
def vonmisesvariate(mu, kappa): return 1.0
def gammavariate(alpha, beta): return 1.0
def stdgamma(alpha, ainv, bbb, ccc): return 1.0
def gauss(mu=0.0, sigma=1.0): return 1.0
def betavariate(alpha, beta): return 1.0
def paretovariate(alpha): return 1.0
def weibullvariate(alpha, beta): return 1.0
def binomialvariate(n=1, p=0.5): return 1
