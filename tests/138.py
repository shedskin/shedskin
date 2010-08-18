
x = [0,1]
i, x[i] = 1, 2
print x

from math import *
sin(pi)

print repr('    '.strip())

print 'a\vb'.split()

s1={1:"a",2:"b"}; s2={1:"a",2:"b"}; print s1 == s2, s1 != s2

print "ab cd\tef\ngh\ril\vmn\fop".split()

a=2; b=3; print bool(a==b)

def test():
    s1, s2 = "ab", "AB"
    alist = ["_"] * 2
    for pos in range(2):
        alist[ord(s1[pos])-ord('a')] = s2[pos]
    return alist
print test()

def f(s): return [s[0] for j in xrange(1)]

print [(i,j+k) for (k,j) in enumerate(xrange(3)) for i in xrange(j) for z in range(2)]

print "a".join(["a","b"])
"".join(set(["he", "oh"]))
"**".join({" oh":1, "he":0})


