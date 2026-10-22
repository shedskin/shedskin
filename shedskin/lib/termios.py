# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

# constants a platform lacks are -1
TCSANOW = 1
TCSADRAIN = 1
TCSAFLUSH = 1
TCIFLUSH = 1
TCOFLUSH = 1
TCIOFLUSH = 1
TCOOFF = 1
TCOON = 1
TCIOFF = 1
TCION = 1
IGNBRK = 1
BRKINT = 1
IGNPAR = 1
PARMRK = 1
INPCK = 1
ISTRIP = 1
INLCR = 1
IGNCR = 1
ICRNL = 1
IUCLC = 1
IXON = 1
IXANY = 1
IXOFF = 1
IMAXBEL = 1
IUTF8 = 1
OPOST = 1
OLCUC = 1
ONLCR = 1
OCRNL = 1
ONOCR = 1
ONLRET = 1
OFILL = 1
OFDEL = 1
NLDLY = 1
CRDLY = 1
TABDLY = 1
BSDLY = 1
VTDLY = 1
FFDLY = 1
NL0 = 1
NL1 = 1
CR0 = 1
CR1 = 1
CR2 = 1
CR3 = 1
TAB0 = 1
TAB1 = 1
TAB2 = 1
TAB3 = 1
XTABS = 1
BS0 = 1
BS1 = 1
VT0 = 1
VT1 = 1
FF0 = 1
FF1 = 1
CSIZE = 1
CS5 = 1
CS6 = 1
CS7 = 1
CS8 = 1
CSTOPB = 1
CREAD = 1
PARENB = 1
PARODD = 1
HUPCL = 1
CLOCAL = 1
CRTSCTS = 1
CBAUD = 1
CIBAUD = 1
ISIG = 1
ICANON = 1
XCASE = 1
ECHO = 1
ECHOE = 1
ECHOK = 1
ECHONL = 1
ECHOCTL = 1
ECHOPRT = 1
ECHOKE = 1
FLUSHO = 1
NOFLSH = 1
TOSTOP = 1
PENDIN = 1
IEXTEN = 1
EXTPROC = 1
VINTR = 1
VQUIT = 1
VERASE = 1
VKILL = 1
VEOF = 1
VTIME = 1
VMIN = 1
VSWTC = 1
VSWTCH = 1
VSTART = 1
VSTOP = 1
VSUSP = 1
VEOL = 1
VREPRINT = 1
VDISCARD = 1
VWERASE = 1
VLNEXT = 1
VEOL2 = 1
NCCS = 1
B0 = 1
B50 = 1
B75 = 1
B110 = 1
B134 = 1
B150 = 1
B200 = 1
B300 = 1
B600 = 1
B1200 = 1
B1800 = 1
B2400 = 1
B4800 = 1
B9600 = 1
B19200 = 1
B38400 = 1
B57600 = 1
B115200 = 1
B230400 = 1
B460800 = 1
B500000 = 1
B576000 = 1
B921600 = 1
B1000000 = 1
B1152000 = 1
B1500000 = 1
B2000000 = 1
B2500000 = 1
B3000000 = 1
B3500000 = 1
B4000000 = 1

class error(Exception):
    pass

class TermAttributes:
    """what tcgetattr returns: like cpython's list [iflag, oflag, cflag,
    lflag, ispeed, ospeed, cc], but with the items of cc as ints"""

    def __init__(self):
        self.iflag = 1
        self.oflag = 1
        self.cflag = 1
        self.lflag = 1
        self.ispeed = 1
        self.ospeed = 1
        self.cc = [1]

    def __getitem__(self, i):
        return 1

    def __setitem__(self, i, value):
        pass

    def __len__(self):
        return 1

    def __eq__(self, other):
        return True

    def copy(self):
        return self

def tcgetattr(fd):
    return TermAttributes()

def tcsetattr(fd, when, attributes):
    pass

def tcsendbreak(fd, duration):
    pass

def tcdrain(fd):
    pass

def tcflush(fd, queue):
    pass

def tcflow(fd, action):
    pass

def tcgetwinsize(fd):
    return (1, 1)

def tcsetwinsize(fd, winsize):
    pass
