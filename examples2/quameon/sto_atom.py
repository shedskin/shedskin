#!/usr/bin/python

"""\
  single_atom - Compute the ground state energy for a single atom

"""

# Copyright (C) 2006, Mark Dewing
# http://quameon.sourceforge.net/
# Quameon is covered under the GNU General Public License.  Please see the
# file LICENSE that is part of this distribution.

import math
import random
#import scipy.optimize

import wave_func
import qmc_loop
from stats import average
from orbital import atomic_sto,lcao,create_orbital
from jastrow import const_jastrow, simple_pade
from observables import en_dist,ee_dist
from coulomb import coulomb_pot

# name,  nuclear charge,  electons

atoms = [
('H',(1,1)),
('He',(2,2)),
('Li',(3,3)),
('Li+',(3,2)),
('Be',(4,4)),
('B',(5,5)),
('C',(6,6)),
('N',(7,7)),
('O',(8,8)),
('F',(9,9)),
('Ne',(10,10))
]


def find_atom(name):
  for atom in atoms:
    if atom[0] == name:
      return atom
  return None

def run_qmc():
   #import psyco
   #psyco.full()
   random.seed(130)

   qmcl = qmc_loop.qmc_loop()
   atom_name = 'He'
   print('Atom = ',atom_name)
   atom = find_atom(atom_name)
   nelec = atom[1][1]
   for n in range(nelec):
     epos = []
     for i in range(3):
       epos.append(random.uniform(-1,1))
     qmcl.add_epos(epos)
   qmcl.wavef = wave_func.wave_func_single_det()
   charges = [atom[1][0]]
   print('nuclear charges = ',charges)

   # use these for testing - should get the HF energy
   qmcl.wavef.ee_wv.func = const_jastrow.const_jastrow()
   qmcl.wavef.en_wv.func = const_jastrow.const_jastrow()

   p = [0.0, 0.0, 0.0]
   qmcl.wavef.set_orbital(lcao.LCAO())
   qmcl.wavef.orb.coeff = [[1.0, 0.0],[0.0, 1.0]]
   orbs = create_orbital.create_sto_orbs([(atom[1],p)])
   qmcl.wavef.orb.orbs = orbs


   old_vp = qmcl.wavef.get_vp()
   new_vp = [0.0046,0.0,1.0,2.0]
   qmcl.wavef.set_vp(new_vp)

   npos = [p]
   en_d = en_dist.en_dist(npos)
   ee_d = ee_dist.ee_dist()
   qmcl.wavef.set_npos(npos)
   qmcl.wavef.pot = coulomb_pot(npos,charges)
   qmcl.nblock = 10
   qmcl.nstep = 10
   qmcl.compute_energy()
   print('after warm-up, average energy',qmcl.ave_e.average(),qmcl.ave_e.error())



   qmcl.nstep = 20

   #  Increase this number to make the run longer
   qmcl.nblock = 1000

   qmcl.add_observable(en_d)
   qmcl.compute_energy()
   qmcl.en_file = None
   en = qmcl.ave_e.average()
   print('energy, average energy',qmcl.ave_e.average(),qmcl.ave_e.error())
   kin_e = qmcl.ave_kin_e.average()
   kin_e_err = qmcl.ave_kin_e.error()
   pot_e = qmcl.ave_pot_e.average()
   pot_e_err = qmcl.ave_pot_e.error()
   print('kinetic energy',kin_e,kin_e_err)
   print('-.5*potential energy',-0.5*pot_e,0.5*pot_e_err)
   print('virial error',kin_e + 0.5*pot_e,math.sqrt(kin_e_err**2 + 0.25*pot_e_err**2))

   print('acceptance ratio = ',qmcl.accept_ratio())


if __name__ == '__main__':
  run_qmc()

