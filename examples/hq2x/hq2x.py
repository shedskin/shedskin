#hq2x filter demo program
#----------------------------------------------------------
#Copyright (C) 2003 MaxSt ( maxst@hiend3d.com )
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.
#
#You should have received a copy of the GNU Lesser General Public
#License along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


LUT16to32 = 65536*[0]
RGBtoYUV = 65536*[0]

Ymask = 0x00FF0000
Umask = 0x0000FF00
Vmask = 0x000000FF
trY   = 0x00300000
trU   = 0x00000700
trV   = 0x00000006

class PPM:
    def __init__(self, w, h, rgb=None):
        self.w, self.h = w, h
        if rgb:
            self.rgb = rgb
        else:
            self.rgb = [0 for i in range(w*h)]

    @staticmethod
    def load(filename):
        lines = [l.strip() for l in open(filename)]
        assert lines[0] == 'P3'
        w, h = list(map(int, lines[1].split()))
        assert int(lines[2]) == 255
        values = []
        for line in lines[3:]:
            values.extend(list(map(int, line.split())))
        rgb = []
        for i in range(0, len(values), 3):
            r = values[i] >> 3
            g = values[i+1] >> 2
            b = values[i+2] >> 3
            rgb.append(r << 11 | g << 5 | b)
        return PPM(w, h, rgb)

    def save(self, filename):
        f = open(filename, 'w')
        print('P3', file=f)
        print(self.w, self.h, file=f)
        print('255', file=f)
        for rgb in self.rgb:
            r = ((rgb >> 16) & 0xff)
            g = ((rgb >> 8) & 0xff)
            b = (rgb & 0xff)
            print(r, g, b, file=f)
        print(file=f)
        f.close()

def diff(w1, w2):
    YUV1 = RGBtoYUV[w1]
    YUV2 = RGBtoYUV[w2]
    return (abs((YUV1 & Ymask) - (YUV2 & Ymask)) > trY) or \
           (abs((YUV1 & Umask) - (YUV2 & Umask)) > trU) or \
           (abs((YUV1 & Vmask) - (YUV2 & Vmask)) > trV)

def Interp1(c1, c2):
    return (c1*3+c2) >> 2

def Interp2(c1, c2, c3): 
    return (c1*2+c2+c3) >> 2

def Interp6(c1, c2, c3): 
    return ((((c1 & 0x00FF00)*5 + (c2 & 0x00FF00)*2 + (c3 & 0x00FF00) ) & 0x0007F800) + \
            (((c1 & 0xFF00FF)*5 + (c2 & 0xFF00FF)*2 + (c3 & 0xFF00FF) ) & 0x07F807F8)) >> 3

def Interp7(c1, c2, c3): 
    return ((((c1 & 0x00FF00)*6 + (c2 & 0x00FF00) + (c3 & 0x00FF00) ) & 0x0007F800) + \
            (((c1 & 0xFF00FF)*6 + (c2 & 0xFF00FF) + (c3 & 0xFF00FF) ) & 0x07F807F8)) >> 3

def Interp9(c1, c2, c3): 
    return ((((c1 & 0x00FF00)*2 + ((c2 & 0x00FF00) + (c3 & 0x00FF00))*3 ) & 0x0007F800) + \
            (((c1 & 0xFF00FF)*2 + ((c2 & 0xFF00FF) + (c3 & 0xFF00FF))*3 ) & 0x07F807F8)) >> 3

def Interp10(c1, c2, c3): 
    return ((((c1 & 0x00FF00)*14 + (c2 & 0x00FF00) + (c3 & 0x00FF00) ) & 0x000FF000) +
            (((c1 & 0xFF00FF)*14 + (c2 & 0xFF00FF) + (c3 & 0xFF00FF) ) & 0x0FF00FF0)) >> 4

