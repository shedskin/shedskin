# The Computer Language Benchmarks Game
# http://shootout.alioth.debian.org/
# Written by Dima Dorfman, 2004

# modified by Heinrich Acker
# modified by Dani Nanz 2007-10-03

import sys
from itertools import count, islice, izip

def nsieve(m, c=0):

    a = [True] * (m + 1)
    iu = m // 2    # faster but not compliant: iu = int(m ** 0.5)
    for i, x in izip(count(2), islice(a, 2, None)):
        if x:
            c += 1
            if i <= iu:
                a[i + i :: i] = (False, ) * ((m - i) // i)
    print 'Primes up to %8d %8d' % (m, c)


for k in 0, 1, 2:
    nsieve((1 << (int(sys.argv[1]) - k)) * 10000)

