from __future__ import print_function

# --- out of bounds can be okay
a = list(range(5))
print(a[:10], a[:10:2])
print(a[-10:], a[-10::2])

# --- abs
class C:
  def __abs__(self):
      return self
  def __neg__(self):
      return self
  def __repr__(self):
      return 'C'

print(abs(C()), abs(23), abs(-1.3), -abs(C()))

# --- improve overloading
class D:
    def __int__(self): return 7
    def __float__(self): return 7.0
    def __str__(self): return '__str__'
    def __repr__(self): return '__repr__'
    def __nonzero__(self): return True
    def __len__(self): return 1

d = D()

print([0,1][bool(d)], str(d), int(d), float(d)) #, max([d,d]), min([d,d]))
if 5: print(5)
if d: print(6)
