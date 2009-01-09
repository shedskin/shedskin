# The Computer Language Shootout
# http://shootout.alioth.debian.org/
# based on bearophile's psyco program
# slightly modified by Isaac Gouy

def Ack(x, y):
    if x == 0: return y+1
    if y == 0: return Ack(x-1, 1)
    return Ack(x-1, Ack(x, y-1))

def Fib(n):
    if n < 2: return 1
    return Fib(n-2) + Fib(n-1)

def FibFP(n):
    if n < 2.0: return 1.0
    return FibFP(n-2.0) + FibFP(n-1.0)

def Tak(x, y, z):
    if y < x: return Tak( Tak(x-1,y,z), Tak(y-1,z,x), Tak(z-1,x,y) )
    return z

def TakFP(x, y, z):
    if y < x: return TakFP( TakFP(x-1.0,y,z), TakFP(y-1.0,z,x), TakFP(z-1.0,x,y) )
    return z

from sys import argv

n = int(argv[1]) - 1
print "Ack(3,%d):" % (n+1), Ack(3, n+1)
print "Fib(%.1f): %.1f" % (28.0+n, FibFP(28.0+n))
print "Tak(%d,%d,%d): %d" % (3*n, 2*n, n, Tak(3*n, 2*n, n))
print "Fib(3):", Fib(3)
print "Tak(3.0,2.0,1.0):", TakFP(3.0, 2.0, 1.0)

