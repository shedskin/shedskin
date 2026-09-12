class Entry:
    def __init__(self, pos):
        self.tape_pos = pos
        self.end_addr = 0

class Loader:
    def __init__(self):
        self.entries = []
        self.offsets = []
    def parse(self, n):
        self.entries = [Entry(i) for i in range(n)]
        self.offsets = sorted(map(lambda entry: (entry.tape_pos, entry), self.entries))
        self.offsets.append((99, None))
        for size, entry in find_distances(self.offsets):
            entry.end_addr = entry.tape_pos + size
        return self

def find_distances(items):
    h, t = items[0], items[1:]
    if len(t) == 0:
        return []
    else:
        hh, tt = t[0], t[1:]
        return [(hh[0] - h[0], h[1])] + find_distances(t)

l = Loader().parse(3)
print([e.end_addr for e in l.entries])
