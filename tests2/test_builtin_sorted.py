
a = [
    (2, 3),
    (3, 2),
    (),
    (2,),
    (3, 4, 5),
    (2, 2),
    (1, 4),
    (4, 1),
    (4, 2),
    (4, 3),
    (3, 4),
    (4, 4),
    (4, 5),
    (1, 5),
    (1, 20),
    (20, 1),
    (20, 2),
]

a_sorted = [
 (),
 (1, 4),
 (1, 5),
 (1, 20),
 (2,),
 (2, 2),
 (2, 3),
 (3, 2),
 (3, 4),
 (3, 4, 5),
 (4, 1),
 (4, 2),
 (4, 3),
 (4, 4),
 (4, 5),
 (20, 1),
 (20, 2)]


def test_sorted1():
    assert list(sorted(a)) == a_sorted


def test_sorted2():
    b = [[3, 2], [1, 3]]
    assert list(sorted(b)) == [[1, 3], [3, 2]]

def test_sorted3():
    c = ["b", "c", "aa"]
    assert list(sorted(c)) == ['aa', 'b', 'c']



def test_all():
    test_sorted1()
    test_sorted2()
    test_sorted3()

if __name__ == '__main__':
    test_all()

