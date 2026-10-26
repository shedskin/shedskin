import struct

a, b, c = struct.unpack('3 i', b'\x00' * 12)
#*ERROR* 81.py:3: bad or unsupported char in struct format: ' '
