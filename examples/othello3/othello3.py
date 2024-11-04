import collections

# define all 38 lines
lines = [
    ((0,0), (7,0), 1, 0), # horizontal
    ((0,1), (7,1), 1, 0),
    ((0,2), (7,2), 1, 0),
    ((0,3), (7,3), 1, 0),
    ((0,4), (7,4), 1, 0),
    ((0,5), (7,5), 1, 0),
    ((0,6), (7,6), 1, 0),
    ((0,7), (7,7), 1, 0),

    ((0,0), (0,7), 0, 1), # vertical
    ((1,0), (1,7), 0, 1),
    ((2,0), (2,7), 0, 1),
    ((3,0), (3,7), 0, 1),
    ((4,0), (4,7), 0, 1),
    ((5,0), (5,7), 0, 1),
    ((6,0), (6,7), 0, 1),
    ((7,0), (7,7), 0, 1),

    ((0,2), (2,0), 1, -1), # diagonal asc
    ((0,3), (3,0), 1, -1),
    ((0,4), (4,0), 1, -1),
    ((0,5), (5,0), 1, -1),
    ((0,6), (6,0), 1, -1),
    ((0,7), (7,0), 1, -1),
    ((1,7), (7,1), 1, -1),
    ((2,7), (7,2), 1, -1),
    ((3,7), (7,3), 1, -1),
    ((4,7), (7,4), 1, -1),
    ((5,7), (7,5), 1, -1),

    ((0,5), (2,7), 1, 1), # diagonal desc
    ((0,4), (3,7), 1, 1),
    ((0,3), (4,7), 1, 1),
    ((0,2), (5,7), 1, 1),
    ((0,1), (6,7), 1, 1),
    ((0,0), (7,7), 1, 1),
    ((1,0), (7,6), 1, 1),
    ((2,0), (7,5), 1, 1),
    ((3,0), (7,4), 1, 1),
    ((4,0), (7,3), 1, 1),
    ((5,0), (7,2), 1, 1),
]

# initial state
state = [list('........') for _ in range(38)]

# topology
topology = collections.defaultdict(list)
for i, (start, end, dx, dy) in enumerate(lines):
    j = 0
    pos = start
    while True:
        topology[pos].append((i, j))
        if pos == end:
            break
        pos = (pos[0]+dx, pos[1]+dy)
        j += 1

print(topology)

def place(pos, turn):
    for line, pos in topology[pos]:
        print('gots', line, pos)
        state[line][pos] = turn

place((3,3), 'o')
place((3,4), 'x')
place((4,4), 'o')
place((4,3), 'x')

for s in state:
    print(s)
