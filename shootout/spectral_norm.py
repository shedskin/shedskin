# The Computer Language Shootout
# http://shootout.alioth.debian.org/
#
# Contributed by Sebastien Loisel
# Fixed by Isaac Gouy
# Sped up by Josh Goldfoot

import sys, math

def eval_A(i,j):
    return 1.0 / ( (i+j) * (i+j+1) / 2 + i + 1 )

def eval_A_times_u(u):
    lenu = len(u)
    v = [0.0] * lenu
    for i in xrange(lenu):
        aux = 0.0
        for j in xrange(lenu):
            aux += eval_A(i,j) * u[j]
        v[i] = aux
    return v

def eval_At_times_u(u):
    lenu = len(u)
    v = [0.0] * lenu
    for i in xrange(lenu):
        aux = 0.0
        for j in xrange(lenu):
            aux += eval_A(j,i) * u[j]
        v[i] = aux
    return v

def eval_AtA_times_u(u):
    return eval_At_times_u(eval_A_times_u(u))

def main():
    n = int(sys.argv[1])
    u = [1.0] * n
    for i in xrange(10):
       v = eval_AtA_times_u(u)
       u = eval_AtA_times_u(v)
    vBv = 0.0
    vv = 0.0
    for i in xrange(n):
       vBv += u[i] * v[i]
       vv += v[i] * v[i]
    print math.sqrt(vBv/vv)

main()
