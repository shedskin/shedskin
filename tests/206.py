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

# unicode basics  # TODO non-ascii so run.py doesn't work
s = u'\u91cf\u5b50\u529b\u5b66'
print repr(s) #, s
t = s.encode('utf-8')
print repr(t) #, t
u = t.decode('utf-8')
print repr(u) #, u
l = [s, u]
print(l)
print repr(s[1]) #, s[1]
print len(s)

# some datetime tests
import datetime
print datetime.datetime.today().date()
