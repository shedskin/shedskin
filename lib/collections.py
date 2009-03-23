class deque(pyiter):
    def __init__(self, iterable=None):
        self.unit = iterable.unit

    def append(self, x):
        self.unit = x
    def appendleft(self, x):
        self.unit = x
    def extend(self, b):
        self.unit = b.unit
    def extendleft(self, b):
        self.unit = b.unit

    def rotate(self, n):
        pass

    def pop(self):
        return self.unit
    def popleft(self):
        return self.unit

    def remove(self, e):
        pass
    def clear(self):
        pass

    def __getitem__(self, i):
        return self.unit
    def __setitem__(self, i, e):
        self.unit = e
    def __delitem__(self, i):
        pass

    def __contains__(self, e):
        return 1

    def __len__(self):
        return 1
    def __iter__(self):
        return __iter(self.unit)

    def __copy__(self):
        return self
    def __deepcopy__(self):
        return self

class defaultdict:
    def __init__(self, value):
        self.value = value

    def __initdict__(self, value, d):
        self.value = value
        self.value = d.value
        self.unit = d.unit

    def __inititer__(self, value, i):
        item = iter(i).next()
        self.unit = item[0]
        self.value = item[1]

    def __setitem__(self, key, value):
        self.__setunit__(key, value)

    def __getitem__(self, key):
        self.__missing__(key)
        return self.value

    def __missing__(self, key):
        self.unit = key
        return self.value

    def keys(self):                      
        return [self.unit]
    def values(self):                  
        return [self.value]           
    def items(self):                 
        return [(self.unit, self.value)] 

    def __repr__(self):             
        self.unit.__repr__()       
        self.value.__repr__()     
        return ''                

    def __str__(self):                  
        return self.__repr__()
    
    def __setunit__(self, k, v):
        self.unit = k
        k.__hash__()
        k.__eq__(k)
        self.value = v

    def __delitem__(self, i):
        pass

    def setdefault(self, k, v=None):  
        self.__setunit__(k, v)
        return v                     

    def has_key(self, k):             
        return 1                    

    def __len__(self):             
        return 1                  

    def clear(self):                     
        pass
    def copy(self):                     
        return {self.unit: self.value} 

    def get(self, k, default=None):   
        return self.value                
        return default
    def pop(self, k):                  
        return self.value            
    def popitem(self):                 
        return (self.unit, self.value)
    def update(self, d):             
        self.__setunit__(d.unit, d.value)

    def __delete__(self, i):
        pass  

    def fromkeys(l, b=None):
        d = defaultdict()
        d.value = b
        d.unit = iter(l).next() 
        return d
    fromkeys = staticmethod(fromkeys) # XXX classmethod

    def iterkeys(self):
        return __iter(self.unit) 
    def itervalues(self):
        return __iter(self.value)
    def iteritems(self):
        return __iter((self.unit, self.value))


