

# (c) Wensheng Wang


def primes(n):                           # n: [int]
   "primes(n): return a list of prime numbers <=n."

   if n == 2:                            # [int]
       return [2]                        # [list(int)]
   elif n<2:                             # [int]
       return []                         # [list(int)]
   s = list(range(3, n+2, 2))                  # [list(int)]
   mroot = n ** 0.5                      # [float]
   #mroot = sqrt(n)
   half = len(s)                         # [int]
   i = 0                                 # [int]
   m = 3                                 # [int]
   while m <= mroot:                     # [int]
       if s[i]:                          # [int]
           j = (m*m - 3) // 2             # [int]
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

# print(primes(100))                        # [list(int)]


def test_primes():
    assert primes(100) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

def test_all():
    test_primes()

if __name__ == '__main__':
    test_all()


