"""
Dijkstra's single-source shortest-path algorithm
from: https://github.com/keon/algorithms
"""

class Dijkstra():
    """
    A fully connected directed graph with edge weights
    """

    def __init__(self, vertex_count):
        self.vertex_count = vertex_count
        self.graph = [[0 for _ in range(vertex_count)] for _ in range(vertex_count)]

    def min_distance(self, dist, min_dist_set):
        """
        Find the vertex that is closest to the visited set
        """
        min_dist = float("inf")
        for target in range(self.vertex_count):
            if min_dist_set[target]:
                continue
            if dist[target] < min_dist:
                min_dist = dist[target]
                min_index = target
        return min_index

    def dijkstra(self, src):
        """
        Given a node, returns the shortest distance to every other node
        """
        dist = [float("inf")] * self.vertex_count
        dist[src] = 0
        min_dist_set = [False] * self.vertex_count

        for _ in range(self.vertex_count):
            #minimum distance vertex that is not processed
            source = self.min_distance(dist, min_dist_set)

            #put minimum distance vertex in shortest tree
            min_dist_set[source] = True

            #Update dist value of the adjacent vertices
            for target in range(self.vertex_count):
                if self.graph[source][target] <= 0 or min_dist_set[target]:
                    continue
                if dist[target] > dist[source] + self.graph[source][target]:
                    dist[target] = dist[source] + self.graph[source][target]

        return dist

def test_dijkstra():
    g = Dijkstra(9)
    g.graph = [[0, 4, 0, 0, 0, 0, 0, 8, 0],
               [4, 0, 8, 0, 0, 0, 0, 11, 0],
               [0, 8, 0, 7, 0, 4, 0, 0, 2],
               [0, 0, 7, 0, 9, 14, 0, 0, 0],
               [0, 0, 0, 9, 0, 10, 0, 0, 0],
               [0, 0, 4, 14, 10, 0, 2, 0, 0],
               [0, 0, 0, 0, 0, 2, 0, 1, 6],
               [8, 11, 0, 0, 0, 0, 1, 0, 7],
               [0, 0, 2, 0, 0, 0, 6, 7, 0]]

    assert g.dijkstra(0) == [0, 4, 12, 19, 21, 11, 9, 8, 14]


def test_all():
    test_dijkstra()

if __name__ == '__main__':
    test_all() 

