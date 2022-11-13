# binascii

import binascii
str = b'my guitar wants to strum all night long'

b2a = binascii.b2a_qp(str)
print(repr(b2a))
a2b = binascii.a2b_qp(b2a)
print(repr(a2b))

b2a = binascii.b2a_uu(str)
print(repr(b2a))
a2b = binascii.a2b_uu(b2a)
print(repr(a2b))

b2a = binascii.b2a_hex(str)
print(repr(b2a))
a2b = binascii.a2b_hex(b2a)
print(repr(a2b))

b2a = binascii.b2a_hqx(str)
print(repr(b2a))
a2b,done = binascii.a2b_hqx(b2a) # returns a string instead of a tuple
print(repr(a2b),done)

b2a = binascii.b2a_base64(str)
print(repr(b2a))
a2b = binascii.a2b_base64(b2a)
print(repr(a2b))

b2a = binascii.rlecode_hqx(str)
print(repr(b2a))
a2b = binascii.rledecode_hqx(b2a)
print(repr(a2b))

b2a = binascii.hexlify(str)
print(repr(b2a))
a2b = binascii.unhexlify(b2a)
print(repr(a2b))
