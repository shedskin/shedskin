# Fixture for test_contours: two iter() calls, and itertools.product, whose
# builtin implementation allocates tuples of its own.

import itertools

numbers = iter([1, 2, 3])
letters = iter(["a", "b"])
for pair in itertools.product([1, 2], ["x", "y"]):
    print(pair)
print(next(numbers), next(letters))
