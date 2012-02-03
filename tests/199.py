# set.__ior__ etc. model
class waf:
    def __init__(self, value):
        self.value = value

    def __iand__(self, b):
        return waf(self.value + b.value)

    def __isub__(self, b):
        return waf(self.value - b.value)

wa = waf(4)
wa &= waf(9)
wa -= waf(2)
print wa.value

set1 = set()
set1 |= set([2,3])
print set1

set2 = set()
set2 &= set([2,3])
print set2

set3 = set()
set3 ^= set([2,3])
print set3

set4 = set()
set4 -= set([2,3])
print set4

# overflow in pow, use long long internally
print pow(290797,2,50515093)
