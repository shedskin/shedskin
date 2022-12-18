
# for x in range(10,14):                   # [list(int)]
#     print(x**3)                           # [int]

# y = 'luis'                               # [str]
# for i in y:                              # [str]
#     print(i)                              # [str]

# print([i*2 for i in 'luis'])             # [list(str)]


# conv = {"A": 0, "B": 1}                  # [dict(str, int)]
# print(conv["A"], conv["B"])               # [int], [int]

# print([{"A": 0, "B": 1}[c] for c in "ABABABA"]) # [list(int)]

def test_open_for():
    f = open('testdata/hoppa')
    assert [l for l in f] == ['hop\n', 'hop\n', 'hoppa!\n']
    f.close()

def test_open_read():
    f = open('testdata/hoppa')
    assert f.read() == 'hop\nhop\nhoppa!\n'
    f.close()

def test_open_readlines():
    f = open('testdata/hoppa')
    assert f.readlines() == ['hop\n', 'hop\n', 'hoppa!\n']
    f.close()

def test_with_open_read():
    with open('testdata/hoppa') as f:
        assert f.read() == 'hop\nhop\nhoppa!\n'

def test_open_write():
    f = open('testdata/hoppa_write', 'w')
    f.write('hop\nhop\nhoppa!\n')
    f.close()
    with open('testdata/hoppa_write') as g:
        assert g.read() == 'hop\nhop\nhoppa!\n'

# def test_with_open_write():
#     with open('testdata/hoppa_write', 'w') as f: # FIXME doesn't work
#         f.write('hop\nhop\nhoppa!\n')
#     with open('testdata/hoppa_write') as f:
#         assert f.read() == 'hop\nhop\nhoppa!\n'


def test_all():
    test_open_for()
    test_open_read()
    test_open_readlines()
    test_with_open_read()
    test_open_write()

if __name__ == '__main__':
    test_all()

