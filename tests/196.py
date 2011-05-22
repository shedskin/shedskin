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
packer = struct.pack( 'HH' ,1 ,2 )
print repr(packer)
print struct.calcsize( 'HH' )
p0_0, p0_1, = struct.unpack( 'HH' ,packer)
print repr(p0_0), repr(p0_1),
print
packer = struct.pack( '!c3L2b3p' ,'\xd5' ,39 ,77 ,77 ,55 ,50 ,'\xf3\x8bq' )
print repr(packer)
print struct.calcsize( '!c3L2b3p' )
p1_0, p1_1, p1_2, p1_3, p1_4, p1_5, p1_6, = struct.unpack( '!c3L2b3p' ,packer)
print repr(p1_0), repr(p1_1), repr(p1_2), repr(p1_3), repr(p1_4), repr(p1_5), repr(p1_6),
print
packer = struct.pack( '!q2i2Q3H' ,91 ,62 ,118 ,45 ,113 ,72 ,117 ,92 )
print repr(packer)
print struct.calcsize( '!q2i2Q3H' )
p2_0, p2_1, p2_2, p2_3, p2_4, p2_5, p2_6, p2_7, = struct.unpack( '!q2i2Q3H' ,packer)
print repr(p2_0), repr(p2_1), repr(p2_2), repr(p2_3), repr(p2_4), repr(p2_5), repr(p2_6), repr(p2_7),
print
packer = struct.pack( '=2Ib3L3s' ,30 ,3 ,65 ,23 ,114 ,101 ,'\xc3\xcaZ' )
print repr(packer)
print struct.calcsize( '=2Ib3L3s' )
p3_0, p3_1, p3_2, p3_3, p3_4, p3_5, p3_6, = struct.unpack( '=2Ib3L3s' ,packer)
print repr(p3_0), repr(p3_1), repr(p3_2), repr(p3_3), repr(p3_4), repr(p3_5), repr(p3_6),
print
packer = struct.pack( '!3?2l' ,False ,False ,True ,75 ,39 )
print repr(packer)
print struct.calcsize( '!3?2l' )
p4_0, p4_1, p4_2, p4_3, p4_4, = struct.unpack( '!3?2l' ,packer)
print repr(p4_0), repr(p4_1), repr(p4_2), repr(p4_3), repr(p4_4),
print
packer = struct.pack( '3B3x2b' ,26 ,112 ,54 ,86 ,10 )
print repr(packer)
print struct.calcsize( '3B3x2b' )
p5_0, p5_1, p5_2, p5_3, p5_4, = struct.unpack( '3B3x2b' ,packer)
print repr(p5_0), repr(p5_1), repr(p5_2), repr(p5_3), repr(p5_4),
print
packer = struct.pack( '@3H3qs' ,67 ,14 ,69 ,12 ,66 ,91 ,'v' )
print repr(packer)
print struct.calcsize( '@3H3qs' )
p6_0, p6_1, p6_2, p6_3, p6_4, p6_5, p6_6, = struct.unpack( '@3H3qs' ,packer)
print repr(p6_0), repr(p6_1), repr(p6_2), repr(p6_3), repr(p6_4), repr(p6_5), repr(p6_6),
print
packer = struct.pack( 'I2qc2p' ,50 ,50 ,15 ,'\xd9' ,'\xb1\x06' )
print repr(packer)
print struct.calcsize( 'I2qc2p' )
p7_0, p7_1, p7_2, p7_3, p7_4, = struct.unpack( 'I2qc2p' ,packer)
print repr(p7_0), repr(p7_1), repr(p7_2), repr(p7_3), repr(p7_4),
print
packer = struct.pack( 'b2x2s' ,77 ,'\xa5~' )
print repr(packer)
print struct.calcsize( 'b2x2s' )
p8_0, p8_1, = struct.unpack( 'b2x2s' ,packer)
print repr(p8_0), repr(p8_1),
print
packer = struct.pack( 'Ip3si' ,60 ,'-' ,'t\xf5\x10' ,9 )
print repr(packer)
print struct.calcsize( 'Ip3si' )
p9_0, p9_1, p9_2, p9_3, = struct.unpack( 'Ip3si' ,packer)
print repr(p9_0), repr(p9_1), repr(p9_2), repr(p9_3),
print
packer = struct.pack( '<ibBx' ,82 ,108 ,61 )
print repr(packer)
print struct.calcsize( '<ibBx' )
p10_0, p10_1, p10_2, = struct.unpack( '<ibBx' ,packer)
print repr(p10_0), repr(p10_1), repr(p10_2),
print
packer = struct.pack( '!c3q2b3d' ,'\xd5' ,39 ,77 ,77 ,55 ,50 ,949.0 ,544.0 ,444.0 )
print repr(packer)
print struct.calcsize( '!c3q2b3d' )
p11_0, p11_1, p11_2, p11_3, p11_4, p11_5, p11_6, p11_7, p11_8, = struct.unpack( '!c3q2b3d' ,packer)
print repr(p11_0), repr(p11_1), repr(p11_2), repr(p11_3), repr(p11_4), repr(p11_5), repr(p11_6), repr(p11_7), repr(p11_8),
print
packer = struct.pack( 'l2Qc2d' ,50 ,50 ,15 ,'\xd9' ,692.0 ,24.0 )
print repr(packer)
print struct.calcsize( 'l2Qc2d' )
p12_0, p12_1, p12_2, p12_3, p12_4, p12_5, = struct.unpack( 'l2Qc2d' ,packer)
print repr(p12_0), repr(p12_1), repr(p12_2), repr(p12_3), repr(p12_4), repr(p12_5),
print
packer = struct.pack( '<0p0I' ,'' )
print repr(packer)
print struct.calcsize( '<0p0I' )
packer = struct.pack( '<3Q0s2B1i' ,64 ,117 ,20 ,'' ,48 ,38 ,50 )
print repr(packer)
print struct.calcsize( '<3Q0s2B1i' )
p14_0, p14_1, p14_2, p14_3, p14_4, p14_5, p14_6, = struct.unpack( '<3Q0s2B1i' ,packer)
print repr(p14_0), repr(p14_1), repr(p14_2), repr(p14_3), repr(p14_4), repr(p14_5), repr(p14_6),
print
packer = struct.pack( '<0L2f0p1x' ,682.0 ,307.0 ,'' )
print repr(packer)
print struct.calcsize( '<0L2f0p1x' )
packer = struct.pack( '=s' ,'\xe6\xc1\xdc\xb4y9\xa9' )
print repr(packer)
print struct.calcsize( '=s' )
p16_0, = struct.unpack( '=s' ,packer)
print repr(p16_0),
print
packer = struct.pack( '<3c3i3l2p' ,'\x84' ,'\xb7' ,'A' ,90 ,51 ,127 ,18 ,56 ,3 ,'\x82' )
print repr(packer)
print struct.calcsize( '<3c3i3l2p' )
p17_0, p17_1, p17_2, p17_3, p17_4, p17_5, p17_6, p17_7, p17_8, p17_9, = struct.unpack( '<3c3i3l2p' ,packer)
print repr(p17_0), repr(p17_1), repr(p17_2), repr(p17_3), repr(p17_4), repr(p17_5), repr(p17_6), repr(p17_7), repr(p17_8), repr(p17_9),
print
packer = struct.pack( '<0p3??' ,'\x85' ,False ,2 ,0 ,'huh' )
print repr(packer)
print struct.calcsize( '<0p3??' )
packer = struct.pack( '!c3pp1q' ,'\xe4' ,'1' ,'\xfeE\x9f\xdf`\x969\xdb' ,40 )
print repr(packer)
print struct.calcsize( '!c3pp1q' )
p19_0, p19_1, p19_2, p19_3, = struct.unpack( '!c3pp1q' ,packer)
print repr(p19_0), repr(p19_1), repr(p19_2), repr(p19_3),
print
packer = struct.pack( '!3s' ,'' )
print repr(packer)
print struct.calcsize( '!3s' )
p20_0, = struct.unpack( '!3s' ,packer)
print repr(p20_0),
print
packer = struct.pack( '@0q3x0p0d' ,'\x13\xe5\xb4\x98.\xff' )
print repr(packer)
print struct.calcsize( '@0q3x0p0d' )
packer = struct.pack( '0p2I?H' ,'\xe7\xa3\xd2' ,426 ,403 ,'hoi' ,85 )
print repr(packer)
print struct.calcsize( '0p2I?H' )
packer = struct.pack( '>0i0p3p2x' ,'g\xb0\x0c\x02\x89\xd3\xaf' ,'\xfdK\xb4\xb1\xf6l' )
print repr(packer)
print struct.calcsize( '>0i0p3p2x' )
packer = struct.pack( '>b0p2s' ,110 ,'\x1d' ,'' )
print repr(packer)
print struct.calcsize( '>b0p2s' )
packer = struct.pack( '@2f0p3p1L' ,531.0 ,469.0 ,'1k\x1a\x8c\xfd\xc0u\xdf' ,'' ,60 )
print repr(packer)
print struct.calcsize( '@2f0p3p1L' )
try:
    s = struct.pack('h', 18.18)
    print repr(s)
    dwah, = struct.unpack('h', s)
    print dwah
    s = struct.pack('h', '19')
    print repr(s)
    dwah, = struct.unpack('h', s)
    print dwah
    s = struct.pack('h', True)
    print repr(s)
    dwah, = struct.unpack('h', s)
    print dwah
except Exception, messg:
    print messg
try:
    s = struct.pack('fd', 17, 18)
    print repr(s)
    dwad, ewad = struct.unpack('fd', s)
    print dwad, ewad
    s = struct.pack('fd', 'oi', 18)
except Exception, e:
    print e
try:
    raise struct.error("butkus")
except struct.error, e:
    print e
booll, = struct.unpack('?', '\x02')
print booll
print repr(struct.pack('p', 300*'x'))

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
aahaa = array.array('i', range(5))
aahaa.extend(aahaa)
print aahaa

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

# sys vars
import sys
print sys.platform
print sys.byteorder
copyright = sys.copyright
assert (sys.version_info[0], sys.version_info[1]) >= (2, 4)
