#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

import sys
import memory

class SID(memory.Memory):
	def __init__(self):
		self.B_active = True
		self.B_can_write = True # in the instance because of ShedSkin
		pass

	#@takes(int, int)
	def read_memory(self, address, size):
		sys.stderr.write("error: SID: do you really think this works? No.\n")
		return 0xFF # FIXME

	#@takes(int, int)
	def write_memory(self, address, value, size):
		print("SID $%X := %r" % (address, value))

"""
$D400-$D401
54272-54273	

Voice #1 frequency.
Write-only.
$D402-$D403
54274-54275	

Voice #1 pulse width.
Write-only.
$D404
54276	

Voice #1 control register. Bits:

    *

      Bit #0: 0 = Voice off, Release cycle; 1 = Voice on, Attack-Decay-Sustain cycle.
    *

      Bit #1: 1 = Synchronization enabled.
    *

      Bit #2: 1 = Ring modulation enabled.
    *

      Bit #3: 1 = Disable voice, reset noise generator.
    *

      Bit #4: 1 = Triangle waveform enabled.
    *

      Bit #5: 1 = Saw waveform enabled.
    *

      Bit #6: 1 = Rectangle waveform enabled.
    *

      Bit #7: 1 = Noise enabled.

Write-only.
$D405
54277	

Voice #1 Attack and Decay length. Bits:

    *

      Bits #0-#3: Decay length. Values:
          o

            %0000, 0: 6 ms.
          o

            %0001, 1: 24 ms.
          o

            %0010, 2: 48 ms.
          o

            %0011, 3: 72 ms.
          o

            %0100, 4: 114 ms.
          o

            %0101, 5: 168 ms.
          o

            %0110, 6: 204 ms.
          o

            %0111, 7: 240 ms.
          o

            %1000, 8: 300 ms.
          o

            %1001, 9: 750 ms.
          o

            %1010, 10: 1.5 s.
          o

            %1011, 11: 2.4 s.
          o

            %1100, 12: 3 s.
          o

            %1101, 13: 9 s.
          o

            %1110, 14: 15 s.
          o

            %1111, 15: 24 s.
    *

      Bits #4-#7: Attack length. Values:
          o

            %0000, 0: 2 ms.
          o

            %0001, 1: 8 ms.
          o

            %0010, 2: 16 ms.
          o

            %0011, 3: 24 ms.
          o

            %0100, 4: 38 ms.
          o

            %0101, 5: 56 ms.
          o

            %0110, 6: 68 ms.
          o

            %0111, 7: 80 ms.
          o

            %1000, 8: 100 ms.
          o

            %1001, 9: 250 ms.
          o

            %1010, 10: 500 ms.
          o

            %1011, 11: 800 ms.
          o

            %1100, 12: 1 s.
          o

            %1101, 13: 3 s.
          o

            %1110, 14: 5 s.
          o

            %1111, 15: 8 s.

Write-only.
$D406
54278	

Voice #1 Sustain volume and Release length. Bits:

    *

      Bits #0-#3: Release length. Values:
          o

            %0000, 0: 6 ms.
          o

            %0001, 1: 24 ms.
          o

            %0010, 2: 48 ms.
          o

            %0011, 3: 72 ms.
          o

            %0100, 4: 114 ms.
          o

            %0101, 5: 168 ms.
          o

            %0110, 6: 204 ms.
          o

            %0111, 7: 240 ms.
          o

            %1000, 8: 300 ms.
          o

            %1001, 9: 750 ms.
          o

            %1010, 10: 1.5 s.
          o

            %1011, 11: 2.4 s.
          o

            %1100, 12: 3 s.
          o

            %1101, 13: 9 s.
          o

            %1110, 14: 15 s.
          o

            %1111, 15: 24 s.
    *

      Bits #4-#7: Sustain volume.

Write-only.
$D407-$D408
54279-54280	

Voice #2 frequency.
Write-only.
$D409-$D40A
54281-54282	

Voice #2 pulse width.
Write-only.
$D40B
54283	

Voice #2 control register.
Write-only.
$D40C
54284	

Voice #2 Attack and Decay length.
Write-only.
$D40D
54285	

Voice #2 Sustain volume and Release length.
Write-only.
$D40E-$D40F
54286-54287	

Voice #3 frequency.
Write-only.
$D410-$D411
54288-54289	

Voice #3 pulse width.
Write-only.
$D412
54290	

Voice #3 control register.
Write-only.
$D413
54291	

Voice #3 Attack and Decay length.
Write-only.
$D414
54292	

Voice #3 Sustain volume and Release length.
Write-only.
$D415
54293	

Filter cut off frequency (bits #0-#2).
Write-only.
$D416
54294	

Filter cut off frequency (bits #3-#10).
Write-only.
$D417
54295	

Filter control. Bits:

    *

      Bit #0: 1 = Voice #1 filtered.
    *

      Bit #1: 1 = Voice #2 filtered.
    *

      Bit #2: 1 = Voice #3 filtered.
    *

      Bit #3: 1 = External voice filtered.
    *

      Bits #4-#7: Filter resonance.

Write-only.
$D418
54296	

Volume and filter modes. Bits:

    *

      Bits #0-#3: Volume.
    *

      Bit #4: 1 = Low pass filter enabled.
    *

      Bit #5: 1 = Band pass filter enabled.
    *

      Bit #6: 1 = High pass filter enabled.
    *

      Bit #7: 1 = Voice #3 disabled.

Write-only.
$D419
54297	

X value of paddle selected at memory address $DD00. (Updates at every 512 system cycles.)
Read-only.
$D41A
54298	

Y value of paddle selected at memory address $DD00. (Updates at every 512 system cycles.)
Read-only.
$D41B
54299	

Voice #3 waveform output.
Read-only.
$D41C
54300	

Voice #3 ADSR output.
Read-only.
$D41D-$D41F
54301-54303	

Unusable (3 bytes).
$D420-$D7FF
54304-55295	

SID register images (repeated every $20, 32 bytes).
"""
