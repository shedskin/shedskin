# !$!#$
try:
    [1].pop(-2)
except IndexError,e:
    print e
try:
    [].pop(0)
except IndexError,e:
    print e
try:
    [].remove(0)
except ValueError,e:
    print e
l = []
l.insert(4, 1)
l.insert(-1, 2)
l.insert(-10, 3)
print l
