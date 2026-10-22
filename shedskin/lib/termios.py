# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

# tcgetattr() returns a list holding six ints and, at index 6 (tty.CC), a list
# of control characters. as shedskin lists are homogeneous, these are modeled
# by two list-like classes: tcattrs, and cclist (holding 1-byte bytes objects).
# indexing a tcattrs with literal 6, CC or tty.CC is redirected to __getcc__
# (see infer.py), so the cclist type does not mix with the int elements.

class error(Exception):
    pass

class cclist(pyseq):
    def __init__(self):
        self.unit = b''
    def __getitem__(self, i):
        return self.unit
    def __setitem__(self, i, v):  # int or bytes
        pass
    def __len__(self):
        return 1
    def __iter__(self):
        return __iter(self.unit)
    def __eq__(self, other):
        return True
    def __ne__(self, other):
        return True
    def __repr__(self):
        return ''
    def __copy__(self):
        return self
    def __deepcopy__(self):
        return self

class tcattrs:
    def __init__(self):
        self.cc = cclist()
    def __getitem__(self, i):
        return 1
    def __getcc__(self, i):
        return self.cc
    def __setitem__(self, i, v):  # int or cclist
        pass
    def __len__(self):
        return 7
    def __eq__(self, other):
        return True
    def __ne__(self, other):
        return True
    def __repr__(self):
        return ''
    def __copy__(self):
        return self
    def __deepcopy__(self):
        return self

# like CPython, fd is a file descriptor or an object with a fileno() method

def tcgetattr(fd):
    fd.fileno()
    return tcattrs()

def tcsetattr(fd, when, attributes):
    fd.fileno()

def tcsendbreak(fd, duration):
    fd.fileno()

def tcdrain(fd):
    fd.fileno()

def tcflush(fd, queue):
    fd.fileno()

def tcflow(fd, action):
    fd.fileno()

def tcgetwinsize(fd):
    fd.fileno()
    return (1, 1)

def tcsetwinsize(fd, winsize):
    fd.fileno()
    len(winsize)
    winsize[0]

