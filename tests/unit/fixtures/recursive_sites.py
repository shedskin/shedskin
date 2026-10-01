# Fixture for test_contours: a function that creates a list and passes it to
# itself.


def collect(items, n):
    acc = []
    acc.append(n)
    if n > 0:
        collect(acc, n - 1)
    return len(items)


print(collect([0], 3))