def PIXEL00_0(rgb_out, pOut, BpL, c): rgb_out[pOut] = c[5]
def PIXEL00_10(rgb_out, pOut, BpL, c): rgb_out[pOut] = Interp1(c[5], c[1])
def PIXEL00_11(rgb_out, pOut, BpL, c): rgb_out[pOut] = Interp1(c[5], c[4])
def PIXEL00_12(rgb_out, pOut, BpL, c): rgb_out[pOut] = Interp1(c[5], c[2])
def PIXEL00_20(rgb_out, pOut, BpL, c): rgb_out[pOut] = Interp2(c[5], c[4], c[2])
def PIXEL00_21(rgb_out, pOut, BpL, c): rgb_out[pOut] = Interp2(c[5], c[1], c[2])
def PIXEL00_22(rgb_out, pOut, BpL, c): rgb_out[pOut] = Interp2(c[5], c[1], c[4])
def PIXEL00_60(rgb_out, pOut, BpL, c): rgb_out[pOut] = Interp6(c[5], c[2], c[4])
def PIXEL00_61(rgb_out, pOut, BpL, c): rgb_out[pOut] = Interp6(c[5], c[4], c[2])
def PIXEL00_70(rgb_out, pOut, BpL, c): rgb_out[pOut] = Interp7(c[5], c[4], c[2])
def PIXEL00_90(rgb_out, pOut, BpL, c): rgb_out[pOut] = Interp9(c[5], c[4], c[2])
def PIXEL00_100(rgb_out, pOut, BpL, c): rgb_out[pOut] = Interp10(c[5], c[4], c[2])
def PIXEL01_0(rgb_out, pOut, BpL, c): rgb_out[pOut+1] = c[5]
def PIXEL01_10(rgb_out, pOut, BpL, c): rgb_out[pOut+1] = Interp1(c[5], c[3])
def PIXEL01_11(rgb_out, pOut, BpL, c): rgb_out[pOut+1] = Interp1(c[5], c[2])
def PIXEL01_12(rgb_out, pOut, BpL, c): rgb_out[pOut+1] = Interp1(c[5], c[6])
def PIXEL01_20(rgb_out, pOut, BpL, c): rgb_out[pOut+1] = Interp2(c[5], c[2], c[6])
def PIXEL01_21(rgb_out, pOut, BpL, c): rgb_out[pOut+1] = Interp2(c[5], c[3], c[6])
def PIXEL01_22(rgb_out, pOut, BpL, c): rgb_out[pOut+1] = Interp2(c[5], c[3], c[2])
def PIXEL01_60(rgb_out, pOut, BpL, c): rgb_out[pOut+1] = Interp6(c[5], c[6], c[2])
def PIXEL01_61(rgb_out, pOut, BpL, c): rgb_out[pOut+1] = Interp6(c[5], c[2], c[6])
def PIXEL01_70(rgb_out, pOut, BpL, c): rgb_out[pOut+1] = Interp7(c[5], c[2], c[6])
def PIXEL01_90(rgb_out, pOut, BpL, c): rgb_out[pOut+1] = Interp9(c[5], c[2], c[6])
def PIXEL01_100(rgb_out, pOut, BpL, c): rgb_out[pOut+1] = Interp10(c[5], c[2], c[6])
def PIXEL10_0(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL] = c[5]
def PIXEL10_10(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL] = Interp1(c[5], c[7])
def PIXEL10_11(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL] = Interp1(c[5], c[8])
def PIXEL10_12(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL] = Interp1(c[5], c[4])
def PIXEL10_20(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL] = Interp2(c[5], c[8], c[4])
def PIXEL10_21(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL] = Interp2(c[5], c[7], c[4])
def PIXEL10_22(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL] = Interp2(c[5], c[7], c[8])
def PIXEL10_60(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL] = Interp6(c[5], c[4], c[8])
def PIXEL10_61(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL] = Interp6(c[5], c[8], c[4])
def PIXEL10_70(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL] = Interp7(c[5], c[8], c[4])
def PIXEL10_90(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL] = Interp9(c[5], c[8], c[4])
def PIXEL10_100(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL] = Interp10(c[5], c[8], c[4])
def PIXEL11_0(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL+1] = c[5]
def PIXEL11_10(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL+1] = Interp1(c[5], c[9])
def PIXEL11_11(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL+1] = Interp1(c[5], c[6])
def PIXEL11_12(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL+1] = Interp1(c[5], c[8])
def PIXEL11_20(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL+1] = Interp2(c[5], c[6], c[8])
def PIXEL11_21(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL+1] = Interp2(c[5], c[9], c[8])
def PIXEL11_22(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL+1] = Interp2(c[5], c[9], c[6])
def PIXEL11_60(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL+1] = Interp6(c[5], c[8], c[6])
def PIXEL11_61(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL+1] = Interp6(c[5], c[6], c[8])
def PIXEL11_70(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL+1] = Interp7(c[5], c[6], c[8])
def PIXEL11_90(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL+1] = Interp9(c[5], c[6], c[8])
def PIXEL11_100(rgb_out, pOut, BpL, c): rgb_out[pOut+BpL+1] = Interp10(c[5], c[6], c[8])

