#!/usr/bin/python

"""\
  coulomb.py - compute the electrostatic interation energy (e-e, e-n, n-n)
"""

# Copyright (C) 2006-2007, Mark Dewing
# http://quameon.sourceforge.net/
# Quameon is covered under the GNU General Public License.  Please see the
# file LICENSE that is part of this distribution.

import box_bc
import math

class coulomb_pot:
  def __init__(self,npos=[],charges=None):
    self.npos = npos
    if charges == None:
      self.charges = []
      for n in npos:
        self.charges.append(1.0)
    else:
      self.charges = charges
    self.box = box_bc.box_nopbc()
    self.nn_pot = 0.0
    self.nn_okay = False

  def set_npos(self,npos):
    self.npos = npos
    self.nn_okay = False

  def compute_ee_value(self,epos):
    pot = 0.0
    for i in range(len(epos)):
      for j in range(i):
        r = self.box.dist(epos[j],epos[i])
        pot += 1.0/r
    return pot

  def compute_en_value(self,epos):
    pot = 0.0
    for i in range(len(epos)):
      for j in range(len(self.npos)):
        r = self.box.dist(epos[i],self.npos[j])
        Z = self.charges[j]
        pot += Z/r
    return -pot

  def compute_nn_value(self):
    if not(self.nn_okay):
      pot = 0.0
      for i in range(len(self.npos)):
        Z1 = self.charges[i]
        for j in range(i):
          Z2 = self.charges[j]
          r = self.box.dist(self.npos[j],self.npos[i])
          pot += Z1*Z2/r
      print('n-n potential energy = ',pot)
      self.nn_pot = pot
      self.nn_okay = True
    return self.nn_pot
