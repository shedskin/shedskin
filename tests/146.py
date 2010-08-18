
class C1:
  def m1(self): self.a1 = 1
  def m2(self): self.a2 = 2
class C2(C1):
  def m2(self): self.a = 3
class C3(C2):
  def m2(self): self.a2 = 4
c3 = C3()
c3.m1()
c3.m2()
print c3.a1, c3.a2

