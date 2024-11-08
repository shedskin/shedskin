from othello3 import *

# generate function tables
def gen_funcs():
    # 64 empty square moves (4 unused)
    move_funcs = []
    for j in range(8):
        for i in range(8):
            human_move = 'abcdefgh'[i] + str(j+1)
            func_name = f'put_{human_move}'
            move_funcs.append(func_name)
            print(f'class {func_name}(Put):')
            print('    def go(self):')
            for (l, idx) in topology[i, j]:
                print(f"        global state_{l}")
            for (l, idx) in topology[i, j]:
                print(f'        flipnr = flippers_x[state_{l} << 10 | {idx << 2} | turn+1]')
                print(f'        line_flip_func[{l} << 6 | flipnr].go()')
            for (l, idx) in topology[i, j]:
                print(f"        state_{l} += turn * {3**idx}")
            print()

    print('move_table = [')
    for name in move_funcs:
        print(f'   {name}(),')
    print(']')
    print()

    # 830 flip patterns (831 including noop)
    patterns = list(flips_nr)
    flipfuncs = set()
    for i, line in enumerate(lines):
        for p in patterns:
            if p and max(p) < line.length-1:
                posn = sorted([calc_pos(i, j) for j in p])
                flipfuncs.add(tuple(posn))

    for flipfunc in flipfuncs:
        human_moves = '_'.join(['abcdefgh'[i] + str(j+1) for (i, j) in flipfunc])
        print(f'class flip_{human_moves}(Flip):')
        print('    def go(self):')
        line_idcs = collections.defaultdict(list)
        for pos in flipfunc:
            for (l, idx) in topology[pos]:
                line_idcs[l].append(idx)
        for l in line_idcs:
            print(f"        global state_{l}")
        for (l, idcs) in line_idcs.items():
            value = sum(3**idx for idx in idcs)
            print(f"        state_{l} += turn * {2 * value}")
        print()

    print('line_flip_func = {}')
    for l in range(46):
        for nr, flips in nr_flips.items():
            posn = sorted([calc_pos(l, idx) for idx in flips if idx < lines[l].length-1])
            human_moves = '_'.join(['abcdefgh'[i] + str(j+1) for (i, j) in posn])
            print(f'line_flip_func[{l << 6 | nr}] = flip_{human_moves}()')


if __name__ == '__main__':
    gen_funcs()
