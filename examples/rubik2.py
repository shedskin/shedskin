# Rubik's cube solver using Thistlethwaite's algorithm
#
# translated from Stefan Pochmann's C++ implementation:
#
# http://www.stefan-pochmann.info/spocc/other_stuff/tools/
#
# by Mark Dufour
#
# but without the bidirectional search, for readability..
# you probably want to have at least 2 GB of RAM because of this
# 
# comments from the C++ version:
#
# cube 'state' is a list with 40 entries, the first 20
# are a permutation of {0,...,19} and describe which cubie is at
# a certain position (regarding the input ordering). The first
# twelve are for edges, the last eight for corners.
# 
# The last 20 entries are for the orientations, each describing
# how often the cubie at a certain position has been turned
# counterclockwise away from the correct orientation. Again the
# first twelve are edges, the last eight are corners. The values
# are 0 or 1 for edges and 0, 1 or 2 for corners.

import random
random.seed(1)

facenames = ["U", "D", "F", "B", "L", "R"]

affected_cubies = [
  [  0,  1,  2,  3,  0,  1,  2,  3 ],   # U
  [  4,  7,  6,  5,  4,  5,  6,  7 ],   # D
  [  0,  9,  4,  8,  0,  3,  5,  4 ],   # F
  [  2, 10,  6, 11,  2,  1,  7,  6 ],   # B
  [  3, 11,  7,  9,  3,  2,  6,  5 ],   # L
  [  1,  8,  5, 10,  1,  0,  4,  7 ],   # R
]

applicable_moves = [262143, 259263, 74943, 74898]

def move_str(move):
    return facenames[move/3]+{1: '', 2: '2', 3: "'"}[move%3+1]

def apply_move(move, state):
    turns = move % 3 + 1
    face = move / 3
    newstate = state[:]
    for turn in range(turns):
        oldstate = newstate[:]
        for i in range(8):
            isCorner = int(i > 3)
            target = affected_cubies[face][i] + isCorner*12
            killer = affected_cubies[face][(i-3) if (i&3)==3 else i+1] + isCorner*12
            orientationDelta = int(1<face<4) if i<4 else (0 if face<2 else 2 - (i&1))
            newstate[target] = oldstate[killer]
            newstate[target+20] = oldstate[killer+20] + orientationDelta
            if turn == turns-1:
                newstate[target+20] %= 2 + isCorner
    return newstate

def get_id(state, phase):
    if phase == 0:
        return tuple(state[20:32])
    if phase == 1:
        result = state[31:40]
        for e in range(12):
            result[0] |= (state[e] / 8) << e;
        return tuple(result)
    if phase == 2:
        result = [0,0,0]
        for e in range(12):
            result[0] |= (2 if (state[e] > 7) else (state[e] & 1)) << (2*e)
        for c in range(8):
            result[1] |= ((state[c+12]-12) & 5) << (3*c)
        for i in range(12, 20):
            for j in range(i+1, 20):
                result[2] ^= int(state[i] > state[j])
        return tuple(result)
    return tuple(state)

class cube_state:
    def __init__(self, state, route=None):
        self.state = state
        self.route = route or []

    def id_(self, phase):
        return get_id(self.state, phase)

    def apply_move(self, move):
        state = apply_move(move, self.state)
        return cube_state(state, self.route+[move])

goal_state = cube_state(range(20)+20*[0])
state = cube_state(goal_state.state[:])

print '*** randomize ***'
moves = [random.randrange(0,18) for x in range(30)]
print ','.join([move_str(move) for move in moves])
print
for move in moves:
    state = state.apply_move(move)

print '*** solve ***'
state.route = []

for phase in range(4):
    current_id = state.id_(phase)
    goal_id = goal_state.id_(phase)

    states = [state]
    state_ids = set([current_id])

    if current_id == goal_id:
      continue

    depth = 0
    phase_ok = False
    while not phase_ok:
        next_states = []
        for cur_state in states:
            for move in range(18):
                if applicable_moves[phase] & (1<<move):
                    next_state = cur_state.apply_move(move)
                    next_id = next_state.id_(phase)
                    if next_id == goal_id:
                        print ','.join([move_str(m) for m in next_state.route])
                        phase_ok = True
                        state = next_state
                        break
                    if next_id not in state_ids:
                        state_ids.add(next_id)
                        next_states.append(next_state)
            if phase_ok:
                break
        if phase_ok:
            break

        depth += 1
        states = next_states

print 'needed %d moves' % len(state.route)
