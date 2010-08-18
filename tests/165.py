
print 1, 2, '3', '%.2f' % 4.1
print '%04x' % 0xfeda

# '..' % (..)
print '%d %x %d' % (10, 11, 12)
print '%d %s' % (1, 'een')
print '%d %s %.2f' % (1, 'een', 8.1)

# '..' % tuple
t = (10, 11, 12)
print '%x %d %x' % t
t2 = ('twee', 2)
print '%s %04x' % t2

# mod
a = '%04x' % 0xdefa
print a, a, '%02x' % 0x1234

# all chars
print '%o' % 10
print "%.4s %.4r\n" % ("abcdefg", "\0hoplakee")

# print to file
f = file('testdata/binf', 'w')
print >>f, 'ik haat %04x\n' % 0xfeda, 'smurven..\n'
f.close()

# conversions
print repr('?%% %c?' % 70), repr('?%c?%%' % 0), '%c' % 'X'
print '!%s!' % [1,2,3]
print '%.2f %d %.2f %d' % (4, 4.4, 5.5, 5)
print '%s.' % 1, '%s.' % (1,)

# %s, %r
print repr(18), repr('x')
print 'aha %s %r' % (18, 19)

# class file
f = file('testdata/hopsakee')
print 1, f.readline(),
print f.readline(5)
print f.readline(),
f.close()

print 2, file('testdata/hopsakee').read()

print 3, file('testdata/hopsakee').readlines()

for line in file('testdata/hopsakee'):
    print 'aha', line,



