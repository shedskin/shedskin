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

class error(Exception): pass
class herror(Exception): pass
class gaierror(Exception): pass
class timeout(Exception): pass

class socket(object):
    def __init__(self, family=AF_INET, type=SOCK_STREAM, proto=0):
        pass

    def accept(self):
        return (socket(), ('', 1) )

    def fileno(self):
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
        return ''

    def send(self, string, flags=0):
        return 0

    def sendall(self, string, flags=0):
        pass

    def getsockname(self):
        return ('', 0)

    def getpeername(self):
        return ('', 0)

    def recvfrom(self, bufsize, flags=0):
        return ('', ('', 0))

    def sendto(self, bufsize, flags=0, address=0):
        return 0

def getfqdn(host):
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
