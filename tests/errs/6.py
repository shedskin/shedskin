class AA:
    def __init__(self, x):
        if x == 1:
            self.a = AA(0)
            self.b = AA(0)
    def __del__(self):
        pass
    def __iter__(self):
        pass
    def __call__(self):
        pass
aa = AA(1)
gg = {1:2,3:4,5:7}
del aa.a, aa.b, gg[1], gg[5]
print(gg)

class meuh:
    attr = 4
    def __init__(self):
        b = self.attr
#        self.attr = 2 XXX add warning
meuh()
meuh().attr

import struct
data = 'data'
unpacked = struct.unpack('<I', data)[0]
struct.unpack('<I', data)
tuple_unpacked = struct.unpack('<I', data)

class wafwaf:
    x = 1

class wof(wafwaf):
    def hap(self):
        self.x

wof().hap()

#*WARNING* 6.py:6: '__del__' is not supported
#*WARNING* 6.py:8: '__iter__' is not supported
#*WARNING* 6.py:10: '__call__' is not supported
#*WARNING* 6.py:14: 'del' has no effect without refcounting
#*WARNING* 6.py:20: class attribute 'attr' accessed without using class name
#*WARNING* 6.py:23: class attribute 'attr' accessed without using class name
#*WARNING* 6.py:36: class attribute 'x' accessed without using class name
#*WARNING* 6.py:27: struct.unpack should be used as follows: 'a, .. = struct.unpack(..)'
#*WARNING* 6.py:28: struct.unpack should be used as follows: 'a, .. = struct.unpack(..)'
#*WARNING* 6.py:29: struct.unpack should be used as follows: 'a, .. = struct.unpack(..)'
