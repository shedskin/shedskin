import memory

class NotExported(Exception):
    pass

class meuk:
    def __init__(self):
        self.memory = 4

class CPU:
    def AND(self):
        return 'AND'
c = CPU()

def press(keys):
    return sorted(list(keys))

def press2(keys):
    return ('h' in keys, 'x' in keys, 'u' in keys, 'r' in keys)

def hoppa(d):
    return d

if __name__ == '__main__':
    c.AND()
    press(set('a'))
    press2(set('a'))
    print meuk().memory
    hoppa({'acht': 8.8})
    NotExported()
