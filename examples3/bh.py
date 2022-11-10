"""
A Python implementation of the _bh_ Olden benchmark.
The Olden benchmark implements the Barnes-Hut benchmark
that is decribed in:

J. Barnes and P. Hut, "A hierarchical o(N log N) force-calculation algorithm",
Nature, 324:446-449, Dec. 1986

The original code in the Olden benchmark suite is derived from the
ftp://hubble.ifa.hawaii.edu/pub/barnes/treecode
source distributed by Barnes.

This code comes from the third Java version.
This uses copy() instead of Vec3.clone(), and it's adapted for ShedSkin.
"""

from time import time as clock 
from sys import stderr, maxsize, argv
from copy import copy
from math import sqrt, pi, floor




class Random:
    """
    Basic uniform random generator: Minimal Standard in Park and
    Miller (1988): "Random Number Generators: Good Ones Are Hard to
    Find", Comm. of the ACM, 31, 1192-1201.
    Parameters: m = 2^31-1, a=48271.

    Adapted from Pascal code by Jesper Lund:
    http:#www.gnu-pascal.de/crystal/gpc/en/mail1390.html
    """
    __slots__ = ["seed"]
    m = maxsize
    a = 48271
    q = m // a
    r = m % a

    def __init__(self, the_seed):
        self.seed = the_seed

    def uniform(self, min, max):
        k = self.seed // Random.q
        self.seed = Random.a * (self.seed - k * Random.q) - Random.r * k
        if self.seed < 1:
            self.seed += Random.m
        r = float(self.seed) / Random.m
        return r * (max - min) + min


class Vec3:
    """
    A class representing a three dimensional vector that implements
    several math operations.  To improve speed we implement the
    vector as an array of doubles rather than use the exising
    code in the java.util.class.
    """
    __slots__ = ["d0", "d1", "d2"]
    # The number of dimensions in the vector
    NDIM = 3

    def __init__(self):
        """Construct an empty 3 dimensional vector for use in Barnes-Hut algorithm."""
        self.d0 = 0.0
        self.d1 = 0.0
        self.d2 = 0.0

    def __getitem__(self, i):
        """
        Return the value at the i'th index of the vector.
        @param i the vector index
        @return the value at the i'th index of the vector.
        """
        if i == 0:
            return self.d0
        elif i == 1:
            return self.d1
        else:
            return self.d2

    def __setitem__(self, i, v):
        """
        Set the value of the i'th index of the vector.
        @param i the vector index
        @param v the value to store
        """
        if i == 0:
            self.d0 = v
        elif i == 1:
            self.d1 = v
        else:
            self.d2 = v

    def __iadd__(self, u):
        """
        Add two vectors and the result is placed in self vector.
        @param u the other operand of the addition
        """
        self.d0 += u.d0
        self.d1 += u.d1
        self.d2 += u.d2
        return self

    def __isub__(self, u):
        """
        Subtract two vectors and the result is placed in self vector.
        This vector contain the first operand.
        @param u the other operand of the subtraction.
        """
        self.d0 -= u.d0
        self.d1 -= u.d1
        self.d2 -= u.d2
        return self

    def __imul__(self, s):
        """
        Multiply the vector times a scalar.
        @param s the scalar value
        """
        self.d0 *= s
        self.d1 *= s
        self.d2 *= s
        return self

    # def __idiv__(self, s):
    def __itruediv__(self, s):
        """
        Divide each element of the vector by a scalar value.
        @param s the scalar value.
        """
        self.d0 /= s
        self.d1 /= s
        self.d2 /= s
        return self

    def add_scalar(self, u, s):
        self.d0 = u.d0 + s
        self.d1 = u.d1 + s
        self.d2 = u.d2 + s

    def subtraction2(self, u, v):
        """
        Subtract two vectors and the result is placed in self vector.
        @param u the first operand of the subtraction.
        @param v the second opernd of the subtraction
        """
        self.d0 = u.d0 - v.d0
        self.d1 = u.d1 - v.d1
        self.d2 = u.d2 - v.d2

    def mult_scalar2(self, u, s):
        """
        Multiply the vector times a scalar and place the result in self vector.
        @param u the vector
        @param s the scalar value
        """
        self.d0 = u.d0 * s
        self.d1 = u.d1 * s
        self.d2 = u.d2 * s

    def dot(self):
        """
        Return the dot product of a vector.
        @return the dot product of a vector.
        """
        return self.d0 * self.d0 + self.d1 * self.d1 + self.d2 * self.d2

    def __repr__(self):
        return "%.17f %.17f %.17f " % (self.d0, self.d1, self.d2)


