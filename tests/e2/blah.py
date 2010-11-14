
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

if __name__ == '__main__':
    press(set('a'))
