"""
demo module doctrings

"""
#import socket



GLOBAL_VAR_A = 10
GLOBAL_VAR_B = "hello"
GLOBAL_VAR_C = 12.51

def foo(x,y):
    """foo function docstrings"""
    return x+y

def bar(hello):
    """bar function docstrings"""
    return '%s world!' % hello

class Person:
    """Person class docstrings"""

    def __init__(self, name, age):
        self.name = name
        self.age = age

class Vehicle:
    """Vehicle class docstrings"""

    def __init__(self, year, owner):
        self.year = year
        self.owner = owner



def test_demo():
    person = Person('sam', 50)
    fiesta = Vehicle(1997, person)

    foo_results = foo(1,2)
    bar_results = bar('hello')

    assert foo_results == 3
    assert bar_results == 'hello world!'

def test_all():
    test_demo()


if __name__ == '__main__':
   test_all() 
