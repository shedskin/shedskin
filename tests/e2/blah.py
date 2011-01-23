import memory

class meuk:
    def __init__(self):
        self.memory = 4

class CPU:
    def AND(self):
        print 'AND'
c = CPU()
c.AND()

def press(keys):
    print sorted(list(keys))
    print 'h' in keys
    print 'x' in keys
    print 'u' in keys
    print 'r' in keys

def hoppa(d):
    return d

if __name__ == '__main__':
    press(set('a'))
    print meuk().memory
    hoppa({'acht': 8.8})
