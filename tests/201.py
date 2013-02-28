# unpacking negative integers
import struct
s = struct.pack('h', -12)
xx, = struct.unpack('h', s)
print xx
s = struct.pack('i', -13)
xx, = struct.unpack('i', s)
print xx
s = struct.pack('l', -14)
xx, = struct.unpack('l', s)
print xx
