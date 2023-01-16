# From: http://en.wikipedia.org/wiki/Eight_queens_puzzle


def n_queens(n, width):
    if n == 0:
        return [[]]  # one solution, the empty list
    else:
        return add_queen(n - 1, width, n_queens(n - 1, width))


def add_queen(new_row, width, previous_solutions):
    solutions = []
    for sol in previous_solutions:
        for new_col in range(width):
            if safe_queen(new_row, new_col, sol):
                solutions.append(sol + [new_col])
    return solutions


def safe_queen(new_row, new_col, sol):
    for row in range(new_row):
        if (
            sol[row] == new_col
            or sol[row] + row == new_col + new_row
            or sol[row] - row == new_col - new_row
        ):
            return 0
    return 1


def test_nqueens():
    # n = 12
    n = 4
    solutions = n_queens(n, n)
    # print(len(solutions), "solutions.")
    # assert len(solutions) == 14200
    assert len(solutions) == 2


def test_all():
    test_nqueens()
    

if __name__ == '__main__':
    test_all() 