class HG:
    """
    A sub class which is used to compute and save information during the
    gravity computation phase.
    """
    __slots__ = ["pskip", "pos0", "phi0", "acc0"]
    def __init__(self, b, p):
        """
        Create a  object.
        @param b the body object
        @param p a vector that represents the body
        """
        # Body to skip in force evaluation
        self.pskip = b

        # Poat which to evaluate field
        self.pos0 = copy(p)

        # Computed potential at pos0
        self.phi0 = 0.0

        # computed acceleration at pos0
        self.acc0 = Vec3()


class Node(object):
    """A class that represents the common fields of a cell or body data structure."""
    # highest bit of coord
    IMAX = 1073741824

    # potential softening parameter
    EPS = 0.05

    def __init__(self):
        """Construct an empty node"""
        self.mass = 0.0 # mass of the node
        self.pos = Vec3() # Position of the node

    def load_tree(self, p, xpic, l, root):
        raise NotImplementedError()

    def hack_cofm(self):
        raise NotImplementedError()

    def walk_sub_tree(self, dsq, hg):
        raise NotImplementedError()

    @staticmethod
    def old_sub_index(ic, l):
        i = 0
        for k in range(Vec3.NDIM):
            if (int(ic[k]) & l) != 0:
                i += Cell.NSUB >> (k + 1)
        return i

    def __repr__(self):
        return "%f : %f" % (self.mass, self.pos)

    def grav_sub(self, hg):
        """Compute a single body-body or body-cell interaction"""
        dr = Vec3()
        dr.subtraction2(self.pos, hg.pos0)

        drsq = dr.dot() + (Node.EPS * Node.EPS)
        drabs = sqrt(drsq)

        phii = self.mass / drabs
        hg.phi0 -= phii
        mor3 = phii / drsq
        dr *= mor3
        hg.acc0 += dr
        return hg


