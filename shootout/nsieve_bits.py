# The Computer Language Benchmarks Game
# http://shootout.alioth.debian.org/
#
# contributed by Kevin Carson
# optimized by Giovanni Bajo
# modified by Heinrich Acker

import sys, itertools

def primes_in_range(M):
    bits = [0xFF]*((M + 7) // 8)
    set_bits = [1 << (j+2 & 7) for j in range(8)]
    unset_bits = [~(1 << j) for j in range(8)]

    count = 0
    for i, sb in itertools.izip(xrange(2, M), itertools.cycle(set_bits)):
        if bits[i>>3] & sb:
            for j in xrange(i+i, M, i):
                bits[j>>3] &= unset_bits[j&7]
            count += 1

    print "Primes up to %8u %8u" % (M, count)

N = int(sys.argv[1])
for j in range(3):
    M = (1 << N-j) * 10000
    primes_in_range(M)
