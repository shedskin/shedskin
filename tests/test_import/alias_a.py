# same names as in alias_b (see test_import_from_as_same_name)

class Item:
    count = 1

    def val(self):
        return 'a'

    @staticmethod
    def twice(x):
        return x * 2


def f(x):
    return x + 1
