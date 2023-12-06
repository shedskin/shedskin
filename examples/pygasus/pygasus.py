# -*- coding: utf-8 -*-
'''
NES emulator by Maciek "Mistrall" Żuk

modified by mark.dufour@gmail.com to work with shedskin
'''



import array

pallete=[[0x52,0x52,0x52],[0x00,0x00,0x80],[0x08,0x00,0x8A],[0x2C,0x00,0x7E],[0x4A,0x00,0x4E],[0x50,0x00,0x06],[0x44,0x00,0x00],[0x26,0x080,0x0],[0x0A,0x20,0x00],[0x00,0x2E,0x00],[0x00,0x32,0x00],[0x00,0x26,0x0A],[0x00,0x1C,0x48],[0x00,0x00,0x00],[0x00,0x00,0x00],[0x00,0x00,0x00],[0xA4,0xA4,0xA4],[0x00,0x38,0xCE],[0x34,0x16,0xEC],[0x5E,0x04,0xDC],[0x8C,0x00,0xB0],[0x9A,0x00,0x4C],[0x90,0x18,0x00],[0x70,0x36,0x00],[0x4C,0x54,0x00],[0x0E,0x6C,0x00],[0x00,0x74,0x00],[0x00,0x6C,0x2C],[0x00,0x5E,0x84],[0x00,0x00,0x00],[0x00,0x00,0x00],[0x00,0x00,0x00],[0xFF,0xFF,0xFF],[0x4C,0x9C,0xFF],[0x7C,0x78,0xFF],[0xA6,0x64,0xFF],[0xDA,0x5A,0xFF],[0xF0,0x54,0xC0],[0xF0,0x6A,0x56],[0xD6,0x86,0x10],[0xBA,0xA4,0x00],[0x76,0xC0,0x00],[0x46,0xCC,0x1A],[0x2E,0xC8,0x66],[0x34,0xC2,0xBE],[0x3A,0x3A,0x3A],[0x00,0x00,0x00],[0x00,0x00,0x00],[0xFF,0xFF,0xFF],[0xB6,0xDA,0xFF],[0xC8,0xCA,0xFF],[0xDA,0xC2,0xFF],[0xF0,0xBE,0xFF],[0xFC,0xBC,0xEE],[0xFA,0xC2,0xC0],[0xF2,0xCC,0xA2],[0xE6,0xDA,0x92],[0xCC,0xE6,0x8E],[0xB8,0xEE,0xA2],[0xAE,0xEA,0xBE],[0xAE,0xE8,0xE2],[0xB0,0xB0,0xB0],[0x00,0x00,0x00],[0x00,0x00,0x00]]

PRGbks=[]
CHRbks=[]
#PRGupper=0
#PRGlower=0
RAMbks=[]
A=0
X=0
Y=0
PC=0
P=0
S=0
adrmask=0xffff
ticks=0
savepc=0
value=0
sum=0
saveflags=0
opcode=0
nticks=[0]*256
adrmode=[None]*256
instruction=[None]*256

nesRAM=[0]*0x800
ioMEM=[0]*0x8
io2MEM=[0xff]*0x20
wRAM=[0]*0x2000
ppuRAM=[0]*0x4000
SPRRAM=[0]*0x100

mMapper=0
ppuNameTableAdr=0
ppuAdrIncrement=1
ppuSprPatTabAdr=0
ppuBgrPatTabAdr=0
ppuSprSizeValue=0
ppuNMIAfterVBlk=0
ppuColorModeSel=0
ppuClipBackgrnd=0
ppuClipSprites_=0
ppuShowBackgrnd=0
ppuShowSprites_=0
ppuColorIntnsty=0
ppuSPRRAMaddres=0
ppuHoristScroll=0
ppuVerticScroll=0
ppuVertOrHorVal=0
ppuAdr2006Ofset=0
ppuVRAMAdrValue=0
ppuStatusRegstr=0
ppuVRAMBuffer__=0
ppuVerticalMirr=0
ppu4ScreensMode=0
ppuSingleScreen=0
jpdKeysBuffer__=0
jpdReadNumber__=0
jpdLastWrote___=0
keys=(0,)*255
mmcLoad=[None]*256
mmcWrite=[None]*256
mmcRead=[None]*256
mmcRegs=[0]*256
mmcBitp=0
mmcLast=0

screen = [[[0,0,0] for y in range(240)] for x in range(256)]
def getscreen():
    l = []
    for y in range(240):
        for x in range(256):
            r,g,b = screen[x][y]
            l.append(r)
            l.append(g)
            l.append(b)
    return array.array('B', l).tobytes()

class MMCload:
    pass
class MMCread:
    pass
class MMCwrite:
    pass

class mmc0Load(MMCload):
  def _exec(self):
    global PRGupper, PRGlower    
    if len(PRGbks)==1:
        PRGupper=PRGbks[0][:]
        PRGlower=PRGbks[0][:]
    elif len(PRGbks)==2:
        PRGlower=PRGbks[0][:]
        PRGupper=PRGbks[1][:]
    if len(CHRbks)>0:
        for i in range(0x2000):
            ppuRAM[i]=CHRbks[0][i]

class mmc0Write(MMCwrite):
  def _exec(self, adr, byte):
    print("wtf? writing to rom?")
    pass

class mmc0Read(MMCread):
  def _exec(self, adr):
    if adr>=0x4000:
        return PRGupper[adr-0x4000]
    return PRGlower[adr]

class mmc1Load(MMCload):
  def _exec(self):
        global PRGupper, PRGlower
        PRGlower=PRGbks[0][:]
        PRGupper=PRGbks[-1][:]

class mmc1Read(MMCread):
  def _exec(self, adr):
   if adr>=0x4000:
        return PRGupper[adr-0x4000]
   return PRGlower[adr]  

class mmc1Write(MMCwrite):
  def _exec(self, adr, byte):
    global mmcLast, mmcBitp, PRGlower, PRGupper
    regnum=(adr>>13)&0x3
    mmcLast=regnum
#    print "write to reg",regnum, bin(byte)
    if byte & 0x80:
        mmcBitp=0
        if regnum==0:
            save4=mmcRegs[0]&0xf
            mmcRegs[0]=0x1f
            if save4: mmcRegs[0]^=0xf
        else:
            mmcRegs[regnum]=0
        return
    byte&=1
    if mmcBitp==5:
        mmcBitp=0
    if mmcLast!=regnum:
        mmcBitp=0
    if byte!=0:
        mmcRegs[regnum]|=(1<<mmcBitp)
    else:
        if mmcRegs[regnum]&(1<<mmcBitp): mmcRegs[regnum]^=(1<<mmcBitp)
    mmcBitp+=1
    if regnum==0:
        if mmcBitp==0:
            if byte!=0: ppuVerticalMirr=1
            else: ppuVerticalMirr=0
        elif mmcBitp==1:
            if byte!=0: ppuSingleScreen=0
            else:  ppuSingleScreen=1
        elif mmcBitp==5 and len(CHRbks)>0:
            print("bllaat")
            if mmcRegs[0]&0x10==0:
                num1=mmcRegs[1]&0xf
                if num1&1: part1=0x0
                else: part1=0x1000
#                num1>>=1
                num2=mmcRegs[2]&0xf
                if num2&1: part2=0x0
                else: part2=0x1000
#                num2>>=1
                ppuAdr=0
                for i in range(0x1000):
                    ppuRAM[ppuAdr]=CHRbks[num1][part1]
                    part1+=1
                    ppuAdr+=1
                for i in range(0x1000):
                    ppuRAM[ppuAdr]=CHRbks[num2][part2]
                    part2+=1
                    ppuAdr+=1
            else:
                num=mmcRegs[1]&0xf
                for i in range(0x2000):
                    ppuRAM[i]=CHRbks[num][i]
    elif regnum==1:
        if mmcBitp==5:
            num=mmcRegs[1]&0xf

    elif regnum==3:
        if mmcBitp==5:
            num=mmcRegs[3]&0xf
            if mmcRegs[0]&8:
                if mmcRegs[0]&4:
                    PRGlower=PRGbks[num][:]
                else:
                    PRGupper=PRGbks[num][:]

            else:
                num>>=1
                PRGlower=PRGbks[num][:]
                PRGupper=PRGbks[num+1][:]

class mmc2Write(MMCwrite):
  def _exec(self, adr, byte):
    global PRGlower
    PRGlower=PRGbks[byte][:]

mmcLoad[0]=mmc0Load()
mmcRead[0]=mmc0Read()
mmcWrite[0]=mmc0Write()
mmcLoad[1]=mmc1Load()
mmcRead[1]=mmc1Read()
mmcWrite[1]=mmc1Write()
mmcLoad[2]=mmc1Load()
mmcRead[2]=mmc1Read()
mmcWrite[2]=mmc2Write()

tilesModified=1
tilePrefetch=[] #[None]*30*2
for i in range(30*2):
        tilePrefetch.append([])
#        tilePrefetch[i]=[None]*32*2
        for j in range(32*2):
                tilePrefetch[-1].append([[[0,0,0] for y in range(8)] for x in range(8)])
#                tilePrefetch[i][j]=[[0 for y in range(8)] for x in range(8)]
PS=0xff

