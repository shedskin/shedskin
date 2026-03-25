# Demo program for shedskin pipeline integration tests.
# Exercises many language features to cover type inference,
# code generation, and virtual method analysis paths.


def add(x, y):
    return x + y


def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def string_ops():
    s = "hello"
    t = s.upper()
    u = s + " world"
    return len(u)


def list_ops():
    nums = [1, 2, 3, 4, 5]
    doubled = [x * 2 for x in nums]
    total = 0
    for n in doubled:
        total += n
    return total


def dict_ops():
    d = {"a": 1, "b": 2, "c": 3}
    keys = []
    for k in d:
        keys.append(k)
    return d["a"]


def tuple_ops():
    t = (1, 2)
    a, b = t
    return a + b


class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return self.name


class Dog(Animal):
    def speak(self):
        return self.name + " says woof"


class Cat(Animal):
    def speak(self):
        return self.name + " says meow"


def use_animals():
    animals = [Dog("Rex"), Cat("Whiskers")]
    result = []
    for a in animals:
        result.append(a.speak())
    return result


double = lambda x: x * 2


def use_lambda():
    return double(21)


def range_loop():
    total = 0
    for i in range(10):
        total += i
    return total


def enumerate_loop():
    words = ["a", "b", "c"]
    result = 0
    for i, w in enumerate(words):
        result += i
    return result


def float_math():
    x = 3.14
    y = 2.0
    return x * y


def nested_list():
    matrix = [[1, 2], [3, 4], [5, 6]]
    flat = []
    for row in matrix:
        for val in row:
            flat.append(val)
    return flat


def set_ops():
    s = set([1, 2, 3, 2, 1])
    return len(s)


if __name__ == "__main__":
    print(add(1, 2))
    print(factorial(5))
    print(string_ops())
    print(list_ops())
    print(dict_ops())
    print(tuple_ops())
    print(use_animals())
    print(use_lambda())
    print(range_loop())
    print(enumerate_loop())
    print(float_math())
    print(nested_list())
    print(set_ops())
