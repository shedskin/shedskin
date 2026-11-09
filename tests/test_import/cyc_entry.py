"""module whose header gets a typedef from cyc_holder referring back to it"""


class Entry:
    def __init__(self, pos):
        self.pos = pos


def describe(obj):  # only called with a cyc_holder.Holder
    return obj.first()
