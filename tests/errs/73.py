class Money:
    def __init__(self, cents):
        self.cents = cents
    def __format__(self, spec):
        return '$%d.%02d' % (self.cents // 100, self.cents % 100)

print(format(Money(150)), f'{Money(5)}')

#*WARNING* 73.py:4: '__format__' is not supported
