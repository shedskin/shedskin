import random
random.seed(1)

faces = U, R, F, D, L, B = range(6)
facenames = ["U", "R", "F", "D", "L", "B"]

facelets = U1, U2, U3, U4, U5, U6, U7, U8, U9, R1, R2, R3, R4, R5, R6, R7, R8, R9, F1, F2, F3, F4, F5, F6, F7, F8, F9, D1, D2, D3, D4, D5, D6, D7, D8, D9, L1, L2, L3, L4, L5, L6, L7, L8, L9, B1, B2, B3, B4, B5, B6, B7, B8, B9 = range(54)

facelet_color = ["G"] * 9 + ["O"] * 9 + ["W"] * 9 + ["B"] * 9 + ["R"] * 9 + ["Y"] * 9

facelet_turn = [
    [U3,U6,U9,U2,U5,U8,U1,U4,U7,F1,F2,F3,R4,R5,R6,R7,R8,R9,L1,L2,L3,F4,F5,F6,F7,F8,F9,D1,D2,D3,D4,D5,D6,D7,D8,D9,B1,B2,B3,L4,L5,L6,L7,L8,L9,R1,R2,R3,B4,B5,B6,B7,B8,B9],
    [U1,U2,B7,U4,U5,B4,U7,U8,B1,R3,R6,R9,R2,R5,R8,R1,R4,R7,F1,F2,U3,F4,F5,U6,F7,F8,U9,D1,D2,F3,D4,D5,F6,D7,D8,F9,L1,L2,L3,L4,L5,L6,L7,L8,L9,D9,B2,B3,D6,B5,B6,D3,B8,B9],
    [U1,U2,U3,U4,U5,U6,R1,R4,R7,D3,R2,R3,D2,R5,R6,D1,R8,R9,F3,F6,F9,F2,F5,F8,F1,F4,F7,L3,L6,L9,D4,D5,D6,D7,D8,D9,L1,L2,U9,L4,L5,U8,L7,L8,U7,B1,B2,B3,B4,B5,B6,B7,B8,B9],
    [U1,U2,U3,U4,U5,U6,U7,U8,U9,R1,R2,R3,R4,R5,R6,B7,B8,B9,F1,F2,F3,F4,F5,F6,R7,R8,R9,D3,D6,D9,D2,D5,D8,D1,D4,D7,L1,L2,L3,L4,L5,L6,F7,F8,F9,B1,B2,B3,B4,B5,B6,L7,L8,L9],
    [F1,U2,U3,F4,U5,U6,F7,U8,U9,R1,R2,R3,R4,R5,R6,R7,R8,R9,D1,F2,F3,D4,F5,F6,D7,F8,F9,B9,D2,D3,B6,D5,D6,B3,D8,D9,L3,L6,L9,L2,L5,L8,L1,L4,L7,B1,B2,U7,B4,B5,U4,B7,B8,U1],
    [L7,L4,L1,U4,U5,U6,U7,U8,U9,R1,R2,U1,R4,R5,U2,R7,R8,U3,F1,F2,F3,F4,F5,F6,F7,F8,F9,D1,D2,D3,D4,D5,D6,R9,R6,R3,D7,L2,L3,D8,L5,L6,D9,L8,L9,B3,B6,B9,B2,B5,B8,B1,B4,B7],
]

facemap = [0, 3, 2, 5, 4, 1]

affected_cubies = [
  [  0,  1,  2,  3,  0,  1,  2,  3 ],   # U
  [  4,  7,  6,  5,  4,  5,  6,  7 ],   # D
  [  0,  9,  4,  8,  0,  3,  5,  4 ],   # F
  [  2, 10,  6, 11,  2,  1,  7,  6 ],   # B
  [  3, 11,  7,  9,  3,  2,  6,  5 ],   # L
  [  1,  8,  5, 10,  1,  0,  4,  7 ],   # R
]

def row(state, j):
    return ' '.join([facelet_color[state[i]] for i in range(j, j+3)])

