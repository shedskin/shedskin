# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)

# model for module socket for shed skin
# from python 2.5.1 documentation

SHUT_RD=0
SHUT_WR=1
SHUT_RDWR=2

SOL_IP=0
SOL_SOCKET=1

SO_REUSEADDR=2

AI_PASSIVE=1

AF_UNIX=1
AF_INET=2
AF_INET6=10

IP_TOS=1

SOCK_STREAM=1
SOCK_DGRAM=2

SOMAXCONN=128

INADDR_ANY=0
INADDR_BROADCAST=0xffffffff
INADDR_NONE=0xffffffff
INADDR_LOOPBACK=0x7f000001

# address families
AF_APPLETALK=5
AF_DECnet=12
AF_IPX=4
AF_SNA=22
AF_UNSPEC=0

# getaddrinfo() flags
AI_ADDRCONFIG=32
AI_ALL=16
AI_CANONNAME=2
AI_NUMERICHOST=4
AI_NUMERICSERV=1024
AI_V4MAPPED=8

# getaddrinfo() error codes
EAI_AGAIN=-3
EAI_BADFLAGS=-1
EAI_FAIL=-4
EAI_FAMILY=-6
EAI_MEMORY=-10
EAI_NODATA=-5
EAI_NONAME=-2
EAI_SERVICE=-8
EAI_SOCKTYPE=-7

# reserved port ranges
IPPORT_RESERVED=1024
IPPORT_USERRESERVED=5000

# multicast address constants
INADDR_ALLHOSTS_GROUP=0xe0000001
INADDR_MAX_LOCAL_GROUP=0xe00000ff
INADDR_UNSPEC_GROUP=0xe0000000

# IP protocols
IPPROTO_AH=51
IPPROTO_DSTOPTS=60
IPPROTO_EGP=8
IPPROTO_ESP=50
IPPROTO_FRAGMENT=44
IPPROTO_HOPOPTS=0
IPPROTO_ICMP=1
IPPROTO_ICMPV6=58
IPPROTO_IDP=22
IPPROTO_IGMP=2
IPPROTO_IP=0
IPPROTO_IPV6=41
IPPROTO_NONE=59
IPPROTO_PIM=103
IPPROTO_PUP=12
IPPROTO_RAW=255
IPPROTO_ROUTING=43
IPPROTO_SCTP=132
IPPROTO_TCP=6
IPPROTO_UDP=17

# IP socket options
IP_ADD_MEMBERSHIP=35
IP_ADD_SOURCE_MEMBERSHIP=39
IP_BLOCK_SOURCE=38
IP_DROP_MEMBERSHIP=36
IP_DROP_SOURCE_MEMBERSHIP=40
IP_HDRINCL=3
IP_MULTICAST_IF=32
IP_MULTICAST_LOOP=34
IP_MULTICAST_TTL=33
IP_OPTIONS=4
IP_PKTINFO=8
IP_RECVTOS=13
IP_RECVTTL=12
IP_TTL=2
IP_UNBLOCK_SOURCE=37

# IPv6 socket options
IPV6_CHECKSUM=7
IPV6_HOPLIMIT=52
IPV6_HOPOPTS=54
IPV6_JOIN_GROUP=20
IPV6_LEAVE_GROUP=21
IPV6_MULTICAST_HOPS=18
IPV6_MULTICAST_IF=17
IPV6_MULTICAST_LOOP=19
IPV6_PKTINFO=50
IPV6_RECVRTHDR=56
IPV6_RECVTCLASS=66
IPV6_RTHDR=57
IPV6_TCLASS=67
IPV6_UNICAST_HOPS=16
IPV6_V6ONLY=26

# send()/recv() flags
MSG_CTRUNC=8
MSG_DONTROUTE=4
MSG_OOB=1
MSG_PEEK=2
MSG_TRUNC=32
MSG_WAITALL=256

# getnameinfo() flags
NI_DGRAM=16
NI_MAXHOST=1025
NI_MAXSERV=32
NI_NAMEREQD=8
NI_NOFQDN=4
NI_NUMERICHOST=1
NI_NUMERICSERV=2

