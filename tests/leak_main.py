import leak
print leak.__file__

p = leak.Point()
while True:
    p.x
    p.y
    p.s
    p.n
    leak.test_float(4.4)
    leak.test_int(4)
    leak.test_str('beh')
    leak.test_str(None)

    for q in leak.points:
        q.x
