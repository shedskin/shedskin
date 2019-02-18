# check bounds after wrapping..
alist = range(5)
for i in range(-10,10):
    try:
        print alist[i], i
    except IndexError:
        print 'nope', i
try:
    print [][-1]
except IndexError:
    print 'nope..'

# fix examples/Gh0stenstein
px = 0xff << 24
print (px == 0xff000000)