def hq2x(xres, yres, rgb):
    '''
    +--+--+--+
    |w1|w2|w3|
    +--+--+--+
    |w4|w5|w6|
    +--+--+--+
    |w7|w8|w9|
    +--+--+--+
    '''
    c = 10*[0]
    w = 10*[0]
    rgb_out = 4*len(rgb)*[0]
    BpL = 2*xres

    for j in range(yres):
        prevline = -xres if j>0 else 0
        nextline = xres if j<yres-1 else 0

        for i in range(xres):
            pos = j*xres+i
            pOut = j*xres*4+2*i

            w[1] = w[2] = w[3] = rgb[pos+prevline]
            w[4] = w[5] = w[6] = rgb[pos]
            w[7] = w[8] = w[9] = rgb[pos+nextline]

            if i>0:
                w[1] = rgb[pos+prevline-1]
                w[4] = rgb[pos-1]
                w[7] = rgb[pos+nextline-1]

            if i<xres-1:
                w[3] = rgb[pos+prevline+1]
                w[6] = rgb[pos+1]
                w[9] = rgb[pos+nextline+1]
          
            pattern = 0
            flag = 1
            YUV1 = RGBtoYUV[w[5]]
            for k in range(1,10):
                if k == 5: 
                    continue
                if w[k] != w[5]:
                    YUV2 = RGBtoYUV[w[k]]
                    if (abs((YUV1 & Ymask) - (YUV2 & Ymask)) > trY ) or \
                       (abs((YUV1 & Umask) - (YUV2 & Umask)) > trU ) or \
                       (abs((YUV1 & Vmask) - (YUV2 & Vmask)) > trV ):
                        pattern |= flag
                flag <<= 1

            for k in range(1,10):
                c[k] = LUT16to32[w[k]]

            if pattern == 0 or pattern == 1 or pattern == 4 or pattern == 32 or pattern == 128 or pattern == 5 or pattern == 132 or pattern == 160 or pattern == 33 or pattern == 129 or pattern == 36 or pattern == 133 or pattern == 164 or pattern == 161 or pattern == 37 or pattern == 165:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 2 or pattern == 34 or pattern == 130 or pattern == 162:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 16 or pattern == 17 or pattern == 48 or pattern == 49:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 64 or pattern == 65 or pattern == 68 or pattern == 69:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 8 or pattern == 12 or pattern == 136 or pattern == 140:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 3 or pattern == 35 or pattern == 131 or pattern == 163:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 6 or pattern == 38 or pattern == 134 or pattern == 166:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 20 or pattern == 21 or pattern == 52 or pattern == 53:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 144 or pattern == 145 or pattern == 176 or pattern == 177:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 192 or pattern == 193 or pattern == 196 or pattern == 197:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 96 or pattern == 97 or pattern == 100 or pattern == 101:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 40 or pattern == 44 or pattern == 168 or pattern == 172:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 9 or pattern == 13 or pattern == 137 or pattern == 141:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 18 or pattern == 50:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 80 or pattern == 81:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 72 or pattern == 76:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 10 or pattern == 138:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 66:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 24:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 7 or pattern == 39 or pattern == 135:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 148 or pattern == 149 or pattern == 180:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 224 or pattern == 228 or pattern == 225:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 41 or pattern == 169 or pattern == 45:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 22 or pattern == 54:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 208 or pattern == 209:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 104 or pattern == 108:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 11 or pattern == 139:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 19 or pattern == 51:
                if (diff(w[2], w[6])):
                    PIXEL00_11(rgb_out, pOut, BpL, c)
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_60(rgb_out, pOut, BpL, c)
                    PIXEL01_90(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 146 or pattern == 178:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                    PIXEL11_12(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_90(rgb_out, pOut, BpL, c)
                    PIXEL11_61(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
            elif pattern == 84 or pattern == 85:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL01_11(rgb_out, pOut, BpL, c)
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_60(rgb_out, pOut, BpL, c)
                    PIXEL11_90(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
            elif pattern == 112 or pattern == 113:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL10_12(rgb_out, pOut, BpL, c)
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_61(rgb_out, pOut, BpL, c)
                    PIXEL11_90(rgb_out, pOut, BpL, c)
            elif pattern == 200 or pattern == 204:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                    PIXEL11_11(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_90(rgb_out, pOut, BpL, c)
                    PIXEL11_60(rgb_out, pOut, BpL, c)
            elif pattern == 73 or pattern == 77:
                if (diff(w[8], w[4])):
                    PIXEL00_12(rgb_out, pOut, BpL, c)
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_61(rgb_out, pOut, BpL, c)
                    PIXEL10_90(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 42 or pattern == 170:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                    PIXEL10_11(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_90(rgb_out, pOut, BpL, c)
                    PIXEL10_60(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 14 or pattern == 142:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                    PIXEL01_12(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_90(rgb_out, pOut, BpL, c)
                    PIXEL01_61(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 67:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 70:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 28:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 152:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 194:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 98:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 56:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 25:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 26 or pattern == 31:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 82 or pattern == 214:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 88 or pattern == 248:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 74 or pattern == 107:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 27:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_10(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 86:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                PIXEL11_10(rgb_out, pOut, BpL, c)
            elif pattern == 216:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_10(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 106:
                PIXEL00_10(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 30:
                PIXEL00_10(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 210:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                PIXEL01_10(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 120:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_10(rgb_out, pOut, BpL, c)
            elif pattern == 75:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_10(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 29:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 198:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 184:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 99:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 57:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 71:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 156:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 226:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 60:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 195:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 102:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 153:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 58:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_70(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_70(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 83:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_70(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_70(rgb_out, pOut, BpL, c)
            elif pattern == 92:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_70(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_70(rgb_out, pOut, BpL, c)
            elif pattern == 202:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_70(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_70(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 78:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_70(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_70(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 154:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_70(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_70(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 114:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_70(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_70(rgb_out, pOut, BpL, c)
            elif pattern == 89:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_70(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_70(rgb_out, pOut, BpL, c)
            elif pattern == 90:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_70(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_70(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_70(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_70(rgb_out, pOut, BpL, c)
            elif pattern == 55 or pattern == 23:
                if (diff(w[2], w[6])):
                    PIXEL00_11(rgb_out, pOut, BpL, c)
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_60(rgb_out, pOut, BpL, c)
                    PIXEL01_90(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 182 or pattern == 150:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                    PIXEL11_12(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_90(rgb_out, pOut, BpL, c)
                    PIXEL11_61(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
            elif pattern == 213 or pattern == 212:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL01_11(rgb_out, pOut, BpL, c)
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_60(rgb_out, pOut, BpL, c)
                    PIXEL11_90(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
            elif pattern == 241 or pattern == 240:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL10_12(rgb_out, pOut, BpL, c)
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_61(rgb_out, pOut, BpL, c)
                    PIXEL11_90(rgb_out, pOut, BpL, c)
            elif pattern == 236 or pattern == 232:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                    PIXEL11_11(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_90(rgb_out, pOut, BpL, c)
                    PIXEL11_60(rgb_out, pOut, BpL, c)
            elif pattern == 109 or pattern == 105:
                if (diff(w[8], w[4])):
                    PIXEL00_12(rgb_out, pOut, BpL, c)
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_61(rgb_out, pOut, BpL, c)
                    PIXEL10_90(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 171 or pattern == 43:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                    PIXEL10_11(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_90(rgb_out, pOut, BpL, c)
                    PIXEL10_60(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 143 or pattern == 15:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                    PIXEL01_12(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_90(rgb_out, pOut, BpL, c)
                    PIXEL01_61(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 124:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_10(rgb_out, pOut, BpL, c)
            elif pattern == 203:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_10(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 62:
                PIXEL00_10(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 211:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                PIXEL01_10(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 118:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                PIXEL11_10(rgb_out, pOut, BpL, c)
            elif pattern == 217:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_10(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 110:
                PIXEL00_10(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 155:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_10(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 188:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 185:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 61:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 157:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 103:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 227:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 230:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 199:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 220:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_70(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 158:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_70(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 234:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_70(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 242:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_70(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 59:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_70(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 121:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_70(rgb_out, pOut, BpL, c)
            elif pattern == 87:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_70(rgb_out, pOut, BpL, c)
            elif pattern == 79:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_70(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 122:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_70(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_70(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_70(rgb_out, pOut, BpL, c)
            elif pattern == 94:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_70(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_70(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_70(rgb_out, pOut, BpL, c)
            elif pattern == 218:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_70(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_70(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_70(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 91:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_70(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_70(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_70(rgb_out, pOut, BpL, c)
            elif pattern == 229:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 167:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 173:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 181:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 186:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_70(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_70(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 115:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_70(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_70(rgb_out, pOut, BpL, c)
            elif pattern == 93:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_70(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_70(rgb_out, pOut, BpL, c)
            elif pattern == 206:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_70(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_70(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 205 or pattern == 201:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_70(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 174 or pattern == 46:
                if (diff(w[4], w[2])):
                    PIXEL00_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_70(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 179 or pattern == 147:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_70(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 117 or pattern == 116:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_10(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_70(rgb_out, pOut, BpL, c)
            elif pattern == 189:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 231:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 126:
                PIXEL00_10(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_10(rgb_out, pOut, BpL, c)
            elif pattern == 219:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_10(rgb_out, pOut, BpL, c)
                PIXEL10_10(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 125:
                if (diff(w[8], w[4])):
                    PIXEL00_12(rgb_out, pOut, BpL, c)
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_61(rgb_out, pOut, BpL, c)
                    PIXEL10_90(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL11_10(rgb_out, pOut, BpL, c)
            elif pattern == 221:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL01_11(rgb_out, pOut, BpL, c)
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_60(rgb_out, pOut, BpL, c)
                    PIXEL11_90(rgb_out, pOut, BpL, c)
                PIXEL10_10(rgb_out, pOut, BpL, c)
            elif pattern == 207:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                    PIXEL01_12(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_90(rgb_out, pOut, BpL, c)
                    PIXEL01_61(rgb_out, pOut, BpL, c)
                PIXEL10_10(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 238:
                PIXEL00_10(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                    PIXEL11_11(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_90(rgb_out, pOut, BpL, c)
                    PIXEL11_60(rgb_out, pOut, BpL, c)
            elif pattern == 190:
                PIXEL00_10(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                    PIXEL11_12(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_90(rgb_out, pOut, BpL, c)
                    PIXEL11_61(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
            elif pattern == 187:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                    PIXEL10_11(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_90(rgb_out, pOut, BpL, c)
                    PIXEL10_60(rgb_out, pOut, BpL, c)
                PIXEL01_10(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 243:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                PIXEL01_10(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL10_12(rgb_out, pOut, BpL, c)
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_61(rgb_out, pOut, BpL, c)
                    PIXEL11_90(rgb_out, pOut, BpL, c)
            elif pattern == 119:
                if (diff(w[2], w[6])):
                    PIXEL00_11(rgb_out, pOut, BpL, c)
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_60(rgb_out, pOut, BpL, c)
                    PIXEL01_90(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                PIXEL11_10(rgb_out, pOut, BpL, c)
            elif pattern == 237 or pattern == 233:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_20(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_100(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 175 or pattern == 47:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_100(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 183 or pattern == 151:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_100(rgb_out, pOut, BpL, c)
                PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 245 or pattern == 244:
                PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_100(rgb_out, pOut, BpL, c)
            elif pattern == 250:
                PIXEL00_10(rgb_out, pOut, BpL, c)
                PIXEL01_10(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 123:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_10(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_10(rgb_out, pOut, BpL, c)
            elif pattern == 95:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_10(rgb_out, pOut, BpL, c)
                PIXEL11_10(rgb_out, pOut, BpL, c)
            elif pattern == 222:
                PIXEL00_10(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_10(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 252:
                PIXEL00_21(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_100(rgb_out, pOut, BpL, c)
            elif pattern == 249:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_22(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_100(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 235:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_21(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_100(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 111:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_100(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_22(rgb_out, pOut, BpL, c)
            elif pattern == 63:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_100(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_21(rgb_out, pOut, BpL, c)
            elif pattern == 159:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_100(rgb_out, pOut, BpL, c)
                PIXEL10_22(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 215:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_100(rgb_out, pOut, BpL, c)
                PIXEL10_21(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 246:
                PIXEL00_22(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_100(rgb_out, pOut, BpL, c)
            elif pattern == 254:
                PIXEL00_10(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_100(rgb_out, pOut, BpL, c)
            elif pattern == 253:
                PIXEL00_12(rgb_out, pOut, BpL, c)
                PIXEL01_11(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_100(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_100(rgb_out, pOut, BpL, c)
            elif pattern == 251:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                PIXEL01_10(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_100(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 239:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_100(rgb_out, pOut, BpL, c)
                PIXEL01_12(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_100(rgb_out, pOut, BpL, c)
                PIXEL11_11(rgb_out, pOut, BpL, c)
            elif pattern == 127:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_100(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_20(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_20(rgb_out, pOut, BpL, c)
                PIXEL11_10(rgb_out, pOut, BpL, c)
            elif pattern == 191:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_100(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_100(rgb_out, pOut, BpL, c)
                PIXEL10_11(rgb_out, pOut, BpL, c)
                PIXEL11_12(rgb_out, pOut, BpL, c)
            elif pattern == 223:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_20(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_100(rgb_out, pOut, BpL, c)
                PIXEL10_10(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_20(rgb_out, pOut, BpL, c)
            elif pattern == 247:
                PIXEL00_11(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_100(rgb_out, pOut, BpL, c)
                PIXEL10_12(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_100(rgb_out, pOut, BpL, c)
            elif pattern == 255:
                if (diff(w[4], w[2])):
                    PIXEL00_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL00_100(rgb_out, pOut, BpL, c)
                if (diff(w[2], w[6])):
                    PIXEL01_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL01_100(rgb_out, pOut, BpL, c)
                if (diff(w[8], w[4])):
                    PIXEL10_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL10_100(rgb_out, pOut, BpL, c)
                if (diff(w[6], w[8])):
                    PIXEL11_0(rgb_out, pOut, BpL, c)
                else:
                    PIXEL11_100(rgb_out, pOut, BpL, c)
    return rgb_out

def init_LUTs():
    global LUT16to32, RGBtoYUV

    for i in range(65536):
        LUT16to32[i] = ((i & 0xF800) << 8) | ((i & 0x07E0) << 5) | ((i & 0x001F) << 3)

    for i in range(32):
        for j in range(64):
            for k in range(32):
                r = i << 3
                g = j << 2
                b = k << 3
                Y = (r + g + b) >> 2
                u = 128 + ((r - b) >> 2)
                v = 128 + ((-r + 2*g -b)>>3)
                RGBtoYUV[ (i << 11) | (j << 5) | k ] = (Y<<16) | (u<<8) | v

def main():
    init_LUTs()
    print('scaling randam.ppm to randam2.ppm (100 times)..')
    ppm = PPM.load('randam.ppm')
    for i in range(100):
        rgb = hq2x(ppm.w, ppm.h, ppm.rgb)
    PPM(2*ppm.w, 2*ppm.h, rgb).save('randam2.ppm')

if __name__ == '__main__':
    main()