def visual(state):
   for i in range(3):
       print 8*' '+row(state, U*9+3*i)
   for i in range(3):
       print ' '+row(state, L*9+3*i)+'  '+row(state, F*9+3*i)+'  '+row(state, R*9+3*i)+'  '+row(state, B*9+3*i)
   for i in range(3):
       print 8*' '+row(state, D*9+3*i)

def move_str(move):
    return facenames[facemap[move/3]]+{1: '', 2: '2', 3: "'"}[move%3+1]

def apply_move(move, state, state2):
    turns = move % 3 + 1;
    face = move / 3;

    face2 = facemap[face]
    for turn in range(turns):
        newstate = 54*[0]
        for i in range(54):
            newstate[facelet_turn[face2][i]] = state[i]
        state = newstate

    newstate2 = state2[:]
    for turn in range(turns):
        oldstate = newstate2[:]
        for i in range(8):
            isCorner = int(i > 3)
            target = affected_cubies[face][i] + isCorner*12
            killer = affected_cubies[face][(i-3) if (i&3)==3 else i+1] + isCorner*12
            orientationDelta = int(1<face<4) if i<4 else (0 if face<2 else 2 - (i&1))
            newstate2[target] = oldstate[killer]
            newstate2[target+20] = oldstate[killer+20] + orientationDelta
            if turn == turns-1:
                newstate2[target+20] %= 2 + isCorner

    return newstate, newstate2

class cube_state:
    def __init__(self, state, state2, route):
        self.state = state
        self.state2 = state2
        self.route = route

    def apply_move(self, move):
        state, state2 = apply_move(move, self.state, self.state2)
        return cube_state(state, state2, self.route+[move])

def get_id(cube_state, phase):
    state = cube_state.state2
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

    return tuple(cube_state.state2)

goal_state = range(20)+20*[0]
#print 'goal id 0', get_id(cube_state(None, goal_state, []), 0)
#print 'goal id 1', get_id(cube_state(None, goal_state, []), 1)

print 'start'
state = range(54)
visual(state)

state2 = range(20)+20*[0]
#print state2, state2[20:32]

#print 'start id', get_id(cube_state(state, state2, []), 1)

print 'randomize'
for x in range(4):
    move = random.randrange(0,18)
    print move_str(move)
    state, state2 = apply_move(move, state, state2)
visual(state)

applicable_moves = [262143, 262098, 259218, 74898]

for phase in range(4):
    for move in range(18):
        if applicable_moves[phase] & (1<<move):
            print 'ok', phase, move, move_str(move)
#solve

print 'solve'
state_ids = set()
states = [cube_state(state, state2, [])]

for phase in range(4):
    print 'PHASE', phase
    phase_ok = False
    depth = 0
    goal_id = get_id(cube_state(None, goal_state, []), phase)
    current_id = get_id(states[0], phase)
#    print 'current_id', current_id
    if current_id == goal_id:
#        print 'al ok'
        continue

    while not phase_ok:
#        print 'DEPTH', depth
        new_states = []
        for cstate in states:
            for move in range(18):
                if applicable_moves[phase] & (1<<move):
                    new_state = cstate.apply_move(move)
                    id_ = get_id(new_state, phase)
#                    print 'move', move_str(move), id_
                    if id_ == goal_id:
#                        print 'gevonden!', move_str(move), id_
                        for m in new_state.route:
                            print move_str(m)
                        cs = cube_state(state, state2, [])
                        for m in new_state.route:
                            cs = cs.apply_move(m)
                        visual(cs.state)
                        phase_ok = True
                        break
                    elif id_ not in state_ids:
                        state_ids.add(id_)
                        new_states.append(new_state)
            if phase_ok:
                break
        depth += 1
#        print 'new states at depth %d: %d' % (depth, len(new_states))
        states = new_states

    state_ids = set()
    states = [new_state]

print 'used moves:', len(new_state.route)
