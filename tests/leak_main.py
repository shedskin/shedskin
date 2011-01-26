import leak
print leak.__file__

p = leak.Point()
while True:
    p.x
    p.y
    leak.test_float(4.4)
    leak.test_int(4)
    leak.test_str('beh')
