# iteration

# TODO a, b = range(2)
# TODO x = range(8,20)[5]

# next

f = open('220.py')
for x in range(5):
    print(next(f))
print('extra', f.__next__())

file_iter = iter(f)
print('iter', next(file_iter))

aiter = iter(list(range(3)))
for i in range(5):
    print(next(aiter, -1))

aiter = iter(list(range(3)))
for i in range(2):
    print(next(aiter))

biter = iter('bla')
for i in range(5):
    print(next(biter, None))

# builtin funcs, now iterators in python3

filt = filter(lambda c: c>'a', 'abaaac')
print(str(filt).startswith('<filter object'), list(filt))

rev = reversed(range(10,20,2))
print('iterator' in str(rev), list(rev))

enum = enumerate('bananen')
print(str(enum).startswith('<enumerate object'), list(enum))

rrr = range(11,4,-2)
print(rrr)
print(list(rrr))

# zip

z1 = zip()
print(str(z1).startswith('<zip object'), list(z1))

z2 = zip([1,2])
print(str(z2).startswith('<zip object'), list(z2))

z3 = zip([1,2], [3,4])
print(str(z3).startswith('<zip object'), list(z3))

z4 = zip([1,2], [3,4], [5,6])
print(str(z4).startswith('<zip object'), list(z4))

# dict_items, dict_keys, dict_values
#print({1:2}.items())

# map

mp = map(lambda a: 2*a, [1,2,3])
print(str(mp).startswith('<map object'), list(mp))

mp = map(lambda a, b: a*b, [1,2,3], [4,5])
print(str(mp).startswith('<map object'), list(mp))

mp = map(lambda a, b, c: a+b+c, [1,2,3], [3,4,5], [5,4,3])
print(str(mp).startswith('<map object'), list(mp))

def hoppa2(a, b):
    if b: return a+b
    return a+'X'
print(list(map(hoppa2, 'banaan', 'aap')))

def hoppa3(a, b):
    if b: return a+b
    return a
print(list(map(hoppa3, range(8), range(4))))

print(list(map(max, ['a','bc'], ['d'], ['e'])))

print(list(map(set, [[1]])))
