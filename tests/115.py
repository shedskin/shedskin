
d = (1, (1.1, 'u'))

a, (b, c) = d
e, f = d


for x,(y,z) in [d]:
    x
    y
    z

l = [((v,u),w) for u,(v,w) in [d]]
print 'uh', '%.2f %d' % l[0][0], l[0][1], len(l)


