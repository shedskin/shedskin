
class Person:
    def __init__(self, name, age):
        self._name = name
        self._age = age

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

class SuperHero(Person): pass

def test_property():
    person = Person("Alice", 30)

    assert person.name == "Alice"
    person.name = "Bob"
    assert person.name == "Bob"

    hero = SuperHero("Sam", 10)

    assert hero.name == "Sam"
    hero.name = "Sue"
    assert hero.name == "Sue"



class Calc:
    @staticmethod
    def add(x, y):
        return x+y


def test_staticmethod():
    assert Calc.add(1, 2) == 3

def test_all():
    test_property()
    test_staticmethod()


if __name__ == "__main__":
    test_all()
