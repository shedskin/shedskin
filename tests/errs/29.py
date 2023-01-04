import struct

a, = struct.unpack('y', 'tnohu')
#*ERROR* 29.py:3: bad or unsupported char in struct format: 'y'