B0 = 0
B1000000 = 0
B110 = 0
B115200 = 0
B1152000 = 0
B1200 = 0
B134 = 0
B150 = 0
B1500000 = 0
B1800 = 0
B19200 = 0
B200 = 0
B2000000 = 0
B230400 = 0
B2400 = 0
B2500000 = 0
B300 = 0
B3000000 = 0
B3500000 = 0
B38400 = 0
B4000000 = 0
B460800 = 0
B4800 = 0
B50 = 0
B500000 = 0
B57600 = 0
B576000 = 0
B600 = 0
B75 = 0
B921600 = 0
B9600 = 0
BRKINT = 0
BS0 = 0
BS1 = 0
BSDLY = 0
CBAUD = 0
CBAUDEX = 0
CDSUSP = 0
CEOF = 0
CEOL = 0
CEOT = 0
CERASE = 0
CFLUSH = 0
CIBAUD = 0
CINTR = 0
CKILL = 0
CLNEXT = 0
CLOCAL = 0
CQUIT = 0
CR0 = 0
CR1 = 0
CR2 = 0
CR3 = 0
CRDLY = 0
CREAD = 0
CRPRNT = 0
CRTSCTS = 0
CS5 = 0
CS6 = 0
CS7 = 0
CS8 = 0
CSIZE = 0
CSTART = 0
CSTOP = 0
CSTOPB = 0
CSUSP = 0
CWERASE = 0
ECHO = 0
ECHOCTL = 0
ECHOE = 0
ECHOK = 0
ECHOKE = 0
ECHONL = 0
ECHOPRT = 0
EXTA = 0
EXTB = 0
EXTPROC = 0
FF0 = 0
FF1 = 0
FFDLY = 0
FIOASYNC = 0
FIOCLEX = 0
FIONBIO = 0
FIONCLEX = 0
FIONREAD = 0
FLUSHO = 0
HUPCL = 0
ICANON = 0
ICRNL = 0
IEXTEN = 0
IGNBRK = 0
IGNCR = 0
IGNPAR = 0
IMAXBEL = 0
INLCR = 0
INPCK = 0
IOCSIZE_MASK = 0
IOCSIZE_SHIFT = 0
ISIG = 0
ISTRIP = 0
IUCLC = 0
IUTF8 = 0
IXANY = 0
IXOFF = 0
IXON = 0
NCC = 0
NCCS = 0
NL0 = 0
NL1 = 0
NLDLY = 0
NOFLSH = 0
N_MOUSE = 0
N_PPP = 0
N_SLIP = 0
N_STRIP = 0
N_TTY = 0
OCRNL = 0
OFDEL = 0
OFILL = 0
OLCUC = 0
ONLCR = 0
ONLRET = 0
ONOCR = 0
OPOST = 0
PARENB = 0
PARMRK = 0
PARODD = 0
PENDIN = 0
TAB0 = 0
TAB1 = 0
TAB2 = 0
TAB3 = 0
TABDLY = 0
TCFLSH = 0
TCGETA = 0
TCGETS = 0
TCIFLUSH = 0
TCIOFF = 0
TCIOFLUSH = 0
TCION = 0
TCOFLUSH = 0
TCOOFF = 0
TCOON = 0
TCSADRAIN = 0
TCSAFLUSH = 0
TCSANOW = 0
TCSBRK = 0
TCSBRKP = 0
TCSETA = 0
TCSETAF = 0
TCSETAW = 0
TCSETS = 0
TCSETSF = 0
TCSETSW = 0
TCXONC = 0
TIOCCONS = 0
TIOCEXCL = 0
TIOCGETD = 0
TIOCGICOUNT = 0
TIOCGLCKTRMIOS = 0
TIOCGPGRP = 0
TIOCGSERIAL = 0
TIOCGSOFTCAR = 0
TIOCGWINSZ = 0
TIOCINQ = 0
TIOCLINUX = 0
TIOCMBIC = 0
TIOCMBIS = 0
TIOCMGET = 0
TIOCMIWAIT = 0
TIOCMSET = 0
TIOCM_CAR = 0
TIOCM_CD = 0
TIOCM_CTS = 0
TIOCM_DSR = 0
TIOCM_DTR = 0
TIOCM_LE = 0
TIOCM_RI = 0
TIOCM_RNG = 0
TIOCM_RTS = 0
TIOCM_SR = 0
TIOCM_ST = 0
TIOCNOTTY = 0
TIOCNXCL = 0
TIOCOUTQ = 0
TIOCPKT = 0
TIOCPKT_DATA = 0
TIOCPKT_DOSTOP = 0
TIOCPKT_FLUSHREAD = 0
TIOCPKT_FLUSHWRITE = 0
TIOCPKT_NOSTOP = 0
TIOCPKT_START = 0
TIOCPKT_STOP = 0
TIOCSCTTY = 0
TIOCSERCONFIG = 0
TIOCSERGETLSR = 0
TIOCSERGETMULTI = 0
TIOCSERGSTRUCT = 0
TIOCSERGWILD = 0
TIOCSERSETMULTI = 0
TIOCSERSWILD = 0
TIOCSER_TEMT = 0
TIOCSETD = 0
TIOCSLCKTRMIOS = 0
TIOCSPGRP = 0
TIOCSSERIAL = 0
TIOCSSOFTCAR = 0
TIOCSTI = 0
TIOCSWINSZ = 0
TOSTOP = 0
VDISCARD = 0
VEOF = 0
VEOL = 0
VEOL2 = 0
VERASE = 0
VINTR = 0
VKILL = 0
VLNEXT = 0
VMIN = 0
VQUIT = 0
VREPRINT = 0
VSTART = 0
VSTOP = 0
VSUSP = 0
VSWTC = 0
VSWTCH = 0
VT0 = 0
VT1 = 0
VTDLY = 0
VTIME = 0
VWERASE = 0
XCASE = 0
XTABS = 0
_POSIX_VDISABLE = 0
