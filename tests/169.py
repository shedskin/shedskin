
# --- assignment expressions
bweh = (2,[4,6])
[a, (b,c)] = bweh
print a,b,c
(a,b), (c,d) = (6,9), (8,7)
print a,b,c,d
[(a,b), (c,d)] = (9,8), (7,6)
print a,b,c,d
[(a,b), (c,d)] = [(1,8), (7,2)]
print a,b,c,d
[[a,b],c] = (5,6),3
print a,b,c
[[a,b],c] = [[4,5],6]
print a,b,c
a, [b,c] = [1, (2,3)]
print a,b,c
a, (b,c,d) = 1, (1,2,3)
print a,b,c,d
[(a,b), [c,d]] = [[1,2], (3,4)]
print a,b,c,d
njeh = [[8,7,6],[5,4,3],[2,1,0]]
[[a,b,c],[d,e,f],[g,h,i]] = njeh
print a,b,c,d,e,f,g,h,i
[dx,[a,b,c],ex] = njeh
print dx,a,b,c,ex
blah = (1,2,3,4,5,6)
a,b,c,d,e,f = blah
print a,b,c,d,e,f

# --- underscore in assignment
_ = 4
print _, _
#a, _ = 1, '2'
#huh = 1, 2
#_, b = huh
#mtx = [[1,2,3],[4,5,6],[6,7,8]]
#[du, [x, y, _], _] = mtx
#print du, x, y
#hop = [(1,(2,3))]
#for _ in hop: print 'hop'
#for _, (a,b) in hop: print 'hop', a, b
#for a, (_,b) in hop: print 'hop', a, b
#for a, _ in hop: print 'hop', a
#print ['hop' for _ in hop]
#print ['hop %d %d' % (a,b) for _, [a,b] in hop]
#print ['hop %d %d' % (a,b) for a, [_,b] in hop]
#print ['hop %d' % a for a, _ in hop]

# --- except 'tuple'
for a in range(2):
    try:
        if not a: assert 1 > 2, 'parasmurf'
        else: {1:2}[3]
    except (AssertionError, KeyError), m:
        print 'foutje3 of 4', m

# --- getopt.GetoptError test
import getopt
try:
    opts, args = getopt.getopt(['-x'], 'nf:', ['nowrap', 'flags='])
except getopt.GetoptError:
    print 'fout'


