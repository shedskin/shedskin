import os

if os.path.exists("testdata"):
    testdata = "testdata"
elif os.path.exists("../testdata"):
    testdata = "../testdata"
else:
    testdata = "../../testdata"

datafile = os.path.join(testdata, 'hoppa')
outputfile = os.path.join(testdata, 'hoppa_write')


def test_open_for():
    f = open(datafile)
    assert [l for l in f] == ['hop\n', 'hop\n', 'hoppa!\n']
    f.close()

def test_open_read():
    f = open(datafile)
    assert f.read() == 'hop\nhop\nhoppa!\n'
    f.close()

def test_open_readlines():
    f = open(datafile)
    assert f.readlines() == ['hop\n', 'hop\n', 'hoppa!\n']
    f.close()

def test_with_open_read():
    with open(datafile) as f:
        assert f.read() == 'hop\nhop\nhoppa!\n'

# def test_open_read2():
#     with open("testdata/hoppa") as f:
#         words = f.read().split()
#         d = {}
#         res = []
#         for i, word in enumerate(words):
#             s = "".join(sorted(list(word.lower())))
#             d.setdefault(s, []).append(i)
#         for val in d.values():
#             if len(val) > 1:
#                 res.append([words[i] for i in val])
#     assert res == [['hop', 'hop']]


def test_open_write():
    f = open(outputfile, 'w')
    f.write('hop\nhop\nhoppa!\n')
    f.close()
    with open(outputfile) as g:
        assert g.read() == 'hop\nhop\nhoppa!\n'

def test_open_enter_exit():
    f = open(outputfile, 'w+')
    f.__enter__()
    f.write('hop\nhop\nhoppa!\n')
    f.seek(0)
    assert f.read() == 'hop\nhop\nhoppa!\n'
    f.__exit__()

# def test_with_open_write():
#     with open(outputfile, 'w') as f: # FIXME doesn't work
#         f.write('hop\nhop\nhoppa!\n')
#     with open(outputfile) as f:
#         assert f.read() == 'hop\nhop\nhoppa!\n'


# def test_lineendings():
#     cr_txt = "testdata/cr.txt"
#     lf_txt = "testdata/lf.txt"
#     crlf_txt = "testdata/crlf.txt"

#     with open(cr_txt, "w") as f1:
#         f1.write("hello world\r")
#         f1.write("bye\r")

#     with open(cr_txt, "r") as f2:
#         assert list(f2) == ["hello world\r", "bye\r"]

#     with open(lf_txt, "w") as f3:
#         f3.write("hello world\n")
#         f3.write("bye\n")

#     with open(lf_txt, "r") as f4:
#         assert list(f4) == ["hello world\n", "bye\n"]

#     with open(crlf_txt, "w") as f5:
#         f5.write("hello world\r\n")
#         f5.write("bye\r\n")

#     with open(crlf_txt, "r") as f6:
#         assert list(f6) == ["hello world\r\n", "bye\r\n"]


def test_all():
    test_open_for()
    test_open_read()
    # test_open_read2() # FIXME: fails
    test_open_readlines()
    test_with_open_read()
    test_open_write()
    test_open_enter_exit()
    # test_lineendings()

if __name__ == '__main__':
    test_all()

