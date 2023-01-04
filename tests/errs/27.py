import struct

fmt = 'HH'
fmt = 'ii'
a, b = struct.unpack(fmt, 'tnaoheu')

#*ERROR* 27.py:5: non-constant format string
