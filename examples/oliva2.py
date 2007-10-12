### see output oliva.pgm

"""
Models for the simulations of the color pattern on the shells of mollusks
see also: Meinhardt,H. and Klingler,M. (1987) J. theor. Biol 126, 63-69
see also: H.Meinhardt: "Algorithmic beauty of sea shells"
(Springer Verlag) (c) H.Meinhardt, Tubingen

This is a short version of a program for the simulations of the color
patterns on tropical sea shells, here # Oliva porphyria# .
An autocatalytic activator a(i) leads to a burst-like activation
that is regulated back by the action of an inhibitor b(i). The life
time of the inhibitor is regulated via a hormone c, that is
homogeneously distributed along the growing edge. Whenever the number
of activated cells cells become too small, active cells # ain activated
until backwards waves are triggered
------------------

Translated by Bearophile from QBASIC to SSPython (for ShedSkin), V. 1.1, Feb 17 2006.
This program requires Python and ShedSkin (http://shedskin.sourceforge.net).
"""

from random import random, randint


class SavePGMlines:
    """SavePGMlines(matrix, filename): class, saves a PGM, 256 greys for each pixel, line by line.
    Values can be int or float in [0, 255]."""
    def __init__(self, filename, ny):
        self.out_file = file(filename, 'w')
        self.ny = ny
        self.nx = 0 # Unknown
        self.written_lines_count = 0 # lines written count

    def saverow(self, row):
        if self.written_lines_count:
            assert len(row) == self.nx
            assert self.written_lines_count < self.ny
        else:
            self.nx = len(row)
            # PPM header
            print >>self.out_file, "P2"
            print >>self.out_file, "# Image created with ppmlib."
            print >>self.out_file, self.nx, self.ny
            print >>self.out_file, "256"

        out_line = [""] * self.nx
        for i in xrange(self.nx):
            ipixel = int(round(row[i]))
            if ipixel >= 255:
                out_line[i] = "255"
            elif ipixel <= 0:
                out_line[i] = "0"
            else:
                out_line[i] = str(ipixel)

        print >>self.out_file, " ".join(out_line)
        self.written_lines_count +=1
        if self.written_lines_count == self.ny:
            self.out_file.close()



def oliva(nx = 600,   # Length of the computed screen matrix (number of cells)
          ny = 500,   # Height of the computed screen matrix
          kp = 12,    # number of iterations between the displays ( = lines on the screen)
          da = 0.015, # Diffusion of the activator
          ra = 0.1,   # Decay rate of the inhibitor
          ba = 0.1,   # Basic production of the activator
          sa = 0.25,  # Saturation of the autocatalysis
          db = 0.0,   # Diffusion of the inhibitor (example = 0.0)
          rb = 0.014, # Decay rate of the inhibitor
          sb = 0.1,   # Michaelis-Menten constant of the inhibition
          rc = 0.1,   # Decay rate of the hormone
          out_file_name = "oliva.pgm"):

    outPGM = SavePGMlines(out_file_name, ny)
    # ----------- Initial condition  --------------------------
    image_matrix = []   # image_matrix will become an array[ny][nx] of float
    c = 0.5             # Hormone-concentration, homogeneous in all cells
    a = [0.0] * (nx+1)  # Activator, general initial concentration
    b = [0.1] * (nx+1)  # Inhibitor, general initial concentration
    # z = fluctuation of the autocatalysis
    #z = [uniform(ra*0.96, ra*1.04) for i in xrange(nx)] # Not possible with SS yet
    z = [ra * (0.96 + 0.08 * random()) for i in xrange(nx)]

    # Seed the initially active cells, not too much close to each other
    # Example distribution: *              *         *                                        *
    i = 10
    for j in xrange(20):
        a[i] = 1.0
        i += randint(10, 60)
        if i >= nx:
            break

    # These constant factors are used again and again, therefore, they are calculated
    # only once at the begin of the calculation
    dac = 1.0 - ra - 2.0*da
    dbc = 1.0 - rb - 2.0*db
    dbcc = dbc

    for row in xrange(ny):
        # Begin of the iteration
        for niter in xrange(kp):
            # -------- Boundary impermeable
            a1 = a[0] # a1 = concentration  of the actual cell. Since this
                      # concentration is identical, no diffusion through the border.
            b1 = b[0]
            a[nx] = a[nx-1] # Concentration in a virtual right cell
            b[nx] = b[nx-1]
            bsa = 0.0  # This will carry the sum of all activations of all cells

            # ---------- Reactions  ------
            for i in xrange(nx): # i = actual cell, kx = right cell
                af = a[i] # local activator concentration
                bf = b[i] # local inhibitor concentration
                aq = z[i] * af * af / (1.0 + sa * af * af)  # Saturating autocatalysis

                # Calculation of the new activator and inhibitor concentration in cell i:
                a[i] = af * dac + da * (a1 + a[i + 1]) + aq / (sb + bf)
                # 1/BF => Action of the inhibitor
                b[i] = bf * dbcc + db * (b1 + b[i + 1]) + aq # new inhibitor conc.
                bsa += rc * af # Hormone production -> Sum of activations
                a1 = af # actual concentration will be concentration in left cell
                b1 = bf # in the concentration change of the next cell

            # New hormone concentration. 1/kx=normalization on total number of cells
            c = c * (1.0 - rc) + bsa/nx
            rbb = rb / c # rbb => Effective life time of the inhibitor

            # Change in a cell by diffusion and decay. Must be recomputed since
            # lifetime of the inhibitor changes.
            dbcc = 1.0 - 2.0*db - rbb

        # ----------- Plot-Save -------------
        outPGM.saverow( [255 * a[ix] for ix in xrange(nx)] )

#import psyco; psyco.full()
oliva()

"""
Timings, nx,ny = 600, 500:
Python: 44.5 s      21.5 X
Psyco: 8.8 s         4.2 X
SS NOWRAP: 2.07 s    1   X
"""
