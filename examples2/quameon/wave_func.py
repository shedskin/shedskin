#!/usr/bin/python

"""\
  wave_func.py - compute the wave fuction and local energy
"""

# Copyright (C) 2006-2007, Mark Dewing
# http://quameon.sourceforge.net/
# Quameon is covered under the GNU General Public License.  Please see the
# file LICENSE that is part of this distribution.

import box_bc
import math
from jastrow import simple_pade, const_jastrow
#from orbital import floating_gaussian
from orbital import lcao
from coulomb import coulomb_pot
from sum_jastrow import ee_jastrow, en_jastrow
import fermion

# general single determinant wavefunction 

class wave_func_single_det:
  def __init__(self): 
    self.npos = [[0.0,0.0,1.0]]
    self.ee_wv = ee_jastrow()
    self.en_wv = en_jastrow(self.npos)
    self.pot = coulomb_pot(self.npos)
    self.orb =  lcao.LCAO()
    self.fermion = fermion.fermion(self.orb)
    self.vp_size_set = False

  def set_npos(self,npos):
    if self.en_wv:
      self.en_wv.set_npos(npos)
    if self.pot:
      self.pot.set_npos(npos)

#  def set_ee_jastrow(self,new_ee_jastrow):
#    self.ee_wv = new_ee_jastrow

#  def set_en_jastrow(self,new_en_jastrow):
#    self.en_wv = new_en_jastrow
#    self.en_wv.set_npos(npos)

  def set_orbital(self,orb):
    self.orb = orb
    self.fermion.set_orbital(self.orb)

  def get_vp(self):
    ee_vp = self.ee_wv.get_vp()
    self.ee_vp_size = len(ee_vp)
    en_vp = self.en_wv.get_vp()
    self.en_vp_size = len(en_vp)
    orb_vp = self.orb.get_vp()
    self.orb_vp_size = len(orb_vp)
    self.vp_size_set = True
    #vp = ee_vp + en_vp + orb_vp
    #vp = [ee_vp[0],en_vp[0],orb_vp[0]]
    vp = []
    for p in ee_vp:
      vp.append(p)
    for p in en_vp:
      vp.append(p)
    for p in orb_vp:
      vp.append(p)
    # this next line doesn't work sometimes, hence the preceeding mess
    #vp = ee_vp + en_vp + orb_vp
    return vp

  def set_vp(self,vp):
    if not(self.vp_size_set):
      self.get_vp()
    ee_vp = vp[:self.ee_vp_size]
    en_vp = vp[self.ee_vp_size:(self.ee_vp_size + self.en_vp_size)]
    orb_vp = vp[(self.en_vp_size + self.ee_vp_size):]
    self.ee_wv.set_vp(ee_vp)
    self.en_wv.set_vp(en_vp)
    self.orb.set_vp(orb_vp)

#  def satisfies_constraints(self,vp):
#    if not(self.vp_size_set):
#      get_vp()
#    ee_vp = vp[:self.ee_vp_size]
#    en_vp = vp[self.ee_vp_size:(self.ee_vp_size + self.en_vp_size)]
#    orb_vp = vp[(self.en_vp_size + self.ee_vp_size):]
#    okay = True
#    okay = self.ee_wv.satisfies_constraints(ee_vp)
#    if okay:
#      okay = self.en_wv.satisfies_constraints(en_vp)
#    if okay:
#      okay = self.orb.satisfies_constraints(orb_vp)
#    return okay

  def compute_jastrow_log_value(self,epos,p,idx):
    ee_wv = self.ee_wv.compute_value(epos,p,idx)
    en_wv = self.en_wv.compute_value(p)
    return 0.5*ee_wv + en_wv

  def compute_log_ratio(self,epos,p,idx):
    old_psi = self.compute_jastrow_log_value(epos,epos[idx],idx)
    new_psi = self.compute_jastrow_log_value(epos,p,idx)
    det_ratio = self.fermion.compute_log_ratio(epos,p,idx)
    return new_psi - old_psi + det_ratio

  def compute_partial_log_value(self,epos):
    val = 0.0
    for i in range(len(epos)):
      val += self.compute_jastrow_log_value(epos,epos[i],i)
    #val += self.fermion.compute_log_value(epos)
    return val

#  def compute_total_log_value(self,epos):
#    j_val = self.compute_partial_log_value(epos)
#    det_orig = self.fermion.compute_value(epos)
# 
#    try:
#      val = j_val*math.log(abs(det_orig))
#    except OverflowError:
#      val = 0.0
#    return val

  def local_energy(self,epos):
    pot_e = 0.0
    pot_e += self.pot.compute_ee_value(epos)
    pot_e += self.pot.compute_en_value(epos)
    pot_e += self.pot.compute_nn_value()
    kin_e = 0.0
    for i in range(len(epos)):
      del_sq = 0.0
      del_sq += self.ee_wv.compute_del_sq(epos,epos[i],i)
      del_sq += self.en_wv.compute_del_sq(epos[i])
      del_sq += self.fermion.compute_del_sq(epos,i)
      du = self.ee_wv.compute_del(epos,epos[i],i)
      dudu = [0.0,0.0,0.0]
      for j in range(len(dudu)):
        dudu[j] += du[j]
      du = self.en_wv.compute_del(epos[i])
      for j in range(len(dudu)):
        dudu[j] += du[j]

      orb_dot = 0.0
      orb_du = self.fermion.compute_del(epos,i)
      for j in range(len(dudu)):
        orb_dot += dudu[j]*orb_du[j]

      dot = 0.0
      for j in range(len(dudu)):
        dot += dudu[j]*dudu[j]
      kin_e += -.5*del_sq - .5*dot - orb_dot
    loc_e = kin_e + pot_e
    return loc_e,kin_e,pot_e

  def local_energy_num(self,epos,h=1e-4):
     val = 0.0
     pot_e = 0.0
     pot_e += self.pot.compute_ee_value(epos)
     pot_e += self.pot.compute_en_value(epos)
     pot_e += self.pot.compute_nn_value()
     kin_e = 0.0
     for i in range(len(epos)):
       deriv = 0.0
       val = self.compute_partial_log_value(epos)
       det_orig = self.fermion.compute_value(epos)
       for j in range(len(epos[0])):
         epos[i][j] += h
         val_p = self.compute_partial_log_value(epos)
         det_p = self.fermion.compute_value(epos)
         epos[i][j] += -2*h
         val_m = self.compute_partial_log_value(epos)
         det_m = self.fermion.compute_value(epos)
         epos[i][j] += h
         arg_p = val_p - val
         arg_m = val_m - val
         deriv += math.exp(arg_p)*det_p/det_orig + math.exp(arg_m)*det_m/det_orig - 2.0
       kin_e -= deriv/(h*h)/2.0
     num_loc_e = kin_e + pot_e
     return num_loc_e,kin_e,pot_e


#def test_orb_derivs(epos):
#  pass
  

if __name__ == '__main__':
  #npos = [[0.0,0.0,0.0],[0.0,0.0,1.4]]
  npos = [[0.0,0.0,0.0]]
  epos = [[0.0,0.0,0.0],[0.0,0.0,1.0]]
  #cp = coulomb_pot(npos)
  #print cp.compute_nn_value(),1.0/1.4
  #print cp.compute_en_value(epos),-4.0/0.7
  #print cp.compute_ee_value(epos)
  wv = wave_func_single_det()
  print(wv.local_energy(epos))
  print(wv.local_energy_num(epos))
