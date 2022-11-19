# overloading TODO support __iter__, __next__ combo?

class huppa:
    def __init__(self):
        self.count = 0

    def __str__(self):
        return 'huppa'

    def __bytes__(self):
        return b'huppa'

    def __truediv__(self, other):
        print('truediv')
        return self

    def __itruediv__(self, other):
        print('itruediv')
        return self

    def __floordiv__(self, other):
        print('floordiv')
        return self

    def __ifloordiv(self, other):
        print('ifloordiv')
        return self

h = huppa()
print(str(h))
print(bytes(h))
print(h/h)
print(h//h)

# next
f = open('220.py')
for x in range(5):
    print(next(f))
print('extra', f.__next__())

file_iter = iter(f)
print('iter', next(file_iter))

# TODO next second arg

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
#def hoppa2(a, b):
#    if b: return a+b
#    return a+'X'
#print(list(map(hoppa2, 'banaan', 'aap')))
#
#def hoppa3(a, b):
#    if b: return a+b
#    return a
#print(list(map(hoppa3, range(8), range(4))))
#
#print(list(map(max, ['a','bc'], ['d'], ['e'])))
#
#print(list(map(set, [[1]])))

# TODO check exception hierarchy

# TODO bytes: test all methods, also for str (sep test)

# TODO os.popen2 disappeared? check
#os.popen2 improvement
#import os
#child_stdin, child_stdout = os.popen2(["echo", "a  text"], "r")
#print(repr(child_stdout.read()))
#child_stdin, child_stdout = os.popen2(iter(["echo", "a  text"]), "r")
#print(repr(child_stdout.read()))
#child_stdin, child_stdout = os.popen2(("echo", "a  text"), "r")
#print(repr(child_stdout.read()))
#child_stdin, child_stdout = os.popen2("echo a  text", "r")
#print(repr(child_stdout.read()))

xx = b'\x00hoi\x00'
print(xx)
print(repr(xx))

print(bytes())
print(bytes([1,2,3]))
print(bytes(0))
print(bytes(4))
print(bytes(7))
print(bytes(b'hop'))
print(bytes(bytes(7)))
print(bytes(bytearray(7)))

print(bytearray())
print(bytearray([1,2,3]))
print(bytearray(0))
print(bytearray(4))
print(bytearray(7))
print(bytearray(b'hop'))
print(bytearray(bytearray(7)))
print(bytearray(bytes(7)))
