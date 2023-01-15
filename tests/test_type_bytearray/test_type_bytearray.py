
# bytearray


def test_bytearray():
    BLA = bytearray(b'bla')
    BA = bytearray(b'-')
    A = bytearray(b'a')
    B = bytearray(b'b')
    C = bytearray(b'c')

    assert BA.join([A, B, C]) == bytearray(b'a-b-c')
    assert BA.expandtabs() == bytearray(b'-')
    assert BA.upper() == bytearray(b'-')
    assert BA.lower() == bytearray(b'-')
    assert BA.replace(A, B) == bytearray(b'-')
    assert BA.swapcase() == bytearray(b'-')
    assert BA.split() == [bytearray(b'-')]
    assert BA.rsplit() == [bytearray(b'-')]
    assert BA.strip() == bytearray(b'-')
    assert BA.lstrip() == bytearray(b'-')
    assert BA.rstrip() == bytearray(b'-')
    assert BA.center(10) == bytearray(b'    -     ')
    assert bytearray(b'-').zfill(10) == bytearray(b'-000000000')
    assert BA.ljust(10) == bytearray(b'-         ')
    assert BA.rjust(10) == bytearray(b'         -')
    assert BA.title() == bytearray(b'-')
    assert BA.capitalize() == bytearray(b'-')
    assert BA.splitlines() == [bytearray(b'-')]
    assert BLA.partition(A)
    assert BLA.rpartition(B)
    assert BLA[1] == ord('l')
    assert BLA[1:] == bytearray(b'la')
    assert BLA[::-1] == bytearray(b'alb')
    assert BLA+BLA == bytearray(b'blabla')
    assert 3*BLA == bytearray(b'blablabla')
    assert BLA*3 == bytearray(b'blablabla')

def test_bytearray_clear():
    ba = bytearray(b'bla')
    ba.clear()
    assert ba == bytearray(b'')

def test_bytearray_getitem():
    ba = bytearray(b'bla')
    assert ba[1] == ord('l')

def test_bytearray_append():
    ba = bytearray(b'bla')
    ba.append(81)
    ba.append(187)
    assert ba == bytearray(b'blaQ\xbb')

def test_bytearray_del():
    ba = bytearray(b'bla')
    del ba[1]
    assert ba == bytearray(b'ba')
    del ba[-2]
    assert ba == bytearray(b'a')

def test_bytearray_copy():
    ba = bytearray(b'bla')
    ba.copy() == bytearray(b'bla')

def test_bytearray_concat():
    ba = bytearray(b'bla')
    assert 2*ba == bytearray(b'blabla')
    assert ba*2 == bytearray(b'blabla')
    assert ba+ba == bytearray(b'blabla')

def test_bytearray_pop():
    ba = bytearray(b'bla')
    assert ba.pop(0) == ord('b')
    assert ba.pop() == ord('a')
    assert ba == bytearray(b'l')

def test_bytearray_extend():
    ba = bytearray(b'bla')
    BA = bytearray(b'-')
    ba.extend([1,2])
    assert ba == bytearray(b'bla\x01\x02')
    ba.extend(b'ab')
    assert ba == bytearray(b'bla\x01\x02ab')
    ba.extend(BA)
    assert ba == bytearray(b'bla\x01\x02ab-')

def test_bytearray_reverse():
    ba = bytearray(b'bla')
    ba.reverse()
    assert ba == bytearray(b'alb')

def test_bytearray_remove():
    ba = bytearray(b'bla')
    ba.remove(ord('l'))
    assert ba == bytearray(b'ba')

def test_bytearray_addition_assign():
    ba = bytearray(b'bla')
    A = bytearray(b'a')
    B = bytearray(b'b')
    ba += A + B
    assert ba == bytearray(b'blaab')
    ba *= 2
    assert ba == bytearray(b'blaabblaab')

def test_bytearray_insert():
    ba = bytearray(b'bla')
    ba.insert(1, ord('u'))
    assert ba == bytearray(b'bula')
    ba.insert(-2, ord('w'))
    assert ba == bytearray(b'buwla')

# def test_bytearray_hash():
#     try:
#         h = hash(bytearray(b'bla'))
#     except TypeError:
#         print('bytearray unhashable')

def test_bytearray_slice():
    ba = bytearray(b'blablabla')
    BLA = bytearray(b'bla')
    ba[1:4] = [ord('c'), ord('d')]
    assert ba ==  bytearray(b'bcdlabla')
    ba[1:4] = BLA
    assert ba == bytearray(b'bblaabla')
    del ba[::2]
    assert ba == bytearray(b'baba')

def test_bytearray_misc():
    assert bytearray() == bytearray(b'')
    assert bytearray([1, 2, 3]) == bytearray(b'\x01\x02\x03')
    assert bytearray(0) == bytearray(b'')
    assert bytearray(4) == bytearray(b'\x00\x00\x00\x00')
    assert bytearray(7) == bytearray(b'\x00\x00\x00\x00\x00\x00\x00')
    assert bytearray(b"hop") == bytearray(b'hop')
    assert bytearray(bytearray(7)) == bytearray(b'\x00\x00\x00\x00\x00\x00\x00')
    assert bytearray(bytes(7)) == bytearray(b'\x00\x00\x00\x00\x00\x00\x00')
    assert b"hop %s" % bytearray(b"hup") == b'hop hup'
    assert list(bytearray(4)) == [0,0,0,0]

def test_all():
    test_bytearray()
    test_bytearray_clear()
    test_bytearray_append()
    test_bytearray_del()
    test_bytearray_copy()
    test_bytearray_getitem()
    test_bytearray_concat()
    test_bytearray_pop()
    test_bytearray_extend()
    test_bytearray_reverse()
    test_bytearray_remove()
    test_bytearray_addition_assign()
    test_bytearray_insert()
    # test_bytearray_hash()
    test_bytearray_slice()
    test_bytearray_misc()

if __name__ == "__main__":
    test_all()

