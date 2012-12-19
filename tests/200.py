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

#inheritance, generator expression
import array

class Common(object):
    CostScale = 7
    #StateTable = FsmGenerator().stateTable

    def __init__(self, inputStream, outputStream, options):
        lzpLowCount = 10
        self.lzpLow = array.array("H", (0xffb5 for _ in xrange(lzpLowCount)))

class Decoder(Common):
    def __init__(self, inputStream, outputStream, options):
        Common.__init__(self, inputStream, outputStream, options)

d = Decoder(None, None, None)
print d.lzpLow
