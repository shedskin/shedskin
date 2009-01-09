# The Great Computer Language Shootout
# http://shootout.alioth.debian.org/
# nsieve benchmark for Psyco
# Optimized from the Free Pascal version by bearophile, Jan 1 2006

import sys

def nsieve(m, c=0):
    a = [True] * (m + 1)
    n1 = m + 1
    for i in xrange(2, n1):
        if a[i]:
            c += 1
            k = i << 1
            while k < n1:
                if a[k]: a[k] = False
                k += i
    print 'Primes up to %8d %8d' % (m, c)

for k in 0, 1, 2:
    nsieve((1 << (int(sys.argv[1]) - k)) * 10000)

