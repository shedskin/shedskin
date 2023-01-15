class Sequence:
    def __init__(self, seq='wxyz'):
        self.seq = seq

    def __len__(self):
        return len(self.seq)

    def __getitem__(self, i):
        return self.seq[i]


class List:
    def __init__(self):
        self._list = []

    def append(self, x):
        self._list.append(x)

    def __getitem__(self, i):
        return self._list[i]



def test_seq():
    seq = Sequence()
    assert len(seq) == 4
    assert seq[0] == 'w'

def test_lst():
    lst = List()
    lst.append(1.0)
    assert lst[0] == 1.0


def test_all():
    test_seq()
    test_lst()

if __name__ == '__main__':
    test_all() 


