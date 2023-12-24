import array


def test_array1():
    arr = array.array("i", [3, 2, 1])
    assert arr.typecode == "i"
    assert sorted(arr) == [1, 2, 3]
    assert arr.tolist() == [3, 2, 1]
    assert arr.tobytes() == b'\x03\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00'
    assert arr[0] == 3
    assert arr[1] == 2
    assert arr[2] == 1

def test_array2():
    f1 = array.array("f", [3.141])
    f2 = array.array("d", (142344, 2384234))
    assert f1.typecode == "f"
    assert f2.typecode == "d"

def test_array3():
    arr = array.array("B")
    arr.extend(list(range(20)))
    assert arr == array.array('B', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    assert arr[:] == array.array('B', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    assert arr[-7:] == array.array('B', [13, 14, 15, 16, 17, 18, 19])
    assert arr[-7::2] == array.array('B', [13, 15, 17, 19])
    assert arr[:8:3] == array.array('B', [0, 3, 6])
    assert arr[15:1:-2] == array.array('B', [15, 13, 11, 9, 7, 5, 3])


# def test_array4():
    # fla.fromlist(
    #     [
    #         1234,
    #     ]
    # )
    # fla[0] = 28000
    # print(fla.typecode, fla.itemsize)
    # print(repr(fla.tobytes()), ["%.2f" % flah for flah in fla.tolist()])
    # print("%.2f" % fla[1])
    # print(repr(fla))
    # arr3 = array.array("i")
    # arr3.frombytes(arr.tobytes())
    # print(arr, arr3)
    # areq = arr == arr3
    # print(areq)
    # arradd = arr + arr
    # print(arradd)
    # beh = arr
    # arr += arr
    # print(arr)
    # print(beh)
    # mul1 = arr * 4
    # mul2 = 3 * arr
    # print(mul1, mul2)
    # wah = mul1
    # mul1 *= 1
    # print(mul1)
    # print(wah)
    # boolt = wah.__contains__(5), 6 in wah
    # print(boolt)
    # print(len(wah), wah.count(5), wah.index(5))
    # print(wah.pop(4))
    # print(wah.pop())
    # print(wah.pop(-2))
    # print(wah)
    # wah.remove(5)
    # print(wah)
    # print(wah[-2])
    # wah.reverse()
    # print(wah)
    # wah.byteswap()
    # print(wah)
    # wah[3] = 99
    # print(wah)
    # wah.insert(7, 98)
    # print(wah)
    # arr4 = array.array("i", [3, 2, 1])
    # print(arr4)
    # f = open("testdata/blabla", "wb")
    # arr4.tofile(f)
    # f.close()
    # arr5 = array.array("i")
    # f = open("testdata/blabla", "rb")
    # arr5.fromfile(f, 2)
    # try:
    #     arr5.fromfile(f, 2)
    # except EOFError as e:
    #     print(e)
    # f.close()
    # print(arr5)
    # import copy

    # arr = array.array("i", [3, 2, 1])
    # c1 = copy.copy(arr)
    # c1.append(4)
    # c2 = copy.deepcopy(arr)
    # c2.append(5)
    # print(c1, c2, arr)
    # arra = array.array("i", [1, 2])
    # arrb = array.array("i", [1, 2, 3])
    # print(arra == arrb, arra > arrb, arra < arrb)
    # del arrb[1]
    # del arrb[-1]
    # print(arrb)
    # allr = array.array("H", list(range(10)))
    # print(allr)
    # print(allr[2:8:2])
    # allr[1:3] = array.array("H", list(range(5)))
    # print(allr)
    # del allr[1:7:2]
    # print(allr)
    # aahaa = array.array("i", list(range(5)))
    # aahaa.extend(aahaa)
    # print(aahaa)
    # arghx = array.array("i", list(range(5)))
    # arghy = array.array("h", list(range(5)))
    # print(arghx == arghy)
    # arghy.append(7)
    # print(arghx == arghy)



def test_all():
    test_array1()
    test_array2()
    test_array3()

if __name__ == '__main__':
    test_all() 


