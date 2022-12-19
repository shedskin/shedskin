# class Object:

#     def __init__(self, name, *args, **kwds):
#         self.name
#         self.args = args
#         self.kwds = kwds
    
#     def __str__(self):
#         return f"<Object '{self.name}'>"
    
#     def __setitem__(self, name , value):
#         self.kwds[name] = value
    
#     def __getitem__(self, name):
#         if name in self.kwds:
#             return self.kwds[name]
    
#     def __delitem__(self, name):
#         if name in self.kwds:
#             del self.kwds[name]
    
#     def __len__(self):
#         return len(self.args)
    
#     def __contains__(self, name):
#         if name in self.kwds:
#             return True
#         else:
#             return False
    

def test_basic():
    assert 1+1 == 2

def test_all():
    test_basic()


if __name__ == '__main__':
    test_all()