class Body(Node):
    """A class used to representing particles in the N-body simulation."""
    def __init__(self):
        """Create an empty body."""
        Node.__init__(self)
        self.vel = Vec3()
        self.acc = Vec3()
        self.new_acc = Vec3()
        self.phi = 0.0

    def expand_box(self, tree, nsteps):
        """
        Enlarge cubical "box", salvaging existing tree structure.
        @param tree the root of the tree.
        @param nsteps the current time step
        """
        rmid = Vec3()

        inbox = self.ic_test(tree)
        while not inbox:
            rsize = tree.rsize
            rmid.add_scalar(tree.rmin, 0.5 * rsize)

            for k in range(Vec3.NDIM):
                if self.pos[k] < rmid[k]:
                    rmin = tree.rmin[k]
                    tree.rmin[k] = rmin - rsize

            tree.rsize = 2.0 * rsize
            if tree.root is not None:
                ic = tree.int_coord(rmid)
                if ic is None:
                    raise Exception("Value is out of bounds")
                k = Node.old_sub_index(ic, Node.IMAX >> 1)
                newt = Cell()
                newt.subp[k] = tree.root
                tree.root = newt
                inbox = self.ic_test(tree)

    def ic_test(self, tree):
        """Check the bounds of the body and return True if it isn't in the correct bounds."""
        pos0 = self.pos[0]
        pos1 = self.pos[1]
        pos2 = self.pos[2]

        # by default, it is in bounds
        result = True

        xsc = (pos0 - tree.rmin[0]) / tree.rsize
        if not (0.0 < xsc and xsc < 1.0):
            result = False

        xsc = (pos1 - tree.rmin[1]) / tree.rsize
        if not (0.0 < xsc and xsc < 1.0):
            result = False

        xsc = (pos2 - tree.rmin[2]) / tree.rsize
        if not (0.0 < xsc and xsc < 1.0):
            result = False

        return result

    def load_tree(self, p, xpic, l, tree):
        """
        Descend and insert particle.  We're at a body so we need to
        create a cell and attach self body to the cell.
        @param p the body to insert
        @param xpic
        @param l
        @param tree the root of the data structure
        @return the subtree with the body inserted
        """
        # create a Cell
        retval = Cell()
        si = self.sub_index(tree, l)
        # attach self node to the cell
        retval.subp[si] = self

        # move down one level
        si = Node.old_sub_index(xpic, l)
        rt = retval.subp[si]
        if rt is not None:
            retval.subp[si] = rt.load_tree(p, xpic, l >> 1, tree)
        else:
            retval.subp[si] = p
        return retval

    def hack_cofm(self):
        """
        Descend tree finding center of mass coordinates
        @return the mass of self node
        """
        return self.mass

    def sub_index(self, tree, l):
        """
        Determine which subcell to select.
        Combination of int_coord and old_sub_index.
        @param t the root of the tree
        """
        xp = Vec3()

        xsc = (self.pos[0] - tree.rmin[0]) / tree.rsize
        xp[0] = floor(Node.IMAX * xsc)

        xsc = (self.pos[1] - tree.rmin[1]) / tree.rsize
        xp[1] = floor(Node.IMAX * xsc)

        xsc = (self.pos[2] - tree.rmin[2]) / tree.rsize
        xp[2] = floor(Node.IMAX * xsc)

        i = 0
        for k in range(Vec3.NDIM):
            if (int(xp[k]) & l) != 0:
                i += Cell.NSUB >> (k + 1)
        return i

    def hack_gravity(self, rsize, root):
        """
        Evaluate gravitational field on the body.
        The original olden version calls a routine named "walkscan",
        but we use the same name that is in the Barnes code.
        """
        hg = HG(self, self.pos)
        hg = root.walk_sub_tree(rsize * rsize, hg)
        self.phi = hg.phi0
        self.new_acc = hg.acc0

    def walk_sub_tree(self, dsq, hg):
        """Recursively walk the tree to do hackwalk calculation"""
        if self != hg.pskip:
            hg = self.grav_sub(hg)
        return hg

    def __repr__(self):
        """
        Return a string represenation of a body.
        @return a string represenation of a body.
        """
        return "Body " + Node.__repr__(self)


class Cell(Node):
    """A class used to represent internal nodes in the tree"""
    # subcells per cell
    NSUB = 8 # 1 << NDIM

    def __init__(self):
        # The children of self cell node.  Each entry may contain either
        # another cell or a body.
        Node.__init__(self)
        self.subp = [None] * Cell.NSUB

    def load_tree(self, p, xpic, l, tree):
        """
        Descend and insert particle.  We're at a cell so
        we need to move down the tree.
        @param p the body to insert into the tree
        @param xpic
        @param l
        @param tree the root of the tree
        @return the subtree with the body inserted
        """
        # move down one level
        si = Node.old_sub_index(xpic, l)
        rt = self.subp[si]
        if rt is not None:
            self.subp[si] = rt.load_tree(p, xpic, l >> 1, tree)
        else:
            self.subp[si] = p
        return self

    def hack_cofm(self):
        """
        Descend tree finding center of mass coordinates
        @return the mass of self node
        """
        mq = 0.0
        tmp_pos = Vec3()
        tmpv = Vec3()
        for i in range(Cell.NSUB):
            r = self.subp[i]
            if r is not None:
                mr = r.hack_cofm()
                mq = mr + mq
                tmpv.mult_scalar2(r.pos, mr)
                tmp_pos += tmpv
        self.mass = mq
        self.pos = tmp_pos
        self.pos /= self.mass
        return mq


    def walk_sub_tree(self, dsq, hg):
        """Recursively walk the tree to do hackwalk calculation"""
        if self.subdiv_p(dsq, hg):
            for k in range(Cell.NSUB):
                r = self.subp[k]
                if r is not None:
                    hg = r.walk_sub_tree(dsq / 4.0, hg)
        else:
            hg = self.grav_sub(hg)
        return hg

    def subdiv_p(self, dsq, hg):
        """
        Decide if the cell is too close to accept as a single term.
        @return True if the cell is too close.
        """
        dr = Vec3()
        dr.subtraction2(self.pos, hg.pos0)
        drsq = dr.dot()

        # in the original olden version drsp is multiplied by 1.0
        return drsq < dsq

    def __repr__(self):
        """
        Return a string represenation of a cell.
        @return a string represenation of a cell.
        """
        return "Cell " + Node.__repr__(self)


