# overloading

# TODO
# __div__ -> __truediv__, __floordiv__
# __bytes__
# __next__?

# generators

# reversed(range)
#print(reversed(range(10,20,2)))

# TODO support slice objects??
#ar = list(range(10))
#ar.__delitem__(slice(1,4))
#print(ar)

# now iterators: dict_items, dict_keys, dict_values, like reversed, enumerate, itertools.imap?
#print({1:2}.items())

# different length args to map
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

