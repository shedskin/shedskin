
l = [(b,a) for a,b in enumerate([1,2,3])] # [list(tuple(int))]
print l                                  # [list(tuple(int))]

for a,b in enumerate([1.1,2.2,3.3]):     # [tuple2(int, float)]
    print 'huhu', a, '%.1f' % b                   # [str], [int], [float]

def bla():
    return ('1',2.2)                     # [tuple2(str, float)]

x,y = bla()                              # [tuple2(str, float)]
z,v = bla()                              # [tuple2(str, float)]

