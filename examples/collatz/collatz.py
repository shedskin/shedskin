# find collatz/3x+1 delay records
# copyright mark dufour 2023
#
# tricks:
# -uses parity sequences to take multiple steps at once
# (https://en.wikipedia.org/wiki/Collatz_conjecture)
# -skips about half of the numbers since they cannot be records
# (https://math.stackexchange.com/questions/60573/reducing-the-time-to-calculate-collatz-sequences)
#
# caveat:
# - requires shedskin --long (64-bit integers.. no 128-bit support yet)
# - doesn't check for 64-bit overflow (in generated C++)!
#
# results (N=100000000) checked against:
#
# http://www.ericr.nl/wondrous/delrecs.html

import time

N = 100000000
K = 17
bmask = 2**K-1

def step(n, extra=False):
    if n % 2 == 0:
        return n // 2
    else:
        if extra:
            return (3*n + 1) // 2
        else:
            return (3*n + 1)

# lookups to perform K steps in one
lookup_multistep = list(range(0, 2**K))
lookup_c = [0] * len(lookup_multistep)

for k in range(K):
    lookup_c = [c + (i%2) for (i, c) in zip(lookup_multistep, lookup_c)]
    lookup_multistep = [step(i, True) for i in lookup_multistep]

lookup_pow = [3**c for c in range(K+1)]

# lookup for final steps (< 2**K)
lookup_tail = [0]
for n in range(1, 2**K):
    steps = 0
    while n != 1:
        n = step(n)
        steps += 1
    lookup_tail.append(steps)

print('1 2') # skipped record

t0 = time.time()

delay_record = 0
rest9 = 1
for n in range(2, N):
    # skip 2, 4, 5, 8 mod 9 and 5 mod 8
    # as these cannot be records (see link in top)
    rest9 += 1
    if rest9 == 9:
        rest9 = 0
    if rest9 in (2, 4, 5, 8):
        continue
    if n & 7 == 5: # 5 mod 8
       continue

    # use multistep lookups (see link in top)
    orign = n
    steps = 0

    while n > bmask:
        a = n >> K
        b = n & bmask

        c = lookup_c[b]
        d = lookup_multistep[b]

        steps += 2*c + (K-c)

        n = a*lookup_pow[c]+d

    # add final steps
    steps += lookup_tail[n]

    # check record
    if steps > delay_record:
        delay_record = steps
        print(delay_record, orign)

print('%.2f numbers/second' % (N/((time.time()-t0))))
