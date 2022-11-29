#!/usr/bin/python

"""\
  atomic_sto.py - Slater Type Orbitals
"""

# Copyright (c) 2007, Mark Dewing
# Quameon is covered under the GNU General Public License.  Please see the
# file LICENSE that is part of this distribution.

import box_bc
import math
from . import atomic_sto_primitive
from .orbital_base import orbital_base


class atomic_STO(orbital_base):
  def __init__(self):
    self.exp = 0.5
    self.primitive = atomic_sto_primitive.s()
    self.npos = [[0.0,0.0,0.0]]
    self.npos_idx = 0
    self.box = box_bc.box_nopbc()
    self.norm = 1.0

#  def set_npos_idx(self,idx):
#    pass
#
#  def set_npos(self,npos):
#    pass

  def set_exp_coeff(self,exp,coeff,orb_type,npos):
    self.coeff = coeff
    self.exp = exp
    if orb_type == 's':
      self.primitive = atomic_sto_primitive.s()

    if orb_type == 'px':
      self.primitive = atomic_sto_primitive.px()
    if orb_type == 'py':
      self.primitive = atomic_sto_primitive.py()
    if orb_type == 'pz':
      self.primitive = atomic_sto_primitive.pz()

    # cartesian d functions

    if orb_type == 'dx2':
      self.primitive = atomic_sto_primitive.dx2()
    if orb_type == 'dy2':
      self.primitive = atomic_sto_primitive.dy2()
    if orb_type == 'dz2':
      self.primitive = atomic_sto_primitive.dz2()
    if orb_type == 'dxy':
      self.primitive = atomic_sto_primitive.dxy()
    if orb_type == 'dxz':
      self.primitive = atomic_sto_primitive.dxz()
    if orb_type == 'dyz':
      self.primitive = atomic_sto_primitive.dyz()

    # canonical d functions (the two linear combinations)

    if orb_type == 'dx2y2':
      self.primitive = atomic_sto_primitive.dx2y2()
    if orb_type == 'd3z2r2':
      self.primitive = atomic_sto_primitive.d3z2r2()

#  def normalize(self):
#    overlap = 0.0
#    return 1.0

    #for c in self.coeff:
    #  overlap += c*c

    #n = len(self.coeff)
    #for i in range(n):
    #  for j in range(i):
    #    a1 = self.exp[i]
    #    a2 = self.exp[j]
    #    ovlp = (2/(a1+a2))**(3.0/2)*(a1*a2)**(3.0/4)
    #    overlap += 2*self.coeff[i]*self.coeff[j]*ovlp
    #
    #print 'qmc overlap = ',overlap
    #self.norm = 1/math.sqrt(overlap)

  def get_coords(self,p):
    (vec,r) = self.box.dist_v(p,self.npos[self.npos_idx])
    return vec[0],vec[1],vec[2],r*r

  def compute_value(self,p,n_orb):
    (x,y,z,r2) = self.get_coords(p)
    val = self.primitive.compute_value(self.exp,[x,y,z])
    return [val]

  def compute_value2(self,p,n_orb):
    (vec,r) = self.box.dist_v(p,self.npos[self.npos_idx])
    return self.primitive.compute_value(self.exp,vec)

  def compute_del(self,p,n_orb):
    (x,y,z,r2) = self.get_coords(p)
    val = self.primitive.compute_del(self.exp,[x,y,z])
    return [val]

  def compute_del_sq(self,p,n_orb):
    (x,y,z,r2) = self.get_coords(p)
    val = self.primitive.compute_del_sq(self.exp,[x,y,z])
    return [val]

  def get_vp(self):
    return [self.exp]

  def set_vp(self,vp):
    self.exp = vp[0]
    return None

