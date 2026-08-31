# Regression coverage for is_property_setter(): multiple real
# @property/@X.setter pairs in one class (to make sure registering one
# property doesn't interfere with another), plus a class that has both a
# real property/setter pair *and* a plain, ordinary method that happens
# to be named 'setter' (not used as a decorator), to confirm the two
# don't interfere with each other.

class Temperature:
    def __init__(self):
        self._celsius = 0.0
        self._label = ''

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        self._celsius = value

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def fahrenheit(self):
        return self._celsius * 9.0 / 5.0 + 32.0


def test_multiple_properties():
    t = Temperature()
    t.celsius = 100.0
    t.label = 'boiling'
    assert t.celsius == 100.0
    assert t.label == 'boiling'
    assert t.fahrenheit == 212.0


class Gadget:
    def __init__(self):
        self._power = 0
        self.applied = 0

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, value):
        self._power = value

    # an ordinary method that just happens to share the name 'setter';
    # not used as a decorator anywhere, so should behave completely
    # normally alongside the real property/setter pair above
    def setter(self, value):
        self.applied += 1
        return value * 2


def test_property_and_plain_setter_method_coexist():
    g = Gadget()
    g.power = 7
    assert g.power == 7
    assert g.setter(3) == 6
    assert g.applied == 1


def test_all():
    test_multiple_properties()
    test_property_and_plain_setter_method_coexist()


if __name__ == '__main__':
    test_all()
    print("ALL OK")
