# extension module under test: compile with 'shedskin build -e alloc',
# then run alloc_main.py (see README.md)

# many small allocations of different sizes (served from the free lists),
# and a few larger ones, with garbage collections in between


class Node:
    def __init__(self, value, next):
        self.value = value
        self.next = next


def chain(n):
    # a linked list that stays alive while garbage piles up around it
    head = None
    for i in range(n):
        head = Node(i, head)
        junk = [(i, i + 1), (i + 2, i + 3)]
        junk1 = (i, str(i))
        junk2 = [i] * (i % 40)
    total = 0
    while head is not None:
        total += head.value
        head = head.next
    return total


def pairs(n):
    return [(i, i * i) for i in range(n)]


def words(n):
    return ['w' + str(i) for i in range(n)]


if __name__ == '__main__':
    print(chain(1000))
    print(pairs(10)[3])
    print(words(10)[3])