def tpFone2(x,y):
    global tilePrefetch
    if ppuNameTableAdr==0x2000:
        nta=0x2000
        nta2=0x2400
    else:
        nta=0x2400
        nta2=0x2000
    addr0=nta2+((y)<<5)+x
    addr1=nta2+0x3c0+((y>>2)<<3)+(x>>2)
    y0=(((y>>1)&0x1)<<2)
    x0=(((x>>1)&0x1)<<1)
    sqcolor=ppuRAM[addr1]
    colUpper=((((sqcolor>>(y0+x0)))&0x3)<<2)
    patadr=(ppuRAM[addr0]<<4)
    for yo in range(8):
        b1=ppuRAM[ppuBgrPatTabAdr+patadr+yo]
        b2=ppuRAM[ppuBgrPatTabAdr+patadr+yo+8]
        for xo in range(8):
            colLower=(b1>>(7-xo))&0x1
            colLower|=((b2>>(7-xo))&0x1)<<1
            cpos=0x3f00+(colUpper+colLower)
            if cpos%4==0: cpos=0x3f00
            color=ppuRAM[cpos]&0x3f
            finalColor=pallete[color]
            tilePrefetch[y][x][xo][yo] = finalColor
def tpFone(x,y):
    global tilePrefetch
    if ppuNameTableAdr==0x2000:
        nta=0x2000
        nta2=0x2400
    else:
        nta=0x2400
        nta2=0x2000
#    x=(x+31)%32
    addr0=nta+((y)<<5)+x
    addr1=nta+0x3c0+((y>>2)<<3)+(x>>2)
    y0=(((y>>1)&0x1)<<2)
    x0=(((x>>1)&0x1)<<1)
    sqcolor=ppuRAM[addr1]
    colUpper=((((sqcolor>>(y0+x0)))&0x3)<<2)
    patadr=(ppuRAM[addr0]<<4)
    for yo in range(8):
        b1=ppuRAM[ppuBgrPatTabAdr+patadr+yo]
        b2=ppuRAM[ppuBgrPatTabAdr+patadr+yo+8]
        for xo in range(8):
            colLower=(b1>>(7-xo))&0x1
            colLower|=((b2>>(7-xo))&0x1)<<1
            cpos=0x3f00+(colUpper+colLower)
            if cpos%4==0: cpos=0x3f00
            color=ppuRAM[cpos]&0x3f
            finalColor=pallete[color]
            tilePrefetch[y][x][xo][yo] = finalColor

def tpF():
        global tilePrefetch
        if ppuNameTableAdr==0x2000:
            nta=0x2000
            nta2=0x2400
        else:
            nta=0x2400
            nta2=0x2000
        for y in range(240):
                addr0=nta+((y>>3)<<5)
                addr1=nta+0x3c0+((y>>5)<<3)
                y0=(((y>>4)&0x1)<<2)
                x0=0
                ydiv=y>>3
                y7=y&7
                for x in range(64):
                        sqcolor=ppuRAM[addr1]
                        colUpper=((((sqcolor>>(y0+x0)))&0x3)<<2)
                        if x%4==3: addr1+=1
                        if x%2==1: x0^=2
                        patadr=(ppuRAM[addr0+x]<<4)+y7
                        b1=ppuRAM[ppuBgrPatTabAdr+patadr]
                        b2=ppuRAM[ppuBgrPatTabAdr+patadr+8]
                        for x2 in range(8):
                                colLower=(b1>>(7-x2))&0x1
                                colLower|=((b2>>(7-x2))&0x1)<<1
                                cpos=0x3f00+(colUpper+colLower)
                                if cpos%4==0: cpos=0x3f00
                                color=ppuRAM[cpos]&0x3f
                                finalColor=pallete[color]
                                tilePrefetch[ydiv][x][x2][y7] = finalColor
        for y in range(240):
                addr0=nta2+((y>>3)<<5)
                addr1=nta2+0x3c0+((y>>5)<<3)
                y0=(((y>>4)&0x1)<<2)
                x0=0
                ydiv=y>>3
                y7=y&7
                for x in range(32):
                        sqcolor=ppuRAM[addr1]
                        colUpper=((((sqcolor>>(y0+x0)))&0x3)<<2)
                        if x%4==3: addr1+=1
                        if x%2==1: x0^=2
                        patadr=(ppuRAM[addr0+x]<<4)+y7
                        b1=ppuRAM[ppuBgrPatTabAdr+patadr]
                        b2=ppuRAM[ppuBgrPatTabAdr+patadr+8]
                        for x2 in range(8):
                                colLower=(b1>>(7-x2))&0x1
                                colLower|=((b2>>(7-x2))&0x1)<<1
                                cpos=0x3f00+(colUpper+colLower)
                                if cpos%4==0: cpos=0x3f00
                                color=ppuRAM[cpos]&0x3f
                                finalColor=pallete[color]
                                tilePrefetch[ydiv][x+32][x2][y7] = finalColor

def ppuDoScanline(n):
        global ppuStatusRegstr,ppuVRAMAdrValue,addr0
        bgcolor=pallete[ppuRAM[0x3f00]&0x3f]
        if ppuShowBackgrnd:
                hor0=ppuHoristScroll&7
                ver0=ppuVerticScroll&7
                sx=(ppuHoristScroll>>3)%64
                sy=((n+ppuVerticScroll)>>3)%30
                if n%8==0:
                        for x in range(32):
                            for wa in range(8):
                                for ha in range(8):
                                    screen[(x<<3)-hor0+wa][n-ver0+ha] = tilePrefetch[sy][sx][wa][ha]
                            sx=(sx+1)%64
        if ppuShowSprites_:
                sprPerScln=0
                ppuStatusRegstr^=ppuStatusRegstr&0x20
                for j in range(64):
                        i=63-j
                        i2=i<<2
                        if ppuSprSizeValue:
                                ypos=SPRRAM[(i2)]
                                if ypos>(n-1) or ypos<(n-14): 
                                        ppuStatusRegstr|=0x20
                                        continue
                                sprPerScln+=1
                                if sprPerScln>8: break
                                atrb=SPRRAM[(i2)+2]
                                if atrb&0x80:
                                        ypos=(-n+ypos)
                                else:
                                        ypos=(n-ypos)
                                indx=SPRRAM[(i2)+1]
                                xpos=SPRRAM[(i2)+3]
                                colUpper=(atrb&0x3)<<2
                                if indx&1: spt=0x1000
                                else : spt=0x0
                                indx<<=4
                                b1=ppuRAM[spt+indx+(ypos)]
                                b2=ppuRAM[spt+indx+(ypos)+8]
                                for x in range(8):
                                        if atrb&0x40:
                                                col=(b1>>(x))&0x1
                                                col|=((b2>>(x))&0x1)<<1
                                        else:
                                                col=(b1>>(7-x))&0x1
                                                col|=((b2>>(7-x))&0x1)<<1
                                        col+=colUpper+0x3f10
                                        if col%4==0: col=0x3f00
                                        color=ppuRAM[col]&0x3f
                                        finalColor=pallete[color]
                                        if indx==0 and screen[xpos+x][n]==bgcolor:
                                                ppuStatusRegstr|=0x40
                                        if finalColor!=bgcolor:
                                                if (xpos+x) < 255 and n < 240:
                                                        screen[xpos+x][n] = finalColor
                        else:
                                ypos=SPRRAM[(i2)]
                                if ypos>n or ypos<=(n-8): 
                                        ppuStatusRegstr|=0x20
                                        continue
                                sprPerScln+=1
                                if sprPerScln>8: break
                                atrb=SPRRAM[(i2)+2]
                                if atrb&0x80:
                                        ypos=(-n+ypos)&0xf
                                else:
                                        ypos=((n-ypos))&0xf
                                indx=SPRRAM[(i2)+1]<<4
                                xpos=SPRRAM[(i2)+3]
                                colUpper=(atrb&0x3)<<2
                                b1=ppuRAM[ppuSprPatTabAdr+(indx)+(ypos)]
                                b2=ppuRAM[ppuSprPatTabAdr+(indx)+(ypos)+8]
                                for x in range(8):
                                        if atrb&0x40:
                                                col=(b1>>(x))&0x1
                                                col|=((b2>>(x))&0x1)<<1
                                        else:
                                                col=(b1>>(7-x))&0x1
                                                col|=((b2>>(7-x))&0x1)<<1
                                        col+=colUpper+0x3f00
                                        if col%4==0: col=0x3f00
                                        color=ppuRAM[col]&0x3f
                                        finalColor=pallete[color]
                                        if (xpos+x) < 256 and n < 240:
                                                if indx==0 and screen[xpos+x][n]==bgcolor:
                                                        ppuStatusRegstr|=0x40
                                                if finalColor!=bgcolor:
                                                        screen[xpos+x][n] = finalColor

def setkeys(keys):
    global pygamekeys
    pygamekeys = keys
def setkeys2(keys2):
    global keys
    keys = keys2

def joyStrobe():
        global jpdKeysBuffer__, jpdReadNumber__, jpdLastWrote___
        jpdKeysBuffer__=0
        if jpdReadNumber__==0:
                if keys[pygamekeys['q']]:
                        jpdKeysBuffer__=1
        elif jpdReadNumber__==1:
                if keys[pygamekeys['w']]:
                        jpdKeysBuffer__=1
        elif jpdReadNumber__==2:
                if keys[pygamekeys['a']]:
                        jpdKeysBuffer__=1
        elif jpdReadNumber__==3:
                if keys[pygamekeys['s']]:
                        jpdKeysBuffer__=1
