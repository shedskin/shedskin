import struct
fmt8755 = '@0p3xi'
print repr(fmt8755)
s = struct.pack(fmt8755,'\x13\xe5\xb4\x98.\xff', 18)
print repr(s)
