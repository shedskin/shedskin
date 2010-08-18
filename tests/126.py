
# (c) Wensheng Wang

from math import sqrt

def primes(n):                           # n: [int]
   "primes(n): return a list of prime numbers <=n."

   if n == 2:                            # [int]
       return [2]                        # [list(int)]
   elif n<2:                             # [int]
       return []                         # [list(int)]
   s = range(3, n+2, 2)                  # [list(int)]
   mroot = n ** 0.5                      # [float]
   #mroot = sqrt(n)
   half = len(s)                         # [int]
   i = 0                                 # [int]
   m = 3                                 # [int]
   while m <= mroot:                     # [int]
       if s[i]:                          # [int]
           j = (m*m - 3) / 2             # [int]
           s[j] = 0                      # [int]
           while j < half:               # [int]
               s[j] = 0                  # [int]
               j += m                    # [int]
       i += 1                            # [int]
       m = 2 * i + 3                     # [int]
   if s[-1] > n:
       s[-1] = 0
   #return [2] + filter(None, s)
   return [2] + [x for x in s if x]      # [list(int)]

print primes(100)                        # [list(int)]

