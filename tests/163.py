
import time
time.sleep(1.01)

import sys
#print 'Python version:', sys.version
sys.stdout.flush()

a = '\001\00\0boink'
print repr('hello, world')
print repr('hello\0, world2')

print 'hello, world'
print repr('hello\0, world2') # XXX no repr!

print repr(a), len(a)
print repr(chr(0)), len(chr(0)+chr(0))
print repr('\0')
print repr(''.join([chr(i) for i in range(256)]))

class behh:
    def __init__(self, a, b, c):
        pass

behh(1,2,c=3)

# sudoku solver!! see: http://markbyers.com/moinmoin/moin.cgi/ShortestSudokuSolver
def r(a):
  i=a.find('0')
  if not ~i: print a; sys.exit()
  [m in [a[j] for j in range(81) if not (i-j)%9*(i/9^j/9)*(i/27^j/27|i%9/3^j%9/3)] or r(a[:i]+m+a[i+1:]) for m in '3814697265625']
  return True # because the type of an 'or' clause is the superset of its terms, we cannot (implicitly) return None here

r(81*'0')


