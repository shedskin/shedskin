#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

sector_size = 256
# 35 tracks, 683 sectors total.
# possible: up to 42 tracks.

# tracks 1..17: 21 sectors
# tracks 18..24: 19 sectors
# tracks 25..30: 18 sectors
# tracks 31..35: 17 sectors
# tracks 36..42: 17 sectors (non standard)

# block allocation map: track 18, sector 0.
# directory: track 18, sector 1 ff.
# first track is track 1.
# first sector is sector 0.
# sectors are in a track.

# D64 file: disk image [sektorcnt][256], then error_info[sektorcnt] (optional; default to 0=ok)

# A0 padding?

# size should be 174848

"""
directory (btes)
    next directory SECTOR track,sector or 0,0 (usually)
    file type and flags
    content track,sector
    16 char petascii, Padded with $A0
    REL_side-sector block track,sector
    REL file record length (max. 254)
    6 bytes unused (except GEOS)
    file_size_sectorsLO,HI
"""

"""
BAM
Sector (18,0).
first directory track,sector (UNTRUSTED)
DOS VERSION $41="A"
UNUSED
$8C bytes of BAM entries for each track, four bytes per track.
$10 Disk Name
2 junk ($A0)
2 Disk ID
$A0
DOS type1,2 "2A"
4 $A0
rest 0 except for extended formats:
DOLPHIN DOS / SPEED DOS BAM.

BAM entry =
    free_sector_count
    3 bitmap: lowest sector first. bit 0=sector 0, bit 7=sector 7. Next byte again bit 0=sector 8 etc.
    if bit=1: free.
    Defaults to allocated for not-existing bits.
"""
