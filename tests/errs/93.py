class A:
    @classmethod
    def make(cls):
        return cls()

print(A.make())

#*ERROR* 93.py:2: unsupported type of decorator
