# The Computer Language Shootout
# http://shootout.alioth.debian.org/
#
# Contributed by Sebastien Loisel
# Fixed by Isaac Gouy
# Sped up by Josh Goldfoot

import math, sys, itertools

def eval_A(i,j):
    return 1.0/((i+j)*(i+j+1)/2+i+1)

def eval_A_times_u(u):
    return [sum(eval_A(i,j)*u[j] for j in xrange(len(u)))
            for i in xrange(len(u))]

def eval_At_times_u(u):
    return [sum(eval_A(j,i)*u[j] for j in xrange(len(u)))
            for i in xrange(len(u))]

def eval_AtA_times_u(u):
    return eval_At_times_u(eval_A_times_u(u))

def main():
    n = int(sys.argv[1])
    u = [1]*n
    for i in xrange(10):
        v=eval_AtA_times_u(u)
        u=eval_AtA_times_u(v)
    vBv = vv = 0
    for ue, ve in itertools.izip(u,v):
        vBv += ue * ve
        vv += ve * ve
    print "%0.9f" % (math.sqrt(vBv/vv))

main()
