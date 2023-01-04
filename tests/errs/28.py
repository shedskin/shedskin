
import struct

fmt = 'HH'
c, d = struct.unpack(fmt+fmt, 'ntaoheu')
#*ERROR* 28.py:5: non-constant format string