#        elif jpdReadNumber__==4:
#                if keys[pygamekeys['UP']]:
#                        jpdKeysBuffer__=1
#        elif jpdReadNumber__==5:
#                if keys[pygamekeys['DOWN']]:
#                        jpdKeysBuffer__=1
#        elif jpdReadNumber__==6:
#                if keys[pygamekeys['LEFT']]:
#                        jpdKeysBuffer__=1
##        elif jpdReadNumber__==7:
#                if keys[pygamekeys['RIGHT']]:
#                        jpdKeysBuffer__=1
        elif jpdReadNumber__==16:
                jpdKeysBuffer__=1
        jpdReadNumber__+=1
        if jpdReadNumber__>23: jpdReadNumber__=0


def ppuProcessRegs2(adr, val):
        global jpdKeysBuffer__, jpdReadNumber__, jpdLastWrote___
        if adr==0x4016:
                if jpdLastWrote___==1 and val==0:
                        jpdReadNumber__=0
                jpdLastWrote___=val
        if adr==0x4014:
                i=0x100*(val&0xff)
                j=0
                while j<256:
                        SPRRAM[j]=pGetMem(i)
                        i+=1
                        j+=1


def ppuProcessRegs(adr, val):
        global ppuNameTableAdr, ppuAdrIncrement, ppuSprPatTabAdr, ppuBgrPatTabAdr, ppuSprSizeValue, ppuNMIAfterVBlk, ppuColorModeSel, ppuClipBackgrnd, ppuClipSprites_, ppuShowBackgrnd, ppuShowSprites_, ppuColorIntnsty, ppuSPRRAMaddres, ppuHorVerOffReg, ppuAdr2006Ofset, ppuVRAMAdrValue, ppuStatusRegstr,ppuVRAMBuffer__,        tilesModified,ppuVertOrHorVal, ppuHoristScroll, ppuVerticScroll
        if adr==0x2000:
                ppuCReg1=val
                ppuNameTableAdr=0x2000
                if ppuCReg1&0x1: ppuNameTableAdr+=0x400
                if ppuCReg1&0x2: ppuNameTableAdr+=0x800
                if ppuCReg1&0x4: ppuAdrIncrement=0x20
                else: ppuAdrIncrement=0x1
                if ppuCReg1&0x8: ppuSprPatTabAdr=0x1000
                else: ppuSprPatTabAdr=0x0
                if ppuCReg1&0x10: ppuBgrPatTabAdr=0x1000
                else: ppuBgrPatTabAdr=0x0        
                ppuSprSizeValue=ppuCReg1&0x20
                ppuNMIAfterVBlk=ppuCReg1&0x80
        elif adr==0x2001:
                ppuCReg2=val
                ppuColorModeSel=ppuCReg2&0x1
                ppuClipBackgrnd=ppuCReg2&0x2
                ppuClipSprites_=ppuCReg2&0x4
                ppuShowBackgrnd=ppuCReg2&0x8
                ppuShowSprites_=ppuCReg2&0x10
                ppuColorIntnsty=ppuCReg2>>4
        elif adr==0x2003:
                ppuSPRRAMaddres=val&0xff
        elif adr==0x2004:
                SPRRAM[ppuSPRRAMaddres]=val&0xff
                ppuSPRRAMaddres=(ppuSPRRAMaddres+1)&0xff
        elif adr==0x2005:
                if ppuVertOrHorVal==0:
                    tmpH=ppuHoristScroll
                    ppuHoristScroll=val&0xff
                    if ppuHoristScroll%8==0:
                        if val>tmpH:
                            for i in range(30):
                                tpFone2((ppuHoristScroll>>3),i)
                        else:
                            for i in range(30):
                                tpFone2((ppuHoristScroll>>3)-31,i)
                else:
                    ppuVerticScroll=val&0xff
                ppuVertOrHorVal^=1
        elif adr==0x2006:
                if ppuAdr2006Ofset == 0: 
                        ppuVRAMAdrValue=(val&0xff)<<8
                        ppuAdr2006Ofset=1
                else:
                        ppuVRAMAdrValue+=(val&0xff)
                        ppuAdr2006Ofset=0
        elif adr==0x2007:
                adr=ppuVRAMAdrValue&0x3FFF
                if adr>=0x3f00 and adr<0x4000:
                        adr=0x3f00+(adr&0x1f)
                        if (adr-0x3f00)%4==0: adr=0x3f00
                        tilesModified=1
                if adr>=0x3000 and adr<0x3f00:
                        adr-=0x1000
                if adr>=0x2000 and adr<0x3000:
                    if ppuVerticalMirr:
                        if adr>=0x2800:
                            adr-=0x800
                    else:
                        if adr>=0x2C00:
                            adr-=0x800
                        elif adr>=0x2800:
                            adr-=0x400
                        elif adr>=0x2400:
                            adr-=0x400

        #        if adr>0 and adr<0x4000:
#                        tilesModified=1
                ppuRAM[adr]=val&0xff
#                print hex(adr)
                if adr>=ppuNameTableAdr and adr<ppuNameTableAdr+0x400:
                    adr%=0x400
                    x=adr&0x1f
                    y=(adr>>5)%30
                    tpFone(x,y)
#                if adr>=0x23c0 and adr<0x2400:
#                    adr2=(adr-0x23c0)/15
#                    x=adr&0x1f
#                    y=(adr>>5)%30
#                    tpFone(x,y)
                ppuVRAMAdrValue+=ppuAdrIncrement

def dump_and_die():
        print("A: ",hex(A))
        print("X: ",hex(X))
        print("Y: ",hex(Y))
        print("PC: ",hex(PC))
        print("P: ",hex(P))
        print("S: ",hex(S))
        print("savepc: ",hex(savepc))
        print("saveflags: ",hex(saveflags))
        print("sum: ",hex(sum))
        print("value: ",hex(value))
        exit(1)

def dump_and_dont_die():
        print("A: ",hex(A)+"\t\t"+"X: ",hex(X)+"\t\t"+ "Y: ",hex(Y)+"\t\t"+ "PC: ",hex(PC)+"\t\t"+ "P: ",hex(P)+"\t\t"+ "S: ",hex(S)+"\t\t"+ "savepc: ",hex(savepc)+"\t\t"+ "saveflags: ",hex(saveflags)+"\t\t"+ "sum: ",hex(sum)+"\t\t"+"value: ",hex(value))


def verbose(s):
#        return
        print("%.2x %.2x %.2x %.4x %.2x %.2x %.2x (%1.4x) %s %s"%(A,X,Y,PC,P,S,opcode,savepc, str(instruction[opcode]).split()[1][1:],s))

def pGetMem(adr):
        global ppuStatusRegstr, ppuAdr2007Ofset, ppuVRAMAdrValue,ppuVRAMBuffer__
        #verbose("get "+hex(adr))
        adr&=0xffff
        if adr>=0x8000:
                return mmcRead[mMapper]._exec(adr-0x8000)
        elif adr<0x2000:
                #verbose("got ram: "+hex(ord(nesRAM[adr&0x7ff])))
                return nesRAM[adr&0x7ff]
        elif adr>=0x2000 and adr<0x4000:
                #verbose("get io:  "+hex(ord(ioMEM[adr&0x7])))
                if adr==0x2002:
                        out=ppuStatusRegstr
                        #verbose("ppu status: "+hex(out))
                        ppuStatusRegstr&=0x7f
                        return out
                if adr==0x2007:
                        adr=ppuVRAMAdrValue&0x3FFF
                        if adr>=0x3f00 and adr<0x4000:
                                adr=0x3f00+(adr&0xf)
#                                if (adr-0x3f00)%4==0: adr=0x3f00
                                ppuVRAMBuffer__        = ppuRAM[adr]
                                ppuVRAMAdrValue+=ppuAdrIncrement
                                return ppuVRAMBuffer__
                        if adr>=0x3000 and adr<0x3f00:
                                adr-=0x1000
                        if adr>=0x2000 and adr<0x3000:
                                if adr>=0x2800:
                                        adr-=0x800
                        out=ppuVRAMBuffer__
                        ppuVRAMBuffer__        = ppuRAM[adr]
                        #ppuVRAMAdrValue+=ppuAdrIncrement
                        ppuVRAMAdrValue+=1
                        #verbose("vram: "+hex(out))
                        return out
                return ioMEM[adr&0x7]
        elif adr>=0x4000 and adr<0x4020:
                #verbose("get io 2:  "+hex(ord(io2MEM[adr-0x4000])))
                if adr==0x4015 and ticks&2:
                        return ticks&0xff
                if adr==0x4016:
                        joyStrobe()
                        return jpdKeysBuffer__
                return io2MEM[adr-0x4000]
        elif adr>=0x6000:
                #verbose("get wram: "+hex(ord(wRAM[adr-0x6000])))
                return wRAM[adr-0x6000]
        else:
                #verbose("!other get "  + hex(adr))
                return 0

def pPutMem(adr, val):
        #verbose("put "+hex(adr)+" "+hex(val))
        adr&=0xffff
        if adr&0x8000:
                #verbose("put PRG: "+hex(adr-0x8000))
                mmcWrite[mMapper]._exec(adr,val)
        elif adr<0x2000:
                nesRAM[adr&0x7ff]=val&0xff
        elif adr>=0x2000 and adr<0x4000:
                ioMEM[adr&0x7]=val&0xff
                ppuProcessRegs(adr,val)
        elif adr>=0x4000 and adr<0x4020:
                io2MEM[adr-0x4000]=val&0xff
                ppuProcessRegs2(adr,val)
        elif adr>=0x6000:
                wRAM[adr-0x6000]=val&0xff
        else:
                #verbose("!other put "  + hex(adr)+" "+hex(val))
                return 0

