
def test_set():
    s1 = set([1,2])
    s1.add(3)
    assert list(sorted(s1)) == [1,2,3]

if __name__ == '__main__':
    test_set()
