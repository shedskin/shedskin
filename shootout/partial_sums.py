# The Computer Language Benchmarks Game
# http://shootout.alioth.debian.org/
#
# contributed by Josh Goldfoot
# modified by Mike Klaas
# modified by Dani Nanz 2007-08-28, also considering input from Tupteq

import sys
import math

def doit(n):

    alt = -1.
    twothirds = 2. / 3.
    k = s0 = 1.
    s1 = s2 = s3 = s4 = s5 = s6 = s7 = s8 = 0.
    while k <= n:
        k2 = k * k
        k3 = k2 * k
        ks, kc = math.sin(k), math.cos(k)
        alt = -alt
        s0 += twothirds ** k
        s1 += k ** -.5
        s2 += 1. / (k * (k + 1.))
        s3 += 1. / (k3 * ks * ks)
        s4 += 1. / (k3 * kc * kc)
        s5 += 1. / k
        s6 += 1. / k2
        s7 += alt / k
        s8 += alt / (k + k - 1.)
        k += 1.
    fmt = '\n%0.9f\t'
    nms = ['(2/3)^k', 'k^-0.5', '1/k(k+1)', 'Flint Hills', 'Cookson Hills',
           'Harmonic', 'Riemann Zeta', 'Alternating Harmonic', 'Gregory']
    print (fmt[1:] + fmt.join(nms)) % (s0, s1, s2, s3, s4, s5, s6, s7, s8)

doit(float(sys.argv[1]))

