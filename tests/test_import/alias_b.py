# same names as in alias_a (see test_import_from_as_same_name)

class Item:
    count = 2

    def val(self):
        return 'b'

    @staticmethod
    def twice(x):
        return x * 20


def f(x):
    return x + 2
