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
print repr(struct.pack('!c3L2b3p','\xd5',39,77,77,55,50,'\xf3\x8bq'))
print repr(struct.pack('!q2i2Q3H',91,62,118,45,113,72,117,92))
print repr(struct.pack('=2Ib3L3s',30,3,65,23,114,101,'\xc3\xcaZ'))
print repr(struct.pack('!3?2l',False,False,True,75,39))
print repr(struct.pack('3B3x2b',26,112,54,86,10))
print repr(struct.pack('@3H3qs',67,14,69,12,66,91,'v'))
print repr(struct.pack('I2qc2p',50,50,15,'\xd9','\xb1\x06'))
print repr(struct.pack('b2x2s',77,'\xa5~'))
print repr(struct.pack('Ip3si',60,'-','t\xf5\x10',9))
print repr(struct.pack('<ibBx',82,108,61))
print repr(struct.pack('!c3q2b3d','\xd5',39,77,77,55,50,949.0,544.0,444.0))
print repr(struct.pack('l2Qc2d',50,50,15,'\xd9',692.0,24.0))
print repr(struct.pack('<0p0I',''))
print repr(struct.pack('<3Q0s2B1i',64,117,20,'',48,38,50))
print repr(struct.pack('<0L2f0p1x',682.0,307.0,''))
print repr(struct.pack('=s','\xe6\xc1\xdc\xb4y9\xa9'))
print repr(struct.pack('<3c3i3l2p','\x84','\xb7','A',90,51,127,18,56,3,'\x82'))
print repr(struct.pack('<0p3??','\x85',False,2,0,'huh'))

# array
import array
arr = array.array('i', [3,2,1])
print arr
print arr.tolist(), repr(arr.tostring())
print arr[0], arr[1], arr[2]
arr.fromlist([4,5])
print sorted(arr)
arr2 = array.array('c')
arr2.extend('hoei')
print arr2.count('h'), arr2.index('h')
arr2[-1] = 'X'
arr2.insert(0, '-')
arr2.fromlist(['a', 'b'])
print arr2, arr2.tolist(), arr2.tostring()
print arr2[0]
fla = array.array('f', [3.141])
fla = array.array('d', (142344, 2384234))
fla.fromlist([1234,])
fla[0] = 28000
print fla.typecode, fla.itemsize
print repr(fla.tostring()), ['%.2f' % flah for flah in fla.tolist()]
print '%.2f' % fla[1]
print repr(fla)
arr3 = array.array('i')
arr3.fromstring(arr.tostring())
print arr, arr3
areq = (arr==arr3)
print areq
arradd = arr+arr
print arradd
beh = arr
arr += arr
print arr
print beh
mul1 = arr * 2
mul2 = 2 * arr
print mul1, mul2
wah = mul1
mul1 *= 2
print mul1
print wah
boolt = wah.__contains__(5), 6 in wah
print boolt
print len(wah), wah.count(5), wah.index(5)
print wah.pop(4)
print wah.pop()
print wah.pop(-2)
print wah
wah.remove(5)
print wah
print wah[-2]
wah.reverse()
print wah
wah.byteswap()
print wah
wah[3] = 99
print wah
wah.insert(7, 98)
print wah
arr4 = array.array('i', [3,2,1])
print arr4
f = open('testdata/blabla', 'w')
arr4.tofile(f)
f.close()
arr5 = array.array('i')
f = open('testdata/blabla')
arr5.fromfile(f, 2)
try:
    arr5.fromfile(f, 2)
except EOFError, e:
    print e
f.close()
print arr5
import copy
arr = array.array('i', [3,2,1])
c1 = copy.copy(arr)
c1.append(4)
c2 = copy.deepcopy(arr)
c2.append(5)
print c1, c2, arr
arra = array.array('i', [1,2])
arrb = array.array('i', [1,2,3])
print arra == arrb, arra > arrb, arra < arrb, cmp(arra, arrb) # XXX compare with non-arrays
del arrb[1]
del arrb[-1]
print arrb
allr = array.array('H', range(10))
print allr
print allr[2:8:2]
allr[1:3] = array.array('H', range(5))
print allr
del allr[1:7:2]
print allr

# binascii
import binascii
str = 'my guitar wants to strum all night long'

#b2a = binascii.b2a_qp(str)
#print repr(b2a)
#a2b = binascii.a2b_qp(b2a)
#print repr(a2b)

b2a = binascii.b2a_uu(str)
print repr(b2a)
a2b = binascii.a2b_uu(b2a)
print repr(a2b)

b2a = binascii.b2a_hex(str)
print repr(b2a)
a2b = binascii.a2b_hex(b2a)
print repr(a2b)

b2a = binascii.b2a_hqx(str)
print repr(b2a)
#a2b = binascii.a2b_hqx(b2a)
#print repr(a2b)

b2a = binascii.b2a_base64(str)
print repr(b2a)
a2b = binascii.a2b_base64(b2a)
print repr(a2b)

b2a = binascii.rlecode_hqx(str)
print repr(b2a)
a2b = binascii.rledecode_hqx(b2a)
print repr(a2b)

b2a = binascii.hexlify(str)
print repr(b2a)
a2b = binascii.unhexlify(b2a)
print repr(a2b)

# delslice bug
all = range(10)
print all[2:8:2]
all[1:3] = range(5)
print all
del all[1:7:2]
print all

# OMG
omg, = (17,)
print omg
