def rec(n):
    if n == 0:
        return [[]]
    return extend(rec(n - 1))


def extend(prev):
    solutions = []
    solutions.append(prev[0] + [1])
    return solutions

rec(0)
