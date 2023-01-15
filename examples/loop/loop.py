"""
Copyright 2011 Google Inc.

Licensed under the Apache License, Version 2.0 (the "License")
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http:#www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This version is designed for ShedSkin
D code translated to Python by leonardo maffi, v.1.0, Jun 14 2011
"""

import sys
sys.setrecursionlimit(100000)
from sys import stdout

class Simple_loop(object):
    """
    Basic representation of loops, a loop has an entry point,
    one or more exit edges, a set of basic blocks, and potentially
    an outer loop - a "parent" loop.

    Furthermore, it can have any set of properties, e.g.,
    it can be an irreducible loop, have control flow, be
    a candidate for transformations, and what not.
    """
    def __init__(self):
        self.basic_blocks_ = set()
        self.children_ = set()
        self.parent_ = None
        self.is_root_ = False
        self.counter_ = 0
        self.nesting_level_ = 0
        self.depth_level_ = 0

    def add_node(self, basic_block):
        self.basic_blocks_.add(basic_block)

    def add_child_loop(self, loop):
        self.children_.add(loop)

    def dump(self):
        # Simplified for readability purposes.
        print("loop-%d, nest: %d, depth: %d" % (self.counter_, self.nesting_level_, self.depth_level_))

    # Getters/Setters
    def set_parent(self, parent):
        self.parent_ = parent
        parent.add_child_loop(self)

    def set_nesting_level(self, level):
        self.nesting_level_ = level
        if level == 0:
            self.is_root_ = True


class Loop_structure_graph(object):
    """
    Maintain loop structure for a given cfg.

    Two values are maintained for this loop graph, depth, and nesting level.
    For example:

    loop        nesting level    depth
    ---------------------------------------
    loop-0      2                0
      loop-1    1                1
      loop-3    1                1
        loop-2  0                2
    """
    def __init__(self):
        self.loops_ = []
        self.loop_counter_ = 0
        self.root_ = Simple_loop()
        self.root_.set_nesting_level(0) # make it the root node
        self.root_.counter_ = self.loop_counter_
        self.loop_counter_ += 1
        self.loops_.append(self.root_)

    def create_new_loop(self):
        loop = Simple_loop()
        loop.counter_ = self.loop_counter_
        self.loop_counter_ += 1
        return loop

    def dump(self):
        self.dump_rec(self.root_, 0)

    def dump_rec(self, loop, indent):
        # Simplified for readability purposes.
        loop.dump()

        for liter in loop.children_:
            pass # self.dump_rec(liter, indent + 1)

    def calculate_nesting_level(self):
        # link up all 1st level loops to artificial root node.
        for loop in self.loops_:
            if loop.is_root_:
                continue
            if not loop.parent_:
                loop.set_parent(self.root_)

        # recursively traverse the tree and assign levels.
        self.calculate_nesting_level_rec(self.root_, 0)

    def calculate_nesting_level_rec(self, loop, depth):
        loop.depth_level_ = depth
        for ch in loop.children_:
            calculate_nesting_level_rec(ch, depth + 1)
            loop.nesting_level_ = max(loop.nesting_level_, 1 + ch.nesting_level_)


#======================================================
# Main Algorithm
#======================================================


class Union_find_node(object): # add __slots__ *******************************************
    """
    Union/Find algorithm after Tarjan, R.E., 1983, Data Structures
    and Network Algorithms.
    """
    def init(self, bb, dfs_number):
        self.parent_ = self
        self.bb_ = bb
        self.dfs_number_ = dfs_number
        self.loop_ = None

    def find_set(self):
        """
        Union/Find Algorithm - The find routine.

        Implemented with Path Compression (inner loops are only
        visited and collapsed once, however, deep nests would still
        result in significant traversals).
        """
        nodeList = []

        node = self
        while node != node.parent_:
            if node.parent_ != node.parent_.parent_:
                nodeList.append(node)
            node = node.parent_

        # Path Compression, all nodes' parents point to the 1st level parent.
        for n in nodeList:
            n.parent_ = node.parent_

        return node

    #/ Union/Find Algorithm - The Union routine. We rely on path compression.
    def do_union(self, B):
        self.parent_ = B


class Basic_block_class(object):
    TOP = 0         # uninitialized
    NONHEADER = 1   # a regular BB
    REDUCIBLE = 2   # reducible loop
    SELF = 3        # single BB loop
    IRREDUCIBLE = 4 # irreducible loop
    DEAD = 5        # a dead BB
    LAST = 6        # Sentinel


