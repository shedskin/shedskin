from __future__ import print_function

# template not removed after iteration
class BadError(Exception):
    pass

if __name__=='__main__':
    BadError()
    BadError("AOE")

# crash in assign_needs_cast XXX try self.method() instead of self.msg!
class MyBaseException:
    def __init__(self, msg=None):
        self.msg = msg
class MyException(MyBaseException): pass
class MyStandardError(MyException): pass
class MyBadError(MyException):
    pass

if __name__=='__main__':
    MyStandardError()
    MyBadError()

# default hash method
class waf(object):
    pass

w = waf()
print(hash(w) - hash(w))

# delslice bug
all = list(range(10))
print(all[2:8:2])
all[1:3] = list(range(5))
print(all)
del all[1:7:2]
print(all)

# OMG
omg, = (17,)
print(omg)

# sys vars
import sys
print(sys.platform.strip('2'))
print(sys.byteorder)
copyright = sys.copyright
assert (sys.version_info[0], sys.version_info[1]) >= (2, 4)

# str.title
print('8RMgvsFN51QrM0sJeXU11yXodq1drv'.title())

# forward referencing base class doesn't work
import testdata.timer
class smurf (testdata.timer.TimingOut):
    def __init__(self):
        testdata.timer.TimingOut.fire_timer(self)
smurfje = smurf()
testdata.timer.timeout_add(42, smurfje)

# file.xreadlines (deprecated but still)
lines = open('testdata/crap.py','r').readlines()
for line in lines:
    print(line.strip())

# bin() limited to 12 digits
print(bin(123456789))

# sys.exit case
import sys
sys.exit()