class AddrMode: 
    pass

class mImplied(AddrMode):
    def _exec(self):
        pass

class mImmediate(AddrMode):
    def _exec(self):
        global savepc,PC
        savepc=PC
        PC+=1

class mAbs(AddrMode):
    def _exec(self):
        global savepc,PC
        savepc=pGetMem(PC)+(pGetMem(PC+1)<<8)
        PC+=2

class mRelative(AddrMode):
    def _exec(self):
        global savepc,PC,ticks
        savepc=pGetMem(PC)
        PC+=1
        if (savepc&0x80): savepc-=0x100
        if((savepc>>8)!=(PC>>8)):
                ticks+=1

class mIndirect(AddrMode):
    def _exec(self):
        global help,PC,savepc
        help=pGetMem(PC)+(pGetMem(PC+1)<<8)
        savepc=pGetMem(help)+(pGetMem(help+1)<<8)
        PC+=2

class mAbsx(AddrMode):
    def _exec(self):
        global savepc,PC,ticks
        savepc=pGetMem(PC) + (pGetMem(PC+1)<<8)
        PC+=2
        if nticks[opcode]==4:
                if (savepc>>8) != ((savepc+X)>>8):
                        ticks+=1
        savepc+=X

class mAbsy(AddrMode):
    def _exec(self):
        global savepc,PC,ticks
        savepc=pGetMem(PC) + (pGetMem(PC+1)<<8)
        PC+=2
        if nticks[opcode]==4:
                if (savepc>>8) != ((savepc+Y)>>8):
                        ticks+=1
        savepc+=Y        

class mZp(AddrMode):
    def _exec(self):
        global PC, savepc
        savepc=pGetMem(PC)
        PC+=1

class mZpx(AddrMode):
    def _exec(self):
        global PC, savepc
        savepc=pGetMem(PC)+X
        PC+=1
        savepc&=0xff

class mZpy(AddrMode):
    def _exec(self):
        global PC, savepc
        savepc=pGetMem(PC)+Y
        PC+=1
        savepc&=0xff

class mIndx(AddrMode):
    def _exec(self):
        global value, PC, savepc
        value=pGetMem(PC)+X
        savepc=pGetMem(value)+(pGetMem(value+1)<<8)
        PC+=1

class mIndy(AddrMode):
    def _exec(self):
        global value, PC, savepc,ticks
        value=pGetMem(PC)
        PC+=1
        savepc=pGetMem(value)+(pGetMem(value+1)<<8)
        if nticks[opcode]==5:
                if (savepc>>8) != ((savepc+Y)>>8):
                        ticks+=1
        savepc+=Y

class mIndabsx(AddrMode):
    def _exec(self):
        global help, savepc, PC
        help=pGetMem(PC)+(pGetMem(PC+1)<<8) + X
        savepc=pGetMem(help)+(pGetMem(help+1)<<8)

class mIndzp(AddrMode):
    def _exec(self):
        global value, savepc, PC
        value=pGetMem(PC)
        PC+=1
        savepc=pGetMem(value)+(pGetMem(value+1)<<8)

def checkFlags1(x):
        global P
        if x!=0: P&=0xfd
        else: P|=0x2
        if x&0x80: P|=0x80
        else: P&=0x7f

class Instruction:
    pass

