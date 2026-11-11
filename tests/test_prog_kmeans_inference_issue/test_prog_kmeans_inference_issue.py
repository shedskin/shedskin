# reduced from the kmeanspp example (#1769): a call without arguments
# (float_one()) in a template that is not the first one created for its
# function (kpp) was never analyzed, so sum_2 sporadically had no type


class Point:
    def __init__(self, x=0.0):
        self.x = x


def float_one():
    return 1.0


def generate_points(npoints):
    points = [Point()]
    return points


def kpp(points):
    d = [0.5]
    total = 0.0
    for i in range(1, 4):
        sum_1 = 0
        sum_3 = sum_1 * float_one()
        for di in d:
            sum_2 = sum_3 - di
            sum_3 = sum_2
            if sum_2 < 0:
                total += sum_2
    return total


def test_noarg_call_in_template():
    points = generate_points(10)
    assert kpp(points) == -1.5


def test_all():
    test_noarg_call_in_template()


if __name__ == '__main__':
    test_all()
