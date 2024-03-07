print('hello, world!')

import struct

bert = bytearray(10*b'-')
struct.pack_into('c', bert, 6, b'*')
struct.pack_into('c', bert, -8, b'*')
assert bert == b'--*---*---'

