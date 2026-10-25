import struct

data = struct.pack('bi', 1, 2)
a, b, c = struct.unpack_from('bi', data)

#*ERROR* 79.py:4: not enough values to unpack (expected 3, got 2)
