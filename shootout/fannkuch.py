# The Computer Language Shootout
# http://shootout.alioth.debian.org/
#
# Contributed by Sokolov Yura

from sys import argv

def fannkuch(n):
   count = range(1,n+1)
   maxFlipsCount, m, r, check = 0, n-1, n, 0

   perm1 = range(n)
   perm  = range(n)
   while True:
      if check < 30:
         print "".join([str(i+1) for i in perm1])
         check += 1;

      while r != 1:
         count[r-1] = r
         r -= 1

      if perm1[0] != 0 and perm1[m] != m:
         for i in xrange(n):
             perm[i] = perm1[i] 
         flipsCount = 0
         k = perm[0]
         while k:
            for x in range((k+1)/2):
                perm[x], perm[k-x] = perm[k-x], perm[x]
            flipsCount += 1
            k = perm[0]

         if flipsCount > maxFlipsCount:
            maxFlipsCount = flipsCount
            maxPerm = list(perm1)

      while True:
         if r == n: return maxFlipsCount
         temp = perm1[0]
         for i in range(r):
             perm1[i] = perm1[i+1]
         perm1[r] = temp

         count[r] -= 1
         if count[r] > 0: break
         r += 1

def main():
    n = int(argv[1])
    print "Pfannkuchen(%d) = %d\n"%(n,fannkuch(n)),

if __name__=="__main__":
    main()

