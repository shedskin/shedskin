"""lambda typedef referring to a class from cyc_entry"""

from cyc_entry import Entry


class Holder:
    def __init__(self):
        self.entries = [Entry(3), Entry(1), Entry(2)]

    def first(self):
        offsets = sorted(map(lambda entry: (entry.pos, entry), self.entries))
        return offsets[0][1].pos
