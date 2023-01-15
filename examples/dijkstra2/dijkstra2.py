'''
bidirectional dijkstra/search algorithm, mostly copied from NetworkX:

http://networkx.lanl.gov/

NetworkX is free software; you can redistribute it and/or modify it under the terms of the LGPL (GNU Lesser General Public License) as published by the Free Software Foundation; either version 2.1 of the License, or (at your option) any later version. Please see the license for more information.

'''

import heapq, time, sys, random

random.seed(1)
print(sys.version)

class Graph:
    def __init__(self):
        self.vertices = {}

    def add_edge(self, a, b, weight):
        for id_ in (a, b):
            if id_ not in self.vertices:
                self.vertices[id_] = Vertex(id_)
        va, vb = self.vertices[a], self.vertices[b]
        va.neighs.append((vb, weight))
        vb.neighs.append((va, weight))

class Vertex:
    def __init__(self, id_):
        self.id_ = id_
        self.neighs = []

    def __repr__(self):
        return repr(self.id_)

    def __lt__(self, other):
        return self.id_ < other.id_

def bidirectional_dijkstra(G, source_id, target_id):
    source, target = G.vertices[source_id], G.vertices[target_id]
    if source == target: return (0.0, [source])
    #Init:   Forward             Backward
    dists =  [{},                {}]# dictionary of final distances
    paths =  [{source:[source]}, {target:[target]}] # dictionary of paths
    fringe = [[],                []] #heap of (distance, node) tuples for extracting next node to expand
    seen =   [{source:0.0},        {target:0.0} ]#dictionary of distances to nodes seen
    #initialize fringe heap
    heapq.heappush(fringe[0], (0.0, source))
    heapq.heappush(fringe[1], (0.0, target))
    #variables to hold shortest discovered path
    #finaldist = 1e30000
    finalpath = []
    dir = 1
    while fringe[0] and fringe[1]:
        # choose direction
        # dir == 0 is forward direction and dir == 1 is back
        dir = 1-dir
        # extract closest to expand
        (dist, v) = heapq.heappop(fringe[dir])
        if v in dists[dir]:
            # Shortest path to v has already been found
            continue
        # update distance
        dists[dir][v] = dist #equal to seen[dir][v]
        if v in dists[1-dir]:
            # if we have scanned v in both directions we are done
            # we have now discovered the shortest path
            return (finaldist,finalpath)
        for w, weight in v.neighs:
            vwLength = dists[dir][v] + weight
            if w in dists[dir]:
                pass
            elif w not in seen[dir] or vwLength < seen[dir][w]:
                # relaxing
                seen[dir][w] = vwLength
                heapq.heappush(fringe[dir], (vwLength,w))
                paths[dir][w] = paths[dir][v]+[w]
                if w in seen[0] and w in seen[1]:
                    #see if this path is better than than the already
                    #discovered shortest path
                    totaldist = seen[0][w] + seen[1][w]
                    if finalpath == [] or finaldist > totaldist:
                        finaldist = totaldist
                        revpath = paths[1][w][:]
                        revpath.reverse()
                        finalpath = paths[0][w] + revpath[1:]
    return None

def make_graph(n):
    G = Graph()
    dirs = [(-1,0), (1,0), (0,1), (0,-1)]
    for u in range(n):
        for v in range(n):
            for dir in dirs:
                x, y = u+dir[0], v+dir[1]
                if 0 <= x < n and 0 <= y < n:
                    G.add_edge((u,v), (x, y), random.randint(1,3))
    return G

if __name__ == '__main__':
    n = 300
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    t0 = time.time()
    G = make_graph(n)
    print('t0 %.2f' % (time.time()-t0))
    t1 = time.time()
    wt, nodes = bidirectional_dijkstra(G, (0,0), (n-1,n-1))
    print('wt', wt)
    print('t1 %.2f' % (time.time()-t1))