# socket types
SOCK_RAW=3
SOCK_RDM=4
SOCK_SEQPACKET=5

# socket option levels
SOL_TCP=6
SOL_UDP=17

# socket options
SO_ACCEPTCONN=30
SO_BROADCAST=6
SO_DEBUG=1
SO_DONTROUTE=5
SO_ERROR=4
SO_KEEPALIVE=9
SO_LINGER=13
SO_OOBINLINE=10
SO_RCVBUF=8
SO_RCVLOWAT=18
SO_RCVTIMEO=20
SO_SNDBUF=7
SO_SNDLOWAT=19
SO_SNDTIMEO=21
SO_TYPE=3

# TCP socket options
TCP_FASTOPEN=23
TCP_KEEPCNT=6
TCP_KEEPINTVL=5
TCP_MAXSEG=2
TCP_NODELAY=1

# errno values
EAGAIN=11
EBADF=9
EWOULDBLOCK=11

class error(Exception): pass
class herror(Exception): pass
class gaierror(Exception): pass
class timeout(Exception): pass

# NOTE literal defaults (AF_INET=2, SOCK_STREAM=1, the same on all supported
# platforms) so the compiler emits them directly instead of default_N globals
class socket(object):
    def __init__(self, family=2, type=1, proto=0):
        self.family = family
        self.type = type
        self.proto = proto

    def __repr__(self):
        return ''

    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def accept(self):
        return (socket(), ('', 1) )

    def fileno(self):
        return 0

    def detach(self):
        return 0

    def dup(self):
        return socket()

    # FIXME CPython default is count=None; a negative value means 'send
    # everything' instead (same convention as timeouts in this module)
    def sendfile(self, file, offset=0, count=-1):
        return 0

    def makefile(self, flags=None):
        return file('', flags)

    def listen(self, backlog):
        return self

    def shutdown(self, how):
        return self

    def close(self):
        return self

    # setblocking(0) == settimeout(0.0)
    # setblocking(1) == settimeout(None)
    def setblocking(self, flag):
        return self

    def getblocking(self):
        return True

    def settimeout(self, value):
        return self

    def gettimeout(self):
        return 0.0

    def setsockopt(self, level, optname, value):
        return self

    def getsockopt(self, level, optname, value=0):
        return ''

    def bind(self, address):
        return self

    def connect(self, address):
        return self

    def recv(self, bufsize, flags=0):
        return b''

    def send(self, string, flags=0):
        return 0

    def sendall(self, string, flags=0):
        pass

    def getsockname(self):
        return ('', 0)

    def getpeername(self):
        return ('', 0)

    def recvfrom(self, bufsize, flags=0):
        return (b'', ('', 0))

    def sendto(self, bufsize, flags=0, address=0):
        return 0

# FIXME CPython default is timeout=None; like settimeout()/setdefaulttimeout()
# elsewhere in this module, None isn't supported so a negative value means
# "no timeout given" instead.
def create_connection(address, timeout=-1, source_address=None):
    return socket()

def fromfd(fd, family, type, proto=0):
    return socket()

# FIXME CPython default is backlog=None; a negative value means 'use a
# reasonable default' instead (same convention as timeouts in this module)
def create_server(address, family=2, backlog=-1, reuse_port=False, dualstack_ipv6=False):
    return socket()

def has_dualstack_ipv6():
    return False

def socketpair(family=2, type=1, proto=0):
    return (socket(), socket())

def getfqdn(name):
    return ''

def gethostname():
    return ''

def gethostbyname(hostname):
    return ''

def ntohs(x):
    return 0

def htons(x):
    return 0

def ntohl(x):
    return 0

def htonl(x):
    return 0

def inet_aton(x):
    return ''

def inet_ntoa(x):
    return ''

def has_ipv6():
    return True

def getdefaulttimeout():
    return 0.0

def setdefaulttimeout(x):
    pass
