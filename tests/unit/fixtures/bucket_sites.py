# Fixture for test_contours: mastermind-like scoring of tuples created in a
# comprehension, chosen in a loop.


def score(guess, code):
    return sum(1 for a, b in zip(guess, code) if a == b)


def best(codes, guesses):
    result = None
    top = -1
    for play in guesses:
        total = sum(score(play, code) for code in codes)
        if total > top:
            top, result = total, play
    return result


codes = [(1, 2), (2, 1)]
guesses = [(a, b) for a in range(3) for b in range(3)]
print(best(codes, guesses))