class pAdc(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S
        adrmode[opcode]._exec()
        value=pGetMem(savepc)
        saveflags=P&1
        tmpA=A
        if (tmpA&0x80): tmpA-=0x100
        tmpV=value
        if (tmpV&0x80): tmpV-=0x100
        sum=tmpA+tmpV+saveflags
        if sum>0x7f or sum<-0x80: P|=0x40
        else: P&=0xbf
        sum=A+value+saveflags
        if sum>0xff: P|=1
        else: P&=0xfe
        A=sum&0xff
        if P&0x8:
                P&=0xfe
                if (A&0xf)>0x9: A+=0x6
                if (A&0xf0)>0x90:
                        A+=0x6
                        P|=1
        else:
                ticks+=1
        checkFlags1(A)

class pAnd(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S
        adrmode[opcode]._exec()
        value=pGetMem(savepc)
        A&=value
        checkFlags1(A)

class pAsl(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        adrmode[opcode]._exec()
        value=pGetMem(savepc)
        P=(P&0xfe)|((value>>7)&1)
        value=(value<<1)&0xff
        pPutMem(savepc,value)
        checkFlags1(value)

class pAsla(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        P=(P&0xfe)|((A>>7)&1)
        A=(A<<1)&0xff
        checkFlags1(A)

class pBcc(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value, PC
        if (P&1)==0:
                adrmode[opcode]._exec()
                PC+=savepc
                ticks+=1
        else:
                value+=pGetMem(PC)
                PC+=1
class pBcs(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        if P&1:
                adrmode[opcode]._exec()
                PC+=savepc
                ticks+=1
        else:
                value+=pGetMem(PC)
                PC+=1

class pBeq(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        if P&2:
                adrmode[opcode]._exec()
                PC+=savepc
                ticks+=1
        else:
                value+=pGetMem(PC)
                PC+=1

class pBit(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        adrmode[opcode]._exec()
        value=pGetMem(savepc)
        if value & A: P&=0xfd
        else: P|=2
        P=(P&0x3f)|(value&0xc0)

class pBmi(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        if P&0x80:
                adrmode[opcode]._exec()
                PC+=savepc
                ticks+=1
        else:
                value=pGetMem(PC)
                PC+=1

class pBne(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        if (P&0x2)==0:
                adrmode[opcode]._exec()
                PC+=(savepc)
                ticks+=1
        else:
                value=pGetMem(PC)
                PC+=1

class pBpl(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        if (P&0x80)==0:
                adrmode[opcode]._exec()
                PC+=savepc
                ticks+=1
        else:
                value=pGetMem(PC)
                PC+=1

class pBrk(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC,gotBrkNMI
        PC+=1
        pPutMem(0x100+S, PC>>8); S=(S-1)&0xff
        pPutMem(0x100+S, PC&0xff); S=(S-1)&0xff
        pPutMem(0x100+S, P); S=(S-1)&0xff
        P|=0x14
        PC=pGetMem(0xfffe)+(pGetMem(0xffff)<<8)

class pBvc(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        if (P&0x40)==0:
                adrmode[opcode]._exec()
                PC+=savepc
                ticks+=1
        else:
                value=pGetMem(PC)
                PC+=1

class pBvs(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        if P&0x40:
                adrmode[opcode]._exec()
                PC+=savepc
                ticks+=1
        else:
                value=pGetMem(PC)
                PC+=1

class pClc(Instruction):
    def _exec(self):
        global P
        P&=0xfe

class pCld(Instruction):
    def _exec(self):
        global P
        P&=0xf7

class pCli(Instruction):
    def _exec(self):
        global P
        P&=0xfb

class pClv(Instruction):
    def _exec(self):
        global P
        P&=0xbf

class pCmp(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        adrmode[opcode]._exec()
        value=pGetMem(savepc)
        if (A+0x100-value)>0xff: P|=0x1
        else: P&=0xfe
        value=(A+0x100-value)&0xff
        checkFlags1(value)

class pCpx(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        adrmode[opcode]._exec()
        value=pGetMem(savepc)
        if (X+0x100-value)>0xff: P|=0x1
        else: P&=0xfe
        value=(X+0x100-value)&0xff
        checkFlags1(value)

class pCpy(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        adrmode[opcode]._exec()
        value=pGetMem(savepc)
        if (Y+0x100-value)>0xff: P|=0x1
        else: P&=0xfe
        value=(Y+0x100-value)&0xff
        checkFlags1(value)

class pDec(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        adrmode[opcode]._exec()
        value=(pGetMem(savepc)-1)&0xff
        pPutMem(savepc, value)
        checkFlags1(value)

class pDex(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        X=(X-1)&0xff
        checkFlags1(X)

class pDey(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        Y=(Y-1)&0xff
        checkFlags1(Y)

class pEor(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        adrmode[opcode]._exec()
        A=(A^pGetMem(savepc))&0xff
        checkFlags1(A)

class pInc(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        adrmode[opcode]._exec()
        value=(pGetMem(savepc)+1)&0xff
        pPutMem(savepc,value)
        checkFlags1(value)

class pInx(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        X=(X+1)&0xff
        checkFlags1(X)

class pIny(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        Y=(Y+1)&0xff
        checkFlags1(Y)

class pJmp(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        adrmode[opcode]._exec()
        PC=savepc

class pJsr(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        PC+=1
        pPutMem(0x0100+S,PC>>8);S=(S-1)&0xff
        pPutMem(0x0100+S,PC&0xff); S=(S-1)&0xff
        PC-=1
        adrmode[opcode]._exec()
        PC=savepc

class pLda(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        adrmode[opcode]._exec()
        A=pGetMem(savepc)
        checkFlags1(A)

class pLdx(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        adrmode[opcode]._exec()
        X=pGetMem(savepc)
        checkFlags1(X)

class pLdy(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        adrmode[opcode]._exec()
        Y=pGetMem(savepc)
        checkFlags1(Y)

class pLsr(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        adrmode[opcode]._exec()
        value=pGetMem(savepc)
        P=(P&0xfe)|(value&0x1)
        value=value>>1
        pPutMem(savepc,value)
        checkFlags1(value)

class pLsra(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value
        P=(P&0xfe)|(A&1)
        A=A>>1
        checkFlags1(A)

class pNop(Instruction):
    def _exec(self):
        pass

class pOra(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        adrmode[opcode]._exec()
        A|=pGetMem(savepc)
        checkFlags1(A)

class pPha(Instruction):
    def _exec(self):
        global S
        pPutMem(0x100+S,A)
        S=(S-1)&0xff

class pPhp(Instruction):
    def _exec(self):
        global S
        pPutMem(0x100+S,P)
        S=(S-1)&0xff

class pPla(Instruction):
    def _exec(self):
        global A, S
        S=(S+1)&0xff
        A=pGetMem(S+0x100)
        checkFlags1(A)

class pPlp(Instruction):
    def _exec(self):
        global P, S
        S=(S+1)&0xff
        P=pGetMem(S+0x100)|0x20

class pRol(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        saveflags=(P&0x1)
        adrmode[opcode]._exec()
        value=pGetMem(savepc)
        P=(P&0xfe)|((value>>7)&0x1)
        value=(value<<1)&0xff
        value|=saveflags
        pPutMem(savepc,value)
        checkFlags1(value)

class pRola(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        saveflags=(P&0x1)
        P=(P&0xfe)|((A>>7)&0x1)
        A=(A<<1)&0xff
        A|=saveflags
        checkFlags1(A)

class pRor(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        saveflags=(P&0x1)
        adrmode[opcode]._exec()
        value=pGetMem(savepc)
        P=(P&0xfe)|(value&0x1)
        value=(value>>1)&0xff
        if saveflags: value |=0x80
        pPutMem(savepc,value)
        checkFlags1(value)

class pRora(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        saveflags=P&0x1
        P=(P&0xfe)|(A&0x1)
        A=(A>>1)&0xff
        if saveflags: A|=0x80
        checkFlags1(A)

class pRti(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        S=(S+1)&0xff
        P=pGetMem(0x100+S)|0x20
        S=(S+1)&0xff
        PC=pGetMem(0x100+S)
        S=(S+1)&0xff
        PC|=pGetMem(0x100+S)<<8

class pRts(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        S=(S+1)&0xff
        PC=pGetMem(0x100+S)
        S=(S+1)&0xff
        PC|=pGetMem(0x100+S)<<8
        PC+=1

class pSbc(Instruction):
    def _exec(self):
        global saveflags,A,X,Y,ticks,P,S,value,PC
        adrmode[opcode]._exec()
        value=(pGetMem(savepc)^0xff)&0xff
        saveflags=P&1
        tmpA=A
        if (tmpA&0x80): tmpA-=0x100
        tmpV=value
        if (tmpV&0x80): tmpV-=0x100
        sum=tmpA+tmpV+saveflags
        if sum>0x7f or sum<-0x80: P|=0x40
        else: P&=0xbf
        sum=A+value+saveflags
        if sum>0xff: P|=1
        else: P&=0xfe
        A=sum&0xff
        if P&0x8:
                P&=0xfe
                if (A&0xf)>0x9: A+=0x6
                if (A&0xf0)>0x90:
                        A+=0x6
                        P|=1
        else:
                ticks+=1
        checkFlags1(A)

class pSec(Instruction):
    def _exec(self):
        global P
        P|=0x1

class pSed(Instruction):
    def _exec(self):
        global P
        P|=0x8

class pSei(Instruction):
    def _exec(self):
        global P
        P|=0x4

class pSta(Instruction):
    def _exec(self):
        adrmode[opcode]._exec()
        pPutMem(savepc,A)

class pStx(Instruction):
    def _exec(self):
        adrmode[opcode]._exec()
        pPutMem(savepc,X)

class pSty(Instruction):
    def _exec(self):
        adrmode[opcode]._exec()
        pPutMem(savepc,Y)

class pTax(Instruction):
    def _exec(self):
        global X
        X=A
        checkFlags1(X)

class pTay(Instruction):
    def _exec(self):
        global Y
        Y=A
        checkFlags1(Y)

class pTsx(Instruction):
    def _exec(self):
        global X
        X=S
        checkFlags1(X)

class pTxa(Instruction):
    def _exec(self):
        global A
        A=X
        checkFlags1(A)

class pTxs(Instruction):
    def _exec(self):
        global S
        S=X

class pTya(Instruction):
    def _exec(self):
        global A
        A=Y
        checkFlags1(A)

class pBra(Instruction):
    def _exec(self):
        global PC,ticks
        adrmode[opcode]._exec()
        PC+=savepc
        ticks+=1

class pDea(Instruction):
    def _exec(self):
        global A
        A-=1
        checkFlags1(A)

class pIna(Instruction):
    def _exec(self):
        global A
        A+=1
        checkFlags1(A)

class pPhx(Instruction):
    def _exec(self):
        global S
        pPutMem(0x100+S,X)
        S=(S-1)&0xff

class pPlx(Instruction):
    def _exec(self):
        global X,S
        S=(S+1)&0xff
        X=pGetMem(S+0x100)
        checkFlags1(X)

class pPhy(Instruction):
    def _exec(self):
        global S
        pPutMem(0x100+S,Y)
        S=(S-1)&0xff

class pPly(Instruction):
    def _exec(self):
        global S,Y
        S=(S+1)&0xff
        Y=pGetMem(0x100+S)
        checkFlags1(Y)

class pStz(Instruction):
    def _exec(self):
        adrmode[opcode]._exec()
        pPutMem(savepc,0)

class pTsb(Instruction):
    def _exec(self):
        global P
        adrmode[opcode]._exec()
        tmp=pGetMem(savepc)|A
        pPutMem(savepc,tmp)
        if tmp: P&=0xfd
        else: P|=0x2

class pTrb(Instruction):
    def _exec(self):
        global P
        adrmode[opcode]._exec()
        tmp=pGetMem(savepc)&((A^0xff)&0xff)
        pPutMem(savepc,tmp)
        if tmp: P&=0xfd
        else: P|=0x2

nticks[0x00]=7; instruction[0x00]=pBrk(); adrmode[0x00]=mImplied()
nticks[0x01]=6; instruction[0x01]=pOra(); adrmode[0x01]=mIndx()
nticks[0x02]=2; instruction[0x02]=pNop(); adrmode[0x02]=mImplied()
nticks[0x03]=2; instruction[0x03]=pNop(); adrmode[0x03]=mImplied()
nticks[0x04]=3; instruction[0x04]=pTsb(); adrmode[0x04]=mZp()
nticks[0x05]=3; instruction[0x05]=pOra(); adrmode[0x05]=mZp()
nticks[0x06]=5; instruction[0x06]=pAsl(); adrmode[0x06]=mZp()
nticks[0x07]=2; instruction[0x07]=pNop(); adrmode[0x07]=mImplied()
nticks[0x08]=3; instruction[0x08]=pPhp(); adrmode[0x08]=mImplied()
nticks[0x09]=3; instruction[0x09]=pOra(); adrmode[0x09]=mImmediate()
nticks[0x0a]=2; instruction[0x0a]=pAsla(); adrmode[0x0a]=mImplied()
nticks[0x0b]=2; instruction[0x0b]=pNop(); adrmode[0x0b]=mImplied()
nticks[0x0c]=4; instruction[0x0c]=pTsb(); adrmode[0x0c]=mAbs()
nticks[0x0d]=4; instruction[0x0d]=pOra(); adrmode[0x0d]=mAbs()
nticks[0x0e]=6; instruction[0x0e]=pAsl(); adrmode[0x0e]=mAbs()
nticks[0x0f]=2; instruction[0x0f]=pNop(); adrmode[0x0f]=mImplied()
nticks[0x10]=2; instruction[0x10]=pBpl(); adrmode[0x10]=mRelative()
nticks[0x11]=5; instruction[0x11]=pOra(); adrmode[0x11]=mIndy()
nticks[0x12]=3; instruction[0x12]=pOra(); adrmode[0x12]=mIndzp()
nticks[0x13]=2; instruction[0x13]=pNop(); adrmode[0x13]=mImplied()
nticks[0x14]=3; instruction[0x14]=pTrb(); adrmode[0x14]=mZp()
nticks[0x15]=4; instruction[0x15]=pOra(); adrmode[0x15]=mZpx()
nticks[0x16]=6; instruction[0x16]=pAsl(); adrmode[0x16]=mZpx()
nticks[0x17]=2; instruction[0x17]=pNop(); adrmode[0x17]=mImplied()
nticks[0x18]=2; instruction[0x18]=pClc(); adrmode[0x18]=mImplied()
nticks[0x19]=4; instruction[0x19]=pOra(); adrmode[0x19]=mAbsy()
nticks[0x1a]=2; instruction[0x1a]=pIna(); adrmode[0x1a]=mImplied()
nticks[0x1b]=2; instruction[0x1b]=pNop(); adrmode[0x1b]=mImplied()
nticks[0x1c]=4; instruction[0x1c]=pTrb(); adrmode[0x1c]=mAbs()
nticks[0x1d]=4; instruction[0x1d]=pOra(); adrmode[0x1d]=mAbsx()
nticks[0x1e]=7; instruction[0x1e]=pAsl(); adrmode[0x1e]=mAbsx()
nticks[0x1f]=2; instruction[0x1f]=pNop(); adrmode[0x1f]=mImplied()
nticks[0x20]=6; instruction[0x20]=pJsr(); adrmode[0x20]=mAbs()
nticks[0x21]=6; instruction[0x21]=pAnd(); adrmode[0x21]=mIndx()
nticks[0x22]=2; instruction[0x22]=pNop(); adrmode[0x22]=mImplied()
nticks[0x23]=2; instruction[0x23]=pNop(); adrmode[0x23]=mImplied()
nticks[0x24]=3; instruction[0x24]=pBit(); adrmode[0x24]=mZp()
nticks[0x25]=3; instruction[0x25]=pAnd(); adrmode[0x25]=mZp()
nticks[0x26]=5; instruction[0x26]=pRol(); adrmode[0x26]=mZp()
nticks[0x27]=2; instruction[0x27]=pNop(); adrmode[0x27]=mImplied()
nticks[0x28]=4; instruction[0x28]=pPlp(); adrmode[0x28]=mImplied()
nticks[0x29]=3; instruction[0x29]=pAnd(); adrmode[0x29]=mImmediate()
nticks[0x2a]=2; instruction[0x2a]=pRola(); adrmode[0x2a]=mImplied()
nticks[0x2b]=2; instruction[0x2b]=pNop(); adrmode[0x2b]=mImplied()
nticks[0x2c]=4; instruction[0x2c]=pBit(); adrmode[0x2c]=mAbs()
nticks[0x2d]=4; instruction[0x2d]=pAnd(); adrmode[0x2d]=mAbs()
nticks[0x2e]=6; instruction[0x2e]=pRol(); adrmode[0x2e]=mAbs()
nticks[0x2f]=2; instruction[0x2f]=pNop(); adrmode[0x2f]=mImplied()
nticks[0x30]=2; instruction[0x30]=pBmi(); adrmode[0x30]=mRelative()
nticks[0x31]=5; instruction[0x31]=pAnd(); adrmode[0x31]=mIndy()
nticks[0x32]=3; instruction[0x32]=pAnd(); adrmode[0x32]=mIndzp()
nticks[0x33]=2; instruction[0x33]=pNop(); adrmode[0x33]=mImplied()
nticks[0x34]=4; instruction[0x34]=pBit(); adrmode[0x34]=mZpx()
nticks[0x35]=4; instruction[0x35]=pAnd(); adrmode[0x35]=mZpx()
nticks[0x36]=6; instruction[0x36]=pRol(); adrmode[0x36]=mZpx()
nticks[0x37]=2; instruction[0x37]=pNop(); adrmode[0x37]=mImplied()
nticks[0x38]=2; instruction[0x38]=pSec(); adrmode[0x38]=mImplied()
nticks[0x39]=4; instruction[0x39]=pAnd(); adrmode[0x39]=mAbsy()
nticks[0x3a]=2; instruction[0x3a]=pDea(); adrmode[0x3a]=mImplied()
nticks[0x3b]=2; instruction[0x3b]=pNop(); adrmode[0x3b]=mImplied()
nticks[0x3c]=4; instruction[0x3c]=pBit(); adrmode[0x3c]=mAbsx()
nticks[0x3d]=4; instruction[0x3d]=pAnd(); adrmode[0x3d]=mAbsx()
nticks[0x3e]=7; instruction[0x3e]=pRol(); adrmode[0x3e]=mAbsx()
nticks[0x3f]=2; instruction[0x3f]=pNop(); adrmode[0x3f]=mImplied()
nticks[0x40]=6; instruction[0x40]=pRti(); adrmode[0x40]=mImplied()
nticks[0x41]=6; instruction[0x41]=pEor(); adrmode[0x41]=mIndx()
nticks[0x42]=2; instruction[0x42]=pNop(); adrmode[0x42]=mImplied()
nticks[0x43]=2; instruction[0x43]=pNop(); adrmode[0x43]=mImplied()
nticks[0x44]=2; instruction[0x44]=pNop(); adrmode[0x44]=mImplied()
nticks[0x45]=3; instruction[0x45]=pEor(); adrmode[0x45]=mZp()
nticks[0x46]=5; instruction[0x46]=pLsr(); adrmode[0x46]=mZp()
nticks[0x47]=2; instruction[0x47]=pNop(); adrmode[0x47]=mImplied()
nticks[0x48]=3; instruction[0x48]=pPha(); adrmode[0x48]=mImplied()
nticks[0x49]=3; instruction[0x49]=pEor(); adrmode[0x49]=mImmediate()
nticks[0x4a]=2; instruction[0x4a]=pLsra(); adrmode[0x4a]=mImplied()
nticks[0x4b]=2; instruction[0x4b]=pNop(); adrmode[0x4b]=mImplied()
nticks[0x4c]=3; instruction[0x4c]=pJmp(); adrmode[0x4c]=mAbs()
nticks[0x4d]=4; instruction[0x4d]=pEor(); adrmode[0x4d]=mAbs()
nticks[0x4e]=6; instruction[0x4e]=pLsr(); adrmode[0x4e]=mAbs()
nticks[0x4f]=2; instruction[0x4f]=pNop(); adrmode[0x4f]=mImplied()
nticks[0x50]=2; instruction[0x50]=pBvc(); adrmode[0x50]=mRelative()
nticks[0x51]=5; instruction[0x51]=pEor(); adrmode[0x51]=mIndy()
nticks[0x52]=3; instruction[0x52]=pEor(); adrmode[0x52]=mIndzp()
nticks[0x53]=2; instruction[0x53]=pNop(); adrmode[0x53]=mImplied()
nticks[0x54]=2; instruction[0x54]=pNop(); adrmode[0x54]=mImplied()
nticks[0x55]=4; instruction[0x55]=pEor(); adrmode[0x55]=mZpx()
nticks[0x56]=6; instruction[0x56]=pLsr(); adrmode[0x56]=mZpx()
nticks[0x57]=2; instruction[0x57]=pNop(); adrmode[0x57]=mImplied()
nticks[0x58]=2; instruction[0x58]=pCli(); adrmode[0x58]=mImplied()
nticks[0x59]=4; instruction[0x59]=pEor(); adrmode[0x59]=mAbsy()
nticks[0x5a]=3; instruction[0x5a]=pPhy(); adrmode[0x5a]=mImplied()
nticks[0x5b]=2; instruction[0x5b]=pNop(); adrmode[0x5b]=mImplied()
nticks[0x5c]=2; instruction[0x5c]=pNop(); adrmode[0x5c]=mImplied()
nticks[0x5d]=4; instruction[0x5d]=pEor(); adrmode[0x5d]=mAbsx()
nticks[0x5e]=7; instruction[0x5e]=pLsr(); adrmode[0x5e]=mAbsx()
nticks[0x5f]=2; instruction[0x5f]=pNop(); adrmode[0x5f]=mImplied()
nticks[0x60]=6; instruction[0x60]=pRts(); adrmode[0x60]=mImplied()
nticks[0x61]=6; instruction[0x61]=pAdc(); adrmode[0x61]=mIndx()
nticks[0x62]=2; instruction[0x62]=pNop(); adrmode[0x62]=mImplied()
nticks[0x63]=2; instruction[0x63]=pNop(); adrmode[0x63]=mImplied()
nticks[0x64]=3; instruction[0x64]=pStz(); adrmode[0x64]=mZp()
nticks[0x65]=3; instruction[0x65]=pAdc(); adrmode[0x65]=mZp()
nticks[0x66]=5; instruction[0x66]=pRor(); adrmode[0x66]=mZp()
nticks[0x67]=2; instruction[0x67]=pNop(); adrmode[0x67]=mImplied()
nticks[0x68]=4; instruction[0x68]=pPla(); adrmode[0x68]=mImplied()
nticks[0x69]=3; instruction[0x69]=pAdc(); adrmode[0x69]=mImmediate()
nticks[0x6a]=2; instruction[0x6a]=pRora(); adrmode[0x6a]=mImplied()
nticks[0x6b]=2; instruction[0x6b]=pNop(); adrmode[0x6b]=mImplied()
nticks[0x6c]=5; instruction[0x6c]=pJmp(); adrmode[0x6c]=mIndirect()
nticks[0x6d]=4; instruction[0x6d]=pAdc(); adrmode[0x6d]=mAbs()
nticks[0x6e]=6; instruction[0x6e]=pRor(); adrmode[0x6e]=mAbs()
nticks[0x6f]=2; instruction[0x6f]=pNop(); adrmode[0x6f]=mImplied()
nticks[0x70]=2; instruction[0x70]=pBvs(); adrmode[0x70]=mRelative()
nticks[0x71]=5; instruction[0x71]=pAdc(); adrmode[0x71]=mIndy()
nticks[0x72]=3; instruction[0x72]=pAdc(); adrmode[0x72]=mIndzp()
nticks[0x73]=2; instruction[0x73]=pNop(); adrmode[0x73]=mImplied()
nticks[0x74]=4; instruction[0x74]=pStz(); adrmode[0x74]=mZpx()
nticks[0x75]=4; instruction[0x75]=pAdc(); adrmode[0x75]=mZpx()
nticks[0x76]=6; instruction[0x76]=pRor(); adrmode[0x76]=mZpx()
nticks[0x77]=2; instruction[0x77]=pNop(); adrmode[0x77]=mImplied()
nticks[0x78]=2; instruction[0x78]=pSei(); adrmode[0x78]=mImplied()
nticks[0x79]=4; instruction[0x79]=pAdc(); adrmode[0x79]=mAbsy()
nticks[0x7a]=4; instruction[0x7a]=pPly(); adrmode[0x7a]=mImplied()
nticks[0x7b]=2; instruction[0x7b]=pNop(); adrmode[0x7b]=mImplied()
nticks[0x7c]=6; instruction[0x7c]=pJmp(); adrmode[0x7c]=mIndabsx()
nticks[0x7d]=4; instruction[0x7d]=pAdc(); adrmode[0x7d]=mAbsx()
nticks[0x7e]=7; instruction[0x7e]=pRor(); adrmode[0x7e]=mAbsx()
nticks[0x7f]=2; instruction[0x7f]=pNop(); adrmode[0x7f]=mImplied()
nticks[0x80]=2; instruction[0x80]=pBra(); adrmode[0x80]=mRelative()
nticks[0x81]=6; instruction[0x81]=pSta(); adrmode[0x81]=mIndx()
nticks[0x82]=2; instruction[0x82]=pNop(); adrmode[0x82]=mImplied()
nticks[0x83]=2; instruction[0x83]=pNop(); adrmode[0x83]=mImplied()
nticks[0x84]=2; instruction[0x84]=pSty(); adrmode[0x84]=mZp()
nticks[0x85]=2; instruction[0x85]=pSta(); adrmode[0x85]=mZp()
nticks[0x86]=2; instruction[0x86]=pStx(); adrmode[0x86]=mZp()
nticks[0x87]=2; instruction[0x87]=pNop(); adrmode[0x87]=mImplied()
nticks[0x88]=2; instruction[0x88]=pDey(); adrmode[0x88]=mImplied()
nticks[0x89]=2; instruction[0x89]=pBit(); adrmode[0x89]=mImmediate()
nticks[0x8a]=2; instruction[0x8a]=pTxa(); adrmode[0x8a]=mImplied()
nticks[0x8b]=2; instruction[0x8b]=pNop(); adrmode[0x8b]=mImplied()
nticks[0x8c]=4; instruction[0x8c]=pSty(); adrmode[0x8c]=mAbs()
nticks[0x8d]=4; instruction[0x8d]=pSta(); adrmode[0x8d]=mAbs()
nticks[0x8e]=4; instruction[0x8e]=pStx(); adrmode[0x8e]=mAbs()
nticks[0x8f]=2; instruction[0x8f]=pNop(); adrmode[0x8f]=mImplied()
nticks[0x90]=2; instruction[0x90]=pBcc(); adrmode[0x90]=mRelative()
nticks[0x91]=6; instruction[0x91]=pSta(); adrmode[0x91]=mIndy()
nticks[0x92]=3; instruction[0x92]=pSta(); adrmode[0x92]=mIndzp()
nticks[0x93]=2; instruction[0x93]=pNop(); adrmode[0x93]=mImplied()
nticks[0x94]=4; instruction[0x94]=pSty(); adrmode[0x94]=mZpx()
nticks[0x95]=4; instruction[0x95]=pSta(); adrmode[0x95]=mZpx()
nticks[0x96]=4; instruction[0x96]=pStx(); adrmode[0x96]=mZpy()
nticks[0x97]=2; instruction[0x97]=pNop(); adrmode[0x97]=mImplied()
nticks[0x98]=2; instruction[0x98]=pTya(); adrmode[0x98]=mImplied()
nticks[0x99]=5; instruction[0x99]=pSta(); adrmode[0x99]=mAbsy()
nticks[0x9a]=2; instruction[0x9a]=pTxs(); adrmode[0x9a]=mImplied()
nticks[0x9b]=2; instruction[0x9b]=pNop(); adrmode[0x9b]=mImplied()
nticks[0x9c]=4; instruction[0x9c]=pStz(); adrmode[0x9c]=mAbs()
nticks[0x9d]=5; instruction[0x9d]=pSta(); adrmode[0x9d]=mAbsx()
nticks[0x9e]=5; instruction[0x9e]=pStz(); adrmode[0x9e]=mAbsx()
nticks[0x9f]=2; instruction[0x9f]=pNop(); adrmode[0x9f]=mImplied()
nticks[0xa0]=3; instruction[0xa0]=pLdy(); adrmode[0xa0]=mImmediate()
nticks[0xa1]=6; instruction[0xa1]=pLda(); adrmode[0xa1]=mIndx()
nticks[0xa2]=3; instruction[0xa2]=pLdx(); adrmode[0xa2]=mImmediate()
nticks[0xa3]=2; instruction[0xa3]=pNop(); adrmode[0xa3]=mImplied()
nticks[0xa4]=3; instruction[0xa4]=pLdy(); adrmode[0xa4]=mZp()
nticks[0xa5]=3; instruction[0xa5]=pLda(); adrmode[0xa5]=mZp()
nticks[0xa6]=3; instruction[0xa6]=pLdx(); adrmode[0xa6]=mZp()
nticks[0xa7]=2; instruction[0xa7]=pNop(); adrmode[0xa7]=mImplied()
nticks[0xa8]=2; instruction[0xa8]=pTay(); adrmode[0xa8]=mImplied()
nticks[0xa9]=3; instruction[0xa9]=pLda(); adrmode[0xa9]=mImmediate()
nticks[0xaa]=2; instruction[0xaa]=pTax(); adrmode[0xaa]=mImplied()
nticks[0xab]=2; instruction[0xab]=pNop(); adrmode[0xab]=mImplied()
nticks[0xac]=4; instruction[0xac]=pLdy(); adrmode[0xac]=mAbs()
nticks[0xad]=4; instruction[0xad]=pLda(); adrmode[0xad]=mAbs()
nticks[0xae]=4; instruction[0xae]=pLdx(); adrmode[0xae]=mAbs()
nticks[0xaf]=2; instruction[0xaf]=pNop(); adrmode[0xaf]=mImplied()
nticks[0xb0]=2; instruction[0xb0]=pBcs(); adrmode[0xb0]=mRelative()
nticks[0xb1]=5; instruction[0xb1]=pLda(); adrmode[0xb1]=mIndy()
nticks[0xb2]=3; instruction[0xb2]=pLda(); adrmode[0xb2]=mIndzp()
nticks[0xb3]=2; instruction[0xb3]=pNop(); adrmode[0xb3]=mImplied()
nticks[0xb4]=4; instruction[0xb4]=pLdy(); adrmode[0xb4]=mZpx()
nticks[0xb5]=4; instruction[0xb5]=pLda(); adrmode[0xb5]=mZpx()
nticks[0xb6]=4; instruction[0xb6]=pLdx(); adrmode[0xb6]=mZpy()
nticks[0xb7]=2; instruction[0xb7]=pNop(); adrmode[0xb7]=mImplied()
nticks[0xb8]=2; instruction[0xb8]=pClv(); adrmode[0xb8]=mImplied()
nticks[0xb9]=4; instruction[0xb9]=pLda(); adrmode[0xb9]=mAbsy()
nticks[0xba]=2; instruction[0xba]=pTsx(); adrmode[0xba]=mImplied()
nticks[0xbb]=2; instruction[0xbb]=pNop(); adrmode[0xbb]=mImplied()
nticks[0xbc]=4; instruction[0xbc]=pLdy(); adrmode[0xbc]=mAbsx()
nticks[0xbd]=4; instruction[0xbd]=pLda(); adrmode[0xbd]=mAbsx()
nticks[0xbe]=4; instruction[0xbe]=pLdx(); adrmode[0xbe]=mAbsy()
nticks[0xbf]=2; instruction[0xbf]=pNop(); adrmode[0xbf]=mImplied()
nticks[0xc0]=3; instruction[0xc0]=pCpy(); adrmode[0xc0]=mImmediate()
nticks[0xc1]=6; instruction[0xc1]=pCmp(); adrmode[0xc1]=mIndx()
nticks[0xc2]=2; instruction[0xc2]=pNop(); adrmode[0xc2]=mImplied()
nticks[0xc3]=2; instruction[0xc3]=pNop(); adrmode[0xc3]=mImplied()
nticks[0xc4]=3; instruction[0xc4]=pCpy(); adrmode[0xc4]=mZp()
nticks[0xc5]=3; instruction[0xc5]=pCmp(); adrmode[0xc5]=mZp()
nticks[0xc6]=5; instruction[0xc6]=pDec(); adrmode[0xc6]=mZp()
nticks[0xc7]=2; instruction[0xc7]=pNop(); adrmode[0xc7]=mImplied()
nticks[0xc8]=2; instruction[0xc8]=pIny(); adrmode[0xc8]=mImplied()
nticks[0xc9]=3; instruction[0xc9]=pCmp(); adrmode[0xc9]=mImmediate()
nticks[0xca]=2; instruction[0xca]=pDex(); adrmode[0xca]=mImplied()
nticks[0xcb]=2; instruction[0xcb]=pNop(); adrmode[0xcb]=mImplied()
nticks[0xcc]=4; instruction[0xcc]=pCpy(); adrmode[0xcc]=mAbs()
nticks[0xcd]=4; instruction[0xcd]=pCmp(); adrmode[0xcd]=mAbs()
nticks[0xce]=6; instruction[0xce]=pDec(); adrmode[0xce]=mAbs()
nticks[0xcf]=2; instruction[0xcf]=pNop(); adrmode[0xcf]=mImplied()
nticks[0xd0]=2; instruction[0xd0]=pBne(); adrmode[0xd0]=mRelative()
nticks[0xd1]=5; instruction[0xd1]=pCmp(); adrmode[0xd1]=mIndy()
nticks[0xd2]=3; instruction[0xd2]=pCmp(); adrmode[0xd2]=mIndzp()
nticks[0xd3]=2; instruction[0xd3]=pNop(); adrmode[0xd3]=mImplied()
nticks[0xd4]=2; instruction[0xd4]=pNop(); adrmode[0xd4]=mImplied()
nticks[0xd5]=4; instruction[0xd5]=pCmp(); adrmode[0xd5]=mZpx()
nticks[0xd6]=6; instruction[0xd6]=pDec(); adrmode[0xd6]=mZpx()
nticks[0xd7]=2; instruction[0xd7]=pNop(); adrmode[0xd7]=mImplied()
nticks[0xd8]=2; instruction[0xd8]=pCld(); adrmode[0xd8]=mImplied()
nticks[0xd9]=4; instruction[0xd9]=pCmp(); adrmode[0xd9]=mAbsy()
nticks[0xda]=3; instruction[0xda]=pPhx(); adrmode[0xda]=mImplied()
nticks[0xdb]=2; instruction[0xdb]=pNop(); adrmode[0xdb]=mImplied()
nticks[0xdc]=2; instruction[0xdc]=pNop(); adrmode[0xdc]=mImplied()
nticks[0xdd]=4; instruction[0xdd]=pCmp(); adrmode[0xdd]=mAbsx()
nticks[0xde]=7; instruction[0xde]=pDec(); adrmode[0xde]=mAbsx()
nticks[0xdf]=2; instruction[0xdf]=pNop(); adrmode[0xdf]=mImplied()
nticks[0xe0]=3; instruction[0xe0]=pCpx(); adrmode[0xe0]=mImmediate()
nticks[0xe1]=6; instruction[0xe1]=pSbc(); adrmode[0xe1]=mIndx()
nticks[0xe2]=2; instruction[0xe2]=pNop(); adrmode[0xe2]=mImplied()
nticks[0xe3]=2; instruction[0xe3]=pNop(); adrmode[0xe3]=mImplied()
nticks[0xe4]=3; instruction[0xe4]=pCpx(); adrmode[0xe4]=mZp()
nticks[0xe5]=3; instruction[0xe5]=pSbc(); adrmode[0xe5]=mZp()
nticks[0xe6]=5; instruction[0xe6]=pInc(); adrmode[0xe6]=mZp()
nticks[0xe7]=2; instruction[0xe7]=pNop(); adrmode[0xe7]=mImplied()
nticks[0xe8]=2; instruction[0xe8]=pInx(); adrmode[0xe8]=mImplied()
nticks[0xe9]=3; instruction[0xe9]=pSbc(); adrmode[0xe9]=mImmediate()
nticks[0xea]=2; instruction[0xea]=pNop(); adrmode[0xea]=mImplied()
nticks[0xeb]=2; instruction[0xeb]=pNop(); adrmode[0xeb]=mImplied()
nticks[0xec]=4; instruction[0xec]=pCpx(); adrmode[0xec]=mAbs()
nticks[0xed]=4; instruction[0xed]=pSbc(); adrmode[0xed]=mAbs()
nticks[0xee]=6; instruction[0xee]=pInc(); adrmode[0xee]=mAbs()
nticks[0xef]=2; instruction[0xef]=pNop(); adrmode[0xef]=mImplied()
nticks[0xf0]=2; instruction[0xf0]=pBeq(); adrmode[0xf0]=mRelative()
nticks[0xf1]=5; instruction[0xf1]=pSbc(); adrmode[0xf1]=mIndy()
nticks[0xf2]=3; instruction[0xf2]=pSbc(); adrmode[0xf2]=mIndzp()
nticks[0xf3]=2; instruction[0xf3]=pNop(); adrmode[0xf3]=mImplied()
nticks[0xf4]=2; instruction[0xf4]=pNop(); adrmode[0xf4]=mImplied()
nticks[0xf5]=4; instruction[0xf5]=pSbc(); adrmode[0xf5]=mZpx()
nticks[0xf6]=6; instruction[0xf6]=pInc(); adrmode[0xf6]=mZpx()
nticks[0xf7]=2; instruction[0xf7]=pNop(); adrmode[0xf7]=mImplied()
nticks[0xf8]=2; instruction[0xf8]=pSed(); adrmode[0xf8]=mImplied()
nticks[0xf9]=4; instruction[0xf9]=pSbc(); adrmode[0xf9]=mAbsy()
nticks[0xfa]=4; instruction[0xfa]=pPlx(); adrmode[0xfa]=mImplied()
nticks[0xfb]=2; instruction[0xfb]=pNop(); adrmode[0xfb]=mImplied()
nticks[0xfc]=2; instruction[0xfc]=pNop(); adrmode[0xfc]=mImplied()
nticks[0xfd]=4; instruction[0xfd]=pSbc(); adrmode[0xfd]=mAbsx()
nticks[0xfe]=7; instruction[0xfe]=pInc(); adrmode[0xfe]=mAbsx()
nticks[0xff]=2; instruction[0xff]=pNop(); adrmode[0xff]=mImplied()


def pReset():
        global A, X, Y, P, S, PC
        A=X=Y=P=0
        P |= 0x20
        S=0xff
        PC=pGetMem(0xfffc)
        PC|=pGetMem(0xfffd)<<8

def pNmi():
        global S,P,PC
        pPutMem(0x100+S,PC>>8);S=(S-1)&0xff
        pPutMem(0x100+S,PC&0xff);S=(S-1)&0xff
        pPutMem(0x100+S,P);S=(S-1)&0xff
        P|=0x4
        PC=pGetMem(0xfffa)
        PC|=pGetMem(0xfffb)<<8

def pIrq():
        global S,P,PC
        pPutMem(0x100+S,PC>>8);S=(S-1)&0xff
        pPutMem(0x100+S,PC&0xff);S=(S-1)&0xff
        pPutMem(0x100+S,P);S=(S-1)&0xff
        P|=0x4
        PC=pGetMem(0xfffe)
        PC|=pGetMem(0xffff)<<8

def pExec():
        global ticks,opcode,PC, ppuStatusRegstr,PS, keys, ppuVRAMAdrValue,addr0,tilesModified

        tscanline=0
        nscanline=0
        vbwait=0
        tt=0
        oe = 0
        while True:
                opcode=pGetMem(PC)
                PC+=1
                instruction[opcode]._exec()
                ticks+=nticks[opcode]
                tscanline+=ticks
                tt+=1
                if vbwait>0:
                        vbwait-=1
                if vbwait==0 and tscanline>114:
                        tscanline=0
                        nscanline+=1
                        if nscanline==240:
                                nscanline=0
                                if ppuNMIAfterVBlk:
                                    pNmi()
                                ppuStatusRegstr|=0x80
                                ppuStatusRegstr^=ppuStatusRegstr&0x40
                                vbwait=20
                                if tilesModified:
                                        tpF()
                                        tilesModified=0
                                return
                        ppuDoScanline(nscanline)
                ticks=0

def read_ines(name):
        global PRGbks, CHRbks,mMapper,ppuVerticalMirr,ppu4ScreensMode
        nPRGbks=0
        nCHRbks=0
        nRAMbks=0
        rCTRLbyte1=0
        rCTRLbyte1=0
        f=open(name, 'rb')
        if f.read(3)!= b"NES":
                print("Not ines")
                return
        if f.read(1)!= b'\x1a':
                print("Not ines")
                return
        print("Reading ines file")
        nPRGbks=ord(f.read(1))
        print(nPRGbks, "PRG-rom banks")
        nCHRbks=ord(f.read(1))
        print(nCHRbks, "CHR-rom banks")
        rCTRLbyte1=ord(f.read(1))
        rCTRLbyte2=ord(f.read(1))
        ppuVerticalMirr=(rCTRLbyte1&1)
        print("Vertical mirroring?", (ppuVerticalMirr!=0))
        mMapper=(rCTRLbyte1>>4)+((rCTRLbyte2>>4)<<4)
        print("Memory mapper no:", mMapper)
        if mmcLoad[mMapper] is None:
            print("I don't have this mapper :(")
            exit(0)
        ppu4ScreensMode=rCTRLbyte1&8
        print("4 screens mirroring?", (ppu4ScreensMode!=0))
        nRAMbks=ord(f.read(1))
        if nRAMbks==0: nRAMbks=1
        print(nRAMbks, "RAM banks")
        f.read(7)
        if rCTRLbyte1&4: f.read(512)
        for i in range(nPRGbks):
                PRGbks+=[list(f.read(0x4000))]
        for i in range(nCHRbks):
                CHRbks+=[list(f.read(0x2000))]
        mmcLoad[mMapper]._exec()

if __name__ == '__main__':
    read_ines('mario_bros.nes')
    setkeys({'q': 0, 'w': 0, 'a': 0, 's': 0, 'UP': 0, 'DOWN': 0, 'LEFT': 0, 'RIGHT': 0})
    setkeys2((0,))
    getscreen()
    pReset()
    x = 0
    while True:
        print(x)
        x += 1
        pExec()
