import struct

a, = struct.unpack('i3', b'\x00' * 4)
#*ERROR* 80.py:3: repeat count given without format specifier
