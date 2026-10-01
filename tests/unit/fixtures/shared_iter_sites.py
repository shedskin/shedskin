# Fixture for test_contours: two list comprehensions over different
# containers, one of which holds lists.


def main():
    rows = [[1, 2], [3, 4, 5]]
    names = ["a", "b"]
    lengths = [len(z) for z in rows]
    upper = [n.upper() for n in names]
    print(lengths, upper)


main()
