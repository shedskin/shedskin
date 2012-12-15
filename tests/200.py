#select.select
import os
import select
f = os.popen("ls", "r")
rFDs, wFDs, xFDs = select.select((), [], set(), 0)
rFDs, wFDs, xFDs = select.select([f.fileno()], set(), [], 20)
print len(rFDs), len(wFDs), len(xFDs)

#time crashes without args
import time
print time.asctime()[:10]
print str(time.localtime())[:50]

#don't crash, keep going
class Lg2(object):
    lgLut = [-1]
    for i in xrange(1, 256):
        lgLut.append(1 + lgLut[i / 2])
lgLut = Lg2.lgLut
print lgLut[:10]
