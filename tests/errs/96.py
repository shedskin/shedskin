class A:
    def __init__(self):
        self.x = 1

    def f(self):
        return self.x

class C:
    def __init__(self):
        self.x = 2

print(A.f(C()))

#*ERROR* 96.py:12: unsupported call 'A.f(..)' with argument of type 'C'
