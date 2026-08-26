
class Registry:
    def __init__(self):
        self.count = 0
    def setter(self, func):
        self.count += 1
        return func

reg = Registry()

class Thing:
    @reg.setter
    def configure(self, value):
        return value * 2

#*ERROR* 48.py:12: unsupported type of decorator
