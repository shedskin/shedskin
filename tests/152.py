
x = '0,0'
b = str(x)
print b

a = [[1]]
c = [None, [2]]

print a == c

d = [3]; d = None
e = [4]; e = None

print d == e, None == d, e == None, a == None, c[0] == None, c[1] == None

class board(object):
    def mergemask(self):
        print 'mergemask'

    def solve(self, board):
        global bekos
        bekos += 1

        #[board.mergemask() for x in range(1)] # XXX list(none) ..
        board.mergemask()
        board.mergemask()

bekos = 0
bo = board()
bo.solve(bo)

class heuk:
    aha = 4
    def bla(self):
        heuk.aha += 1
        self.ahah = 2
        print self.ahah, heuk.aha

h = heuk()
h.lala = 1
h.bla()

heuk.aha
heuk.aha += 1
print heuk.aha

heuk.noinit = 3
print heuk.noinit, h.ahah

class myiter:
    def __init__(self, container):
        self.container = container
        self.count = -1
    def next(self):
        self.count +=1
        if self.count < len(self.container):
            return self.container[self.count]
        raise StopIteration

class container:
    def __init__(self):
        self.unit = range(3)
    def __getitem__(self, i):
        return self.unit[i]
    def __iter__(self):
        return myiter(self)
    def __len__(self):
        return len(self.unit)

def iter_(x):
    return x.__iter__()

i = iter_(container())
try:
    while 1:
        y = i.next()
        print y
except StopIteration: pass

