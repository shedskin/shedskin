#class list:                              # unit: [float]*
#    def append(self, x):                 # x: [float], self: [list_float]
#        self.unit = x                    # [float]
#
#    def __getitem__(self, i):            # i: [int], a: [float], self: [list_float]
#        a = self.unit                    # [float]
#        return a                         # [float]

list1 = []
list1.append(1.0)

list2 = []
list2.append(1)

list3 = []
list3.append("astring")

list4 = [(1,2),(3,4)]

# list5 = list4.copy() # NotImplemented

list5 = [(1,2),(3,4)]



def test_list_append():
    assert list1[0] == 1.0
    assert list2[0] == 1
    assert list3[0] == "astring"


def test_tuple_in_list():
    assert (1,2) in list4


def test_list_assign():
    list5[0] = (2,2)
    assert list5 == [(2,2),(3,4)]




if __name__ == '__main__':
    test_list_append()
    test_tuple_in_list()
