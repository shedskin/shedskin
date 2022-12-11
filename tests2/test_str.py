class Sequence:
    def __init__(self, seq='wxyz'):
        self.seq = seq

    def __len__(self):
        return len(self.seq)

    def __getitem__(self, i):
        return self.seq[i]

def test_str():
    s = Sequence()
    assert len(s) == 4
    assert s[0] == 'w'

if __name__ == '__main__':
    test_str()