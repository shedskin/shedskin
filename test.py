import array
arr = array.array('i', [3,2,1])
print arr
print arr.tolist(), repr(arr.tostring())
print arr[0], arr[1], arr[2]
print sorted(arr)
arr2 = array.array('c')
arr2.extend('hoei')
print arr2, arr2.tolist(), arr2.tostring()
print arr2[0]
fla = array.array('d', (142344, 2384234))
print fla.typecode, fla.itemsize
print repr(fla.tostring()), ['%.2f' % flah for flah in fla.tolist()]
print '%.2f' % fla[1]
print 'hello, world!'

