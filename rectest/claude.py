class BankAccount:
    def __init__(self, balance=0):
        self.balance = balance
        self.history = []
    def deposit(self, amt):
        self.balance += amt
        self.history.append(('deposit', amt))
        return self
    def withdraw(self, amt):
        if amt > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amt
        self.history.append(('withdraw', amt))
        return self

acc = BankAccount(100)
acc.deposit(50).withdraw(30).deposit(10)
print(acc.balance)

class LRUCacheSimple:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.order = []
    def get(self, key):
        if key not in self.cache:
            return '?'
        self.order.remove(key)
        self.order.append(key)
        return self.cache[key]
    def put(self, key, value):
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.order.pop(0)
            del self.cache[oldest]
        self.cache[key] = value
        self.order.append(key)

lru = LRUCacheSimple(2)
lru.put(1, 'a')
print(lru.get(1))

class Graph:
    def __init__(self):
        self.edges = {}
    def add_edge(self, a, b):
        self.edges.setdefault(a, []).append(b)
        self.edges.setdefault(b, []).append(a)
    def bfs(self, start):
        visited = {start}
        queue = [start]
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in self.edges.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

g = Graph()
g.add_edge(1, 2)
print(g.bfs(1))
