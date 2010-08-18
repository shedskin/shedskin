
print 'hello, world!'

for x in range(10,14):                   # [list(int)]
    print x**3                           # [int]

y = 'luis'                               # [str]
for i in y:                              # [str]
    print i                              # [str]

print [i*2 for i in 'luis']              # [list(str)]

f = open('testdata/hoppa')                        # [file]
print 'lc', [l for l in f]               # [str], [list(str)]
f.close()                                # []

f = open('testdata/hoppa')                        # [file]
print 'read', f.read()                   # [str], [str]
f.close()                                # []

f = file('testdata/hoppa')                        # [file]
print 'lines', f.readlines()             # [str], [list(str)]
f.close()                                # []

conv = {"A": 0, "B": 1}                  # [dict(str, int)]
print conv["A"], conv["B"]               # [int], [int]

print [{"A": 0, "B": 1}[c] for c in "ABABABA"] # [list(int)]

