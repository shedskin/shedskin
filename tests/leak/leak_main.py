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

    leak.test_list(range(100))
    leak.test_list(None)
    leak.test_list2([1.1, 2.2, 3.3])
    leak.test_list2(None)
    leak.test_list_nested([[1,2],None,[]])
    leak.test_list_nested(None)
    leak.test_dict({'hoi': 8.8, 'wa': 9.1})
    leak.test_dict(None)
    leak.test_set(set([1,2,3]))
    leak.test_set(None)
    leak.test_tuple((1,2,3))
    leak.test_tuple(None)
    leak.test_tuple2(('hoi', 8.9))
    leak.test_tuple2(None)
