
class Blah:
    def __init__(self, a, b):
        self.a, self.b = a, b

def woef(x):
    print x

class do:
    def __init__(self, public, do):
        self.public = public
        self.do = do

if __name__ == '__main__':
    blah = Blah(7, 'eight')
    woef(1)
    d = do('public', 'do')
