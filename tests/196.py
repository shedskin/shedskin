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
print hash(w) - hash(w)

# struct
import struct
from struct import unpack
b1, b2, h1, h2, h3, i1, i2, s1 = unpack("<BBHHHII16s", 32*'0')
print b1, b2, h1, h2, h3, i1, i2, s1
header_format = "<32s2BHHH24s"
s1, b1, b2, h1, h2, h3, s2 = struct.unpack(header_format, 64*'0')
print s1, b1, b2, h1, h2, h3, s2
print struct.calcsize(header_format)
class woef:
    def __init__(self):
        header_format = "<32s2BHHH24s"
        version = [0,0]
        magic, version[0], version[1], max_files, self.cur_files, reserved, user_description = struct.unpack(header_format, 64*'0')
        print magic, version, self.cur_files
woef()
print repr(struct.pack('HH', 1, 2))

# array
import array
arr = array.array('i', [3,2,1])
print arr
print arr.tolist()
print arr[0], arr[1], arr[2]
print sorted(arr)
arr2 = array.array('c')
arr2.extend('hoei')
print arr2, arr2.tostring()
fla = array.array('d', (142344, 2384234))
print fla.typecode, fla.itemsize
print repr(fla.tostring())
