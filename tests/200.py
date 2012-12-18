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

#null char
print 'hello\0world'
print repr('hello\0world')
print repr('woef%swaf' % 'waaa\0wa')
print repr('woef%swaf%s!' % ('waaa\0wa\0wa', '\0haaap'))
