
class integer: pass

class fred:
    def __add__(self, x):
        i = integer()
        return i

def hoei():
    a = fred()
    return a+a

a = hoei()