class Havlak_loop_finder(object):
    """
    Loop Recognition

    based on:
      Paul Havlak, Nesting of Reducible and Irreducible Loops,
         Rice University.

      We adef doing tree balancing and instead use path compression
      to adef traversing parent pointers over and over.

      Most of the variable names and identifiers are taken literally
      from_n this paper (and the original Tarjan paper mentioned above).
    """
    def __init__(self, cfg, lsg):
        self.cfg_ = cfg # current control flow graph.
        self.lsg_ = lsg # loop forest.

    # Constants
    #/ Marker for uninitialized nodes.
    K_UNVISITED = -1

    #/ Safeguard against pathologic algorithm behavior.
    K_MAX_NON_BACK_PREDS = 32 * 1024

    """
    As described in the paper, determine whether a node 'w' is a
    "True" ancestor for node 'v'.

    Dominance can be tested quickly using a pre-order trick
    for depth-first spanning trees. This is why dfs is the first
    thing we run below.
    """
    @staticmethod
    def is_ancestor(w, v, last):
        return w <= v and v <= last[w] # improve this ************************************************

    @staticmethod
    def dfs(current_node, nodes, number, last, current):
        #/ Simple depth first traversal along out edges with node numbering.
        nodes[current].init(current_node, current)
        number[current_node] = current

        lastid = current
        for target in current_node.out_edges_:
            if number[target] == Havlak_loop_finder.K_UNVISITED:
                lastid = Havlak_loop_finder.dfs(target, nodes, number, last, lastid + 1)

        last[number[current_node]] = lastid
        return lastid

    """
    Find loops and build loop forest using Havlak's algorithm, which
    is derived from_n Tarjan. Variable names and step numbering has
    been chosen to be identical to the nomenclature in Havlak's
    paper (which is similar to the one used by Tarjan).
    """
    def find_loops(self):
        if not self.cfg_.start_node_:
            return

        size = len(self.cfg_.basic_block_map_)
        non_back_preds = [set() for _ in range(size)]
        back_preds = [[] for _ in range(size)]
        header = [0] * size
        type = [0] * size
        last = [0] * size
        nodes = [Union_find_node() for _ in range(size)]

        number = {}

        # Step a:
        #   - initialize all nodes as unvisited.
        #   - depth-first traversal and numbering.
        #   - unreached BB's are marked as dead.
        #
        for bblock in self.cfg_.basic_block_map_.values():
            number[bblock] = Havlak_loop_finder.K_UNVISITED

        Havlak_loop_finder.dfs(self.cfg_.start_node_, nodes, number, last, 0)

        # Step b:
        #   - iterate over all nodes.
        #
        #   A backedge comes from_n a descendant in the dfs tree, and non-backedges
        #   from_n non-descendants (following Tarjan).
        #
        #   - check incoming edges 'v' and add them to either
        #     - the list of backedges (back_preds) or
        #     - the list of non-backedges (non_back_preds)
        for w in range(size):
            header[w] = 0
            type[w] = Basic_block_class.NONHEADER

            node_w = nodes[w].bb_
            if not node_w:
                type[w] = Basic_block_class.DEAD
                continue # dead BB

            if len(node_w.in_edges_):
                for node_v in node_w.in_edges_:
                    v = number[node_v]
                    if v == Havlak_loop_finder.K_UNVISITED:
                        continue # dead node

                    if Havlak_loop_finder.is_ancestor(w, v, last):
                        back_preds[w].append(v)
                    else:
                        non_back_preds[w].add(v)

        # Start node is root of all other loops.
        header[0] = 0

        # Step c:
        #
        # The outer loop, unchanged from_n Tarjan. It does nothing except
        # for those nodes which are the destinations of backedges.
        # For a header node w, we chase backward from_n the sources of the
        # backedges adding nodes to the set P, representing the body of
        # the loop headed by w.
        #
        # By running through the nodes in reverse of the DFST preorder,
        # we ensure that inner loop headers will be processed before the
        # headers for surrounding loops.
        for w in range(size-1, -1, -1):
            node_pool = [] # this is 'P' in Havlak's paper
            node_w = nodes[w].bb_
            if not node_w:
                continue # dead BB

            # Step d:
            for back_pred in back_preds[w]:
                if back_pred != w:
                    node_pool.append(nodes[back_pred].find_set())
                else:
                    type[w] = Basic_block_class.SELF

            # Copy node_pool to worklist.
            worklist = []
            for np in node_pool:
                worklist.append(np)

            if len(node_pool):
                type[w] = Basic_block_class.REDUCIBLE

            # work the list...
            #
            while len(worklist):
                x = worklist[0]
                worklist = worklist[1:] # slow? *************************************************

                # Step e:
                #
                # Step e represents the main difference from_n Tarjan's method.
                # Chasing upwards from_n the sources of a node w's backedges. If
                # there is a node y' that is not a descendant of w, w is marked
                # the header of an irreducible loop, there is another entry
                # into this loop that avoids w.

                # The algorithm has degenerated. Break and
                # return in this case.
                non_back_size = len(non_back_preds[x.dfs_number_])
                if non_back_size > Havlak_loop_finder.K_MAX_NON_BACK_PREDS:
                    return

                for non_back_pred_iter in non_back_preds[x.dfs_number_]:
                    y = nodes[non_back_pred_iter]
                    ydash = y.find_set()

                    if not Havlak_loop_finder.is_ancestor(w, ydash.dfs_number_, last):
                        type[w] = Basic_block_class.IRREDUCIBLE
                        non_back_preds[w].add(ydash.dfs_number_)
                    else:
                        if ydash.dfs_number_ != w:
                            if ydash not in node_pool:
                                worklist.append(ydash)
                                node_pool.append(ydash)

            # Collapse/Unionize nodes in a SCC to a single node
            # For every SCC found, create a loop descriptor and link it in.
            #
            if len(node_pool) or type[w] == Basic_block_class.SELF:
                loop = self.lsg_.create_new_loop()

                # At this point, one can set attributes to the loop, such as:
                #
                # the bottom node:
                #    int[]::iterator iter  = back_preds[w].begin()
                #    loop bottom is: nodes[*backp_iter].node)
                #
                # the number of backedges:
                #    back_preds[w].length
                #
                # whether this loop is reducible:
                #    type[w] != IRREDUCIBLE
                #
                # TODO(rhundt): Define those interfaces in the Loop Forest.
                #
                nodes[w].loop_ = loop

                for node in node_pool:
                    # Add nodes to loop descriptor.
                    header[node.dfs_number_] = w
                    node.do_union(nodes[w])

                    # Nested loops are not added, but linked together.
                    if node.loop_:
                        node.loop_.parent_ = loop
                    else:
                        loop.add_node(node.bb_)

                self.lsg_.loops_.append(loop)



