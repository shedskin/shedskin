from __future__ import print_function

# optional start/end arguments for str.{count, startswith, endswith}

def hop(b):
    if b: print(1)
    else: print(0)

hop('hoi'.startswith('ho', 0))
hop('hoi'.startswith('ho', 0, 3))
hop('hoi'.startswith('ho', 0, -1))
hop('hoi'.endswith('oi'))
hop('hoi'.endswith('oi', 0, 3))
hop('hoi'.endswith('ho', 0, -1))
hop('hoi'.endswith('ho', -3, 2))
hop('hoi'.startswith(':', 3))
hop('hoi:'.startswith(':', 3))

print('hoooi'.count('o'))
print('hoooi'.count('o', 2))
print('hoooi'.count('o', 0, -2))

# mother contour (6,5) -> (1,1) instead of (1,5)
def getopt(args, longopts):
    opts = []
    opts.append(('',))

    do_longs(opts, longopts)

def do_longs(opts, longopts):
    [o for o in longopts]

wa = ['']

getopt(wa, wa)

s = open('testdata/hopsakee')
print(s.name)
print(s.mode)
print(s.read())

f = open('testdata/hopsakee')
print(f.read())
f.seek(0)
print(f.read())
f.close()

