# dijkstra shortest-distance algorithm
#
# (C) 2006 Gustavo J.A.M. Carneiro, licensed under the GPL version 2

import random

random.seed()

class Vertex(object):
    __slots__ = ('name',)
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Edge(object):
    __slots__ = ('u', 'v', 'd')
    def __init__(self, u, v, d):
        assert isinstance(u, Vertex) # source vertex
        assert isinstance(v, Vertex) # destination vertex
        assert isinstance(d, float) # distance, or cost
        self.u = u
        self.v = v
        self.d = d
    def __str__(self):
        return "[%s --%3.2f--> %s]" % (self.u.name, self.d, self.v.name)
    def __repr__(self):
        return str(self)

class Graph(object):
    def __init__(self):
        V = []

        for n in xrange(100):
            V.append(Vertex(str(n + 1)))

        E = []
        for n in xrange(10*len(V)):
            u = V[random.randint(0, len(V) - 1)]
            while True:
                v = V[random.randint(0, len(V) - 1)]
                if v is not u:
                    break
            E.append(Edge(u, v, random.uniform(10, 100)))

        self.V = V
        self.E = E

    def distance(self, s, S):
        for edge in [e for e in G.E if e.u == s and e.v == S[0]]:
            d = edge.d
            break
        else:
            raise AssertionError

        for u, v in zip(S[:-1], S[1:]):
            for edge in [e for e in G.E if e.u == u and e.v == v]:
                d += edge.d
                break
            else:
                raise AssertionError
        return d

def Extract_Min(Q, d):
    m = None
    md = 1e50
    for u in Q:
        if m is None:
            m = u
            md = d[u]
        else:
            if d[u] < md:
                md = d[u]
                m = u
    Q.remove(m)
    return m

def dijkstra(G, t, s):
    d = {}
    previous = {}
    for v in G.V:
        d[v] = 1e50 # infinity
        previous[v] = None
    del v
    d[s] = 0
    S = []
    Q = list(G.V)


    while Q:
        u = Extract_Min(Q, d)
        if u == t:
            break
        S.append(u)
        for edge in [e for e in G.E if e.u == u]:
            if d[u] + edge.d < d[edge.v]:
                d[edge.v] = d[u] + edge.d
                previous[edge.v] = u

    S = []
    u = t
    while previous[u] is not None:
        S.insert(0, u)
        u = previous[u]
    return S
 
if __name__ == '__main__':
    for n in xrange(100):
        G = Graph()
        s = G.V[random.randint(0, len(G.V) - 1)]
        while True:
            t = G.V[random.randint(0, len(G.V) - 1)]
            if t is not s:
                break
        S = dijkstra(G, t, s)
        if S:
            print "dijkstra %s ---> %s: " % (s, t), S, G.distance(s, S)
            for inter in S[:-1]:
                S1 = dijkstra(G, t, inter)
                print "\t => dijkstra %s ---> %s: " % (inter, t), S1, G.distance(inter, S1)
                if S1 != S[ (len(S) - len(S1)) : ]:
                    print "************ ALARM! **************"


 	  	 
