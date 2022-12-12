
board = 1                                # [int]

def best_move(board):                    # board: [int]
    max_move = (1,2)                     # [tuple2(int, int)]
    max_mobility = 1                     # [int]

    return max_move, max_mobility        # [tuple2(tuple2(int, int), int)]

move, mob = best_move(board)                 # [tuple2(tuple2(int, int), int)]

