
# basic string module support
import string
print string.join(['hello', 'world!']), string.join(['hello', 'world!'], '_')

# add random.shuffle
import random
l = [1,2,3,4,5]
random.shuffle(l)
print set(l)

# add __or__ to builtin.int..
class c: # grr
   def a(self):
       return 1|1
   def b(self):
       return 1&1
   def c(self):
       return 1^1
   def d(self):
       return ~1

a_c = c()
print a_c.a(), a_c.b(), a_c.c(), a_c.d()

# fake child nodes conflicting for binary tuples (e.g. one for unit and one for first)
class LowLevel:
   def comRxHeader(self):
       ('a', 'h')
       (7, 8)

bsl = LowLevel()
bsl.comRxHeader()

# self.mergeinh instead of self.merge XXX fix others
class LowLevel2:
   def bslTxRx(self, addr):
       addr % 2

class BootStrapLoader2(LowLevel2):
    pass

bsl2 = BootStrapLoader2()
bsl2.bslTxRx(0)

# improve parent constructor calls
class L:
    def __init__(self):
        pass

class BSL(L):
    def __init__(self, a, b):
        L.__init__(self)

BSL(1, 2)

# for/while-else construction
bla = True
while bla:
    for a in range(10):
        for b in range(10):
            pass
        else:
            print 'bah1'
        while bla:
            bla = False
            break
        else:
            print 'bah4'
        break
    else:
        print 'bah2'
else:
    print 'bah3'

# user-defined exception class problems
class MyException(Exception):
    pass

try:
    raise MyException('hoepa')
except MyException, m:
    print m

# parent constructor call and default arguments
class LowLevel3:
    def __init__(self, a=1):
        pass

class BootStrapLoader3(LowLevel3):
    def __init__(self):
        LowLevel3.__init__(self)

BootStrapLoader3()