class Tree:
    """
    A class that represents the root of the data structure used
    to represent the N-bodies in the Barnes-Hut algorithm.
    """
    def __init__(self):
        """Construct the root of the data structure that represents the N-bodies."""
        self.bodies = [] # The complete list of bodies that have been created.
        self.rmin = Vec3()
        self.rsize = -2.0 * -2.0
        self.root = None # A reference to the root node.
        self.rmin[0] = -2.0
        self.rmin[1] = -2.0
        self.rmin[2] = -2.0

    def create_test_data(self, nbody):
        """
        Create the testdata used in the benchmark.
        @param nbody the number of bodies to create
        """
        cmr = Vec3()
        cmv = Vec3()

        rsc = 3.0 * pi / 16.0
        vsc = sqrt(1.0 / rsc)
        seed = 123
        rnd = Random(seed)
        self.bodies = [None] * nbody
        aux_mass = 1.0 / float(nbody)

        for i in range(nbody):
            p = Body()
            self.bodies[i] = p
            p.mass = aux_mass

            t1 = rnd.uniform(0.0, 0.999)
            t1 = pow(t1, (-2.0 // 3.0)) - 1.0
            r = 1.0 / sqrt(t1)

            coeff = 4.0
            for k in range(Vec3.NDIM):
                r = rnd.uniform(0.0, 0.999)
                p.pos[k] = coeff * r

            cmr += p.pos

            while True:
                x = rnd.uniform(0.0, 1.0)
                y = rnd.uniform(0.0, 0.1)
                if y <= (x * x * pow(1.0 - x * x, 3.5)):
                    break
            v = sqrt(2.0) * x / pow(1 + r * r, 0.25)

            rad = vsc * v
            while True:
                for k in range(Vec3.NDIM):
                    p.vel[k] = rnd.uniform(-1.0, 1.0)
                rsq = p.vel.dot()
                if rsq <= 1.0:
                    break
            rsc1 = rad / sqrt(rsq)
            p.vel *= rsc1
            cmv += p.vel

        cmr /= float(nbody)
        cmv /= float(nbody)

        for b in self.bodies:
            b.pos -= cmr
            b.vel -= cmv

    def step_system(self, nstep):
        """
        Advance the N-body system one time-step.
        @param nstep the current time step
        """
        # free the tree
        self.root = None

        self.make_tree(nstep)

        # compute the gravity for all the particles
        for b in reversed(self.bodies):
            b.hack_gravity(self.rsize, self.root)
        Tree.vp(self.bodies, nstep)

    def make_tree(self, nstep):
        """
        Initialize the tree structure for hack force calculation.
        @param nsteps the current time step
        """
        for q in reversed(self.bodies):
            if q.mass != 0.0:
                q.expand_box(self, nstep)
                xqic = self.int_coord(q.pos)
                if self.root is None:
                    self.root = q
                else:
                    self.root = self.root.load_tree(q, xqic, Node.IMAX >> 1, self)
        self.root.hack_cofm()

    def int_coord(self, vp):
        """
        Compute integerized coordinates.
        @return the coordinates or None if rp is out of bounds
        """
        xp = Vec3()

        xsc = (vp[0] - self.rmin[0]) / self.rsize
        if 0.0 <= xsc and xsc < 1.0:
            xp[0] = floor(Node.IMAX * xsc)
        else:
            return None

        xsc = (vp[1] - self.rmin[1]) / self.rsize
        if 0.0 <= xsc and xsc < 1.0:
            xp[1] = floor(Node.IMAX * xsc)
        else:
            return None

        xsc = (vp[2] - self.rmin[2]) / self.rsize
        if 0.0 <= xsc and xsc < 1.0:
            xp[2] = floor(Node.IMAX * xsc)
        else:
            return None

        return xp

    @staticmethod
    def vp(bodies, nstep):
        dacc = Vec3()
        dvel = Vec3()
        dthf = 0.5 * BH.DTIME

        for b in reversed(bodies):
            acc1 = copy(b.new_acc)
            if nstep > 0:
                dacc.subtraction2(acc1, b.acc)
                dvel.mult_scalar2(dacc, dthf)
                dvel += b.vel
                b.vel = copy(dvel)

            b.acc = copy(acc1)
            dvel.mult_scalar2(b.acc, dthf)

            vel1 = copy(b.vel)
            vel1 += dvel
            dpos = copy(vel1)
            dpos *= BH.DTIME
            dpos += b.pos
            b.pos = copy(dpos)
            vel1 += dvel
            b.vel = copy(vel1)


class BH(object):
    DTIME = 0.0125
    TSTOP = 2.0

    # The user specified number of bodies to create.
    nbody = 0

    # The maximum number of time steps to take in the simulation
    nsteps = 10

    # Should we prinformation messsages
    print_msgs = False

    # Should we prdetailed results
    print_results = False

    @staticmethod
    def main(args):
        BH.parse_cmd_line(args)

        if BH.print_msgs:
            print("nbody =", BH.nbody)

        start0 = clock()
        root = Tree()
        root.create_test_data(BH.nbody)
        end0 = clock()
        if BH.print_msgs:
              print("Bodies created")

        start1 = clock()
        tnow = 0.0
        i = 0
        while (tnow < BH.TSTOP + 0.1 * BH.DTIME) and i < BH.nsteps:
            root.step_system(i)
            i += 1
            tnow += BH.DTIME
        end1 = clock()

        if BH.print_results:
            for j, b in enumerate(root.bodies):
                print("body %d: %s" % (j, b.pos))

        if BH.print_msgs:
            print("Build Time %.3f" % (end0 - start0))
            print("Compute Time %.3f" % (end1 - start1))
            print("Total Time %.3f" % (end1 - start0))
        print("Done!")

    @staticmethod
    def parse_cmd_line(args):
        i = 1
        while i < len(args) and args[i].startswith("-"):
            arg = args[i]
            i += 1

            # check for options that require arguments
            if arg == "-b":
                if i < len(args):
                    BH.nbody = int(args[i])
                    i += 1
                else:
                    raise Exception("-l requires the number of levels")
            elif arg == "-s":
                if i < len(args):
                    BH.nsteps = int(args[i])
                    i += 1
                else:
                    raise Exception("-l requires the number of levels")
            elif arg == "-m":
                BH.print_msgs = True
            elif arg == "-p":
                BH.print_results = True
            elif arg == "-h":
                BH.usage()

        if BH.nbody == 0:
            BH.usage()

    @staticmethod
    def usage():
        """The usage routine which describes the program options."""
        print("usage: python bh.py -b <size> [-s <steps>] [-p] [-m] [-h]", file=stderr)
        print("  -b the number of bodies", file=stderr)
        print("  -s the max. number of time steps (default=10)", file=stderr)
        print("  -p (print detailed results)", file=stderr)
        print("  -m (print information messages", file=stderr)
        print("  -h (self message)", file=stderr)
        raise SystemExit()


if __name__ == '__main__':
    BH.main(argv)
