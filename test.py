class M(object):
    pass
class P2(M):
    def handle_key_press(self, n):
        pass
class P1(M):
    pass

p = P1()
p = P2()
p.handle_key_press("X")