def find_havlak_loops(cfg, lsg):
    """External entry point."""
    finder = Havlak_loop_finder(cfg, lsg)
    finder.find_loops()
    return len(lsg.loops_)


def build_diamond(cfg, start):
    bb0 = start
    Basic_block_edge(cfg, bb0, bb0 + 1)
    Basic_block_edge(cfg, bb0, bb0 + 2)
    Basic_block_edge(cfg, bb0 + 1, bb0 + 3)
    Basic_block_edge(cfg, bb0 + 2, bb0 + 3)
    return bb0 + 3


def build_connect(cfg, start, end):
    Basic_block_edge(cfg, start, end)


def build_straight(cfg, start, n):
    for i in range(n):
        build_connect(cfg, start + i, start + i + 1)
    return start + n


def build_base_loop(cfg, from_n):
    header = build_straight(cfg, from_n, 1)
    diamond1 = build_diamond(cfg, header)
    d11 = build_straight(cfg, diamond1, 1)
    diamond2 = build_diamond(cfg, d11)
    footer = build_straight(cfg, diamond2, 1)
    build_connect(cfg, diamond2, d11)
    build_connect(cfg, diamond1, header)
    build_connect(cfg, footer, from_n)
    footer = build_straight(cfg, footer, 1)
    return footer


# --- MOCKING CODE begin -------------------
# These data structures are stubbed out to make the code below easier to review.

class Basic_block_edge(object):
    """Basic_block_edge only maintains two pointers to BasicBlocks."""
    def __init__(self, cfg, from_name, to_name):
        self.from_ = cfg.create_node(from_name)
        self.to_ = cfg.create_node(to_name)
        self.from_.out_edges_.append(self.to_)
        self.to_.in_edges_.append(self.from_)
        cfg.edge_list_.append(self)


class Basic_block(object):
    """Basic_block only maintains a vector of in-edges and a vector of out-edges."""
    def __init__(self, name):
        self.in_edges_ = []
        self.out_edges_ = []
        self.name_ = name


class MaoCFG(object):
    """MaoCFG maintains a list of nodes."""
    def __init__(self):
        self.basic_block_map_ = {}
        self.start_node_ = None
        self.edge_list_ = []

    def create_node(self, name):
        if name in self.basic_block_map_:
            node = self.basic_block_map_[name]
        else:
            node = Basic_block(name)
            self.basic_block_map_[name] = node

        if len(self.basic_block_map_) == 1:
            self.start_node_ = node

        return node

#--- MOCKING CODE end  -------------------


def main():
    print("Welcome to LoopTesterApp, Python edition")
    print("Constructing App...")
    cfg = MaoCFG()
    lsg = Loop_structure_graph()

    print("Constructing Simple cfg...")
    cfg.create_node(0) # top
    build_base_loop(cfg, 0)
    cfg.create_node(1) # bottom
    Basic_block_edge(cfg, 0,  2)

    print("15000 dummy loops")
    for dummyLoops in range(15000):
        lsglocal = Loop_structure_graph()
        find_havlak_loops(cfg, lsglocal)

    print("Constructing cfg...")
    n = 2

    for parlooptrees in range(10):
        cfg.create_node(n + 1)
        build_connect(cfg, 2, n + 1)
        n += 1

        for i in range(100):
            top = n
            n = build_straight(cfg, n, 1)
            for j in range(25):
                n = build_base_loop(cfg, n)
            bottom = build_straight(cfg, n, 1)
            build_connect(cfg, n, top)
            n = bottom
        build_connect(cfg, n, 1)

    print("Performing Loop Recognition\n1 Iteration")
    numLoops = find_havlak_loops(cfg, lsg)

    print("Another 50 iterations...")
    sum = 0
    for i in range(50):
        lsg2 = Loop_structure_graph()
        stdout.write(".")
        sum += find_havlak_loops(cfg, lsg2)

    print("\nFound %d loops (including artificial root node)(%d)" % (numLoops, sum))
    lsg.dump()

if __name__ == '__main__':
    main()
