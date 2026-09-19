/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/*
 * Implementation of the Python 2.5.1 socket module for Shed Skin
 * by: Michael Elkins <me@cs.hmc.edu>
 * February 25, 2008
 *
 * Current Issues:
 * - unix domain sockets are not implemented
 * - can't call socket.settimeout(None)
 */

/* macOS only exposes the RFC 3542 IPv6 socket options (IPV6_HOPOPTS,
 * IPV6_RTHDR, IPV6_PKTINFO, ...) with this defined, as CPython does */
#ifdef __APPLE__
#define __APPLE_USE_RFC_3542 1
#endif

#include "socket.hpp"
#include <climits>
#include <fcntl.h>
#include <cerrno>

#ifndef WIN32
#include <unistd.h>
#include <net/if.h>
#endif

#ifdef WIN32
/* if_nametoindex()/if_indextoname()/GetAdaptersAddresses() */
#include <iphlpapi.h>
#ifdef _MSC_VER
#pragma comment(lib, "iphlpapi.lib")
#endif
#endif

#ifdef WIN32

#define CLOSE closesocket
#define EINPROGRESS WSAEINPROGRESS
#define SOCKOPT_CAST (char*)
typedef long tv_sec_type;
typedef long tv_usec_type;
typedef u_long in_addr_t;
typedef u_short sa_family_t;


#define ERRNO WSAGetLastError()

/* ws2def.h defines these as enum values rather than macros, so make the
 * #ifdef tests below see them (a self-referencing macro is harmless) */
#define IPPROTO_AH IPPROTO_AH
#define IPPROTO_DSTOPTS IPPROTO_DSTOPTS
#define IPPROTO_EGP IPPROTO_EGP
#define IPPROTO_ESP IPPROTO_ESP
#define IPPROTO_FRAGMENT IPPROTO_FRAGMENT
#define IPPROTO_HOPOPTS IPPROTO_HOPOPTS
#define IPPROTO_ICMP IPPROTO_ICMP
#define IPPROTO_ICMPV6 IPPROTO_ICMPV6
#define IPPROTO_IDP IPPROTO_IDP
#define IPPROTO_IGMP IPPROTO_IGMP
#define IPPROTO_IPV6 IPPROTO_IPV6
#define IPPROTO_NONE IPPROTO_NONE
#define IPPROTO_PIM IPPROTO_PIM
#define IPPROTO_PUP IPPROTO_PUP
#define IPPROTO_RAW IPPROTO_RAW
#define IPPROTO_ROUTING IPPROTO_ROUTING
#define IPPROTO_SCTP IPPROTO_SCTP
#define IPPROTO_TCP IPPROTO_TCP
#define IPPROTO_UDP IPPROTO_UDP

#else /* ! WIN32 */

#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/un.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <fcntl.h>
#define CLOSE close
#define SOCKET_ERROR -1
#define SOCKOPT_CAST
#define ERRNO errno
typedef time_t tv_sec_type;
typedef suseconds_t tv_usec_type;

#endif /* WIN32 */

#ifndef HOST_NAME_MAX
#define HOST_NAME_MAX 256
#endif

#ifdef WIN32
#define SS_INVALID_SOCKET INVALID_SOCKET
#else
#define SS_INVALID_SOCKET (-1)
#endif

#include <sstream>

namespace __socket__ {

str *__name__;

str *invalid_address;
str *timed_out;
str *host_not_found;

/**
  class error
  */

class_ *cl_error;

/**
  class herror
  */

class_ *cl_herror;

/**
  class gaierror
  */

class_ *cl_gaierror;

/**
  class timeout
  */

class_ *cl_timeout;

/**
  class socket
  */

class_ *cl_socket;

__ss_int __ss_AF_INET6 = AF_INET6;
__ss_int __ss_AF_INET = AF_INET;
__ss_int __ss_AF_UNIX = AF_UNIX;
__ss_int __ss_SOCK_STREAM = SOCK_STREAM;
__ss_int __ss_SOCK_DGRAM = SOCK_DGRAM;
#ifdef AI_PASSIVE
__ss_int __ss_AI_PASSIVE = AI_PASSIVE;
#endif
#ifdef SOL_IP
__ss_int __ss_SOL_IP = SOL_IP;
#else
__ss_int __ss_SOL_IP = 0; /* as CPython does */
#endif
#ifdef IP_TOS
__ss_int __ss_IP_TOS = IP_TOS;
#endif
__ss_int __ss_SOL_SOCKET = SOL_SOCKET;
__ss_int __ss_SO_REUSEADDR = SO_REUSEADDR;
__ss_int __ss_INADDR_ANY = INADDR_ANY;
__ss_int __ss_INADDR_LOOPBACK = INADDR_LOOPBACK;
#ifdef INADDR_NONE
__ss_int __ss_INADDR_NONE = (__ss_int)INADDR_NONE;
#else
__ss_int __ss_INADDR_NONE = (__ss_int)0xffffffff;
#endif
__ss_int __ss_INADDR_BROADCAST = (__ss_int)INADDR_BROADCAST;
__ss_int __ss_SOMAXCONN = SOMAXCONN;
/* CPython defines these itself, so no header lookup */
__ss_int __ss_SHUT_RD = 0;
__ss_int __ss_SHUT_WR = 1;
__ss_int __ss_SHUT_RDWR = 2;

/* address families */
#ifdef AF_APPLETALK
__ss_int __ss_AF_APPLETALK = AF_APPLETALK;
#endif
#ifdef AF_DECnet
__ss_int __ss_AF_DECnet = AF_DECnet;
#endif
#ifdef AF_IPX
__ss_int __ss_AF_IPX = AF_IPX;
#endif
#ifdef AF_SNA
__ss_int __ss_AF_SNA = AF_SNA;
#endif
#ifdef AF_UNSPEC
__ss_int __ss_AF_UNSPEC = AF_UNSPEC;
#endif

/* getaddrinfo() flags */
#ifdef AI_ADDRCONFIG
__ss_int __ss_AI_ADDRCONFIG = AI_ADDRCONFIG;
#endif
#ifdef AI_ALL
__ss_int __ss_AI_ALL = AI_ALL;
#endif
#ifdef AI_CANONNAME
__ss_int __ss_AI_CANONNAME = AI_CANONNAME;
#endif
#ifdef AI_NUMERICHOST
__ss_int __ss_AI_NUMERICHOST = AI_NUMERICHOST;
#endif
#ifdef AI_NUMERICSERV
__ss_int __ss_AI_NUMERICSERV = AI_NUMERICSERV;
#endif
#ifdef AI_V4MAPPED
__ss_int __ss_AI_V4MAPPED = AI_V4MAPPED;
#endif

/* getaddrinfo() error codes */
#ifdef EAI_AGAIN
__ss_int __ss_EAI_AGAIN = EAI_AGAIN;
#endif
#ifdef EAI_BADFLAGS
__ss_int __ss_EAI_BADFLAGS = EAI_BADFLAGS;
#endif
#ifdef EAI_FAIL
__ss_int __ss_EAI_FAIL = EAI_FAIL;
#endif
#ifdef EAI_FAMILY
__ss_int __ss_EAI_FAMILY = EAI_FAMILY;
#endif
#ifdef EAI_MEMORY
__ss_int __ss_EAI_MEMORY = EAI_MEMORY;
#endif
#ifdef EAI_NODATA
__ss_int __ss_EAI_NODATA = EAI_NODATA;
#endif
#ifdef EAI_NONAME
__ss_int __ss_EAI_NONAME = EAI_NONAME;
#endif
#ifdef EAI_SERVICE
__ss_int __ss_EAI_SERVICE = EAI_SERVICE;
#endif
#ifdef EAI_SOCKTYPE
__ss_int __ss_EAI_SOCKTYPE = EAI_SOCKTYPE;
#endif

/* reserved port ranges */
#ifdef IPPORT_RESERVED
__ss_int __ss_IPPORT_RESERVED = IPPORT_RESERVED;
#else
__ss_int __ss_IPPORT_RESERVED = 1024;
#endif
#ifdef IPPORT_USERRESERVED
__ss_int __ss_IPPORT_USERRESERVED = IPPORT_USERRESERVED;
#else
__ss_int __ss_IPPORT_USERRESERVED = 5000;
#endif

/* multicast address constants */
#ifdef INADDR_ALLHOSTS_GROUP
__ss_int __ss_INADDR_ALLHOSTS_GROUP = (__ss_int)INADDR_ALLHOSTS_GROUP;
#else
__ss_int __ss_INADDR_ALLHOSTS_GROUP = (__ss_int)0xe0000001;
#endif
#ifdef INADDR_MAX_LOCAL_GROUP
__ss_int __ss_INADDR_MAX_LOCAL_GROUP = (__ss_int)INADDR_MAX_LOCAL_GROUP;
#else
__ss_int __ss_INADDR_MAX_LOCAL_GROUP = (__ss_int)0xe00000ff;
#endif
#ifdef INADDR_UNSPEC_GROUP
__ss_int __ss_INADDR_UNSPEC_GROUP = (__ss_int)INADDR_UNSPEC_GROUP;
#else
__ss_int __ss_INADDR_UNSPEC_GROUP = (__ss_int)0xe0000000;
#endif

/* IP protocols */
#ifdef IPPROTO_AH
__ss_int __ss_IPPROTO_AH = IPPROTO_AH;
#endif
#ifdef IPPROTO_DSTOPTS
__ss_int __ss_IPPROTO_DSTOPTS = IPPROTO_DSTOPTS;
#endif
#ifdef IPPROTO_EGP
__ss_int __ss_IPPROTO_EGP = IPPROTO_EGP;
#endif
#ifdef IPPROTO_ESP
__ss_int __ss_IPPROTO_ESP = IPPROTO_ESP;
#endif
#ifdef IPPROTO_FRAGMENT
__ss_int __ss_IPPROTO_FRAGMENT = IPPROTO_FRAGMENT;
#endif
#ifdef IPPROTO_HOPOPTS
__ss_int __ss_IPPROTO_HOPOPTS = IPPROTO_HOPOPTS;
#endif
#ifdef IPPROTO_ICMP
__ss_int __ss_IPPROTO_ICMP = IPPROTO_ICMP;
#endif
#ifdef IPPROTO_ICMPV6
__ss_int __ss_IPPROTO_ICMPV6 = IPPROTO_ICMPV6;
#endif
#ifdef IPPROTO_IDP
__ss_int __ss_IPPROTO_IDP = IPPROTO_IDP;
#endif
#ifdef IPPROTO_IGMP
__ss_int __ss_IPPROTO_IGMP = IPPROTO_IGMP;
#endif
#ifdef IPPROTO_IP
__ss_int __ss_IPPROTO_IP = IPPROTO_IP;
#endif
#ifdef IPPROTO_IPV6
__ss_int __ss_IPPROTO_IPV6 = IPPROTO_IPV6;
#endif
#ifdef IPPROTO_NONE
__ss_int __ss_IPPROTO_NONE = IPPROTO_NONE;
#endif
#ifdef IPPROTO_PIM
__ss_int __ss_IPPROTO_PIM = IPPROTO_PIM;
#endif
#ifdef IPPROTO_PUP
__ss_int __ss_IPPROTO_PUP = IPPROTO_PUP;
#endif
#ifdef IPPROTO_RAW
__ss_int __ss_IPPROTO_RAW = IPPROTO_RAW;
#endif
#ifdef IPPROTO_ROUTING
__ss_int __ss_IPPROTO_ROUTING = IPPROTO_ROUTING;
#endif
#ifdef IPPROTO_SCTP
__ss_int __ss_IPPROTO_SCTP = IPPROTO_SCTP;
#endif
#ifdef IPPROTO_TCP
__ss_int __ss_IPPROTO_TCP = IPPROTO_TCP;
#endif
#ifdef IPPROTO_UDP
__ss_int __ss_IPPROTO_UDP = IPPROTO_UDP;
#endif

/* IP socket options */
#ifdef IP_ADD_MEMBERSHIP
__ss_int __ss_IP_ADD_MEMBERSHIP = IP_ADD_MEMBERSHIP;
#endif
#ifdef IP_ADD_SOURCE_MEMBERSHIP
__ss_int __ss_IP_ADD_SOURCE_MEMBERSHIP = IP_ADD_SOURCE_MEMBERSHIP;
#endif
#ifdef IP_BLOCK_SOURCE
__ss_int __ss_IP_BLOCK_SOURCE = IP_BLOCK_SOURCE;
#endif
#ifdef IP_DROP_MEMBERSHIP
__ss_int __ss_IP_DROP_MEMBERSHIP = IP_DROP_MEMBERSHIP;
#endif
#ifdef IP_DROP_SOURCE_MEMBERSHIP
__ss_int __ss_IP_DROP_SOURCE_MEMBERSHIP = IP_DROP_SOURCE_MEMBERSHIP;
#endif
#ifdef IP_HDRINCL
__ss_int __ss_IP_HDRINCL = IP_HDRINCL;
#endif
#ifdef IP_MULTICAST_IF
__ss_int __ss_IP_MULTICAST_IF = IP_MULTICAST_IF;
#endif
#ifdef IP_MULTICAST_LOOP
__ss_int __ss_IP_MULTICAST_LOOP = IP_MULTICAST_LOOP;
#endif
#ifdef IP_MULTICAST_TTL
__ss_int __ss_IP_MULTICAST_TTL = IP_MULTICAST_TTL;
#endif
#ifdef IP_OPTIONS
__ss_int __ss_IP_OPTIONS = IP_OPTIONS;
#endif
#ifdef IP_PKTINFO
__ss_int __ss_IP_PKTINFO = IP_PKTINFO;
#endif
#ifdef IP_RECVTOS
__ss_int __ss_IP_RECVTOS = IP_RECVTOS;
#endif
#ifdef IP_RECVTTL
__ss_int __ss_IP_RECVTTL = IP_RECVTTL;
#endif
#ifdef IP_TTL
__ss_int __ss_IP_TTL = IP_TTL;
#endif
#ifdef IP_UNBLOCK_SOURCE
__ss_int __ss_IP_UNBLOCK_SOURCE = IP_UNBLOCK_SOURCE;
#endif

/* IPv6 socket options */
#ifdef IPV6_CHECKSUM
__ss_int __ss_IPV6_CHECKSUM = IPV6_CHECKSUM;
#endif
#ifdef IPV6_HOPLIMIT
__ss_int __ss_IPV6_HOPLIMIT = IPV6_HOPLIMIT;
#endif
#ifdef IPV6_HOPOPTS
__ss_int __ss_IPV6_HOPOPTS = IPV6_HOPOPTS;
#endif
#ifdef IPV6_JOIN_GROUP
__ss_int __ss_IPV6_JOIN_GROUP = IPV6_JOIN_GROUP;
#endif
#ifdef IPV6_LEAVE_GROUP
__ss_int __ss_IPV6_LEAVE_GROUP = IPV6_LEAVE_GROUP;
#endif
#ifdef IPV6_MULTICAST_HOPS
__ss_int __ss_IPV6_MULTICAST_HOPS = IPV6_MULTICAST_HOPS;
#endif
#ifdef IPV6_MULTICAST_IF
__ss_int __ss_IPV6_MULTICAST_IF = IPV6_MULTICAST_IF;
#endif
#ifdef IPV6_MULTICAST_LOOP
__ss_int __ss_IPV6_MULTICAST_LOOP = IPV6_MULTICAST_LOOP;
#endif
#ifdef IPV6_PKTINFO
__ss_int __ss_IPV6_PKTINFO = IPV6_PKTINFO;
#endif
#ifdef IPV6_RECVRTHDR
__ss_int __ss_IPV6_RECVRTHDR = IPV6_RECVRTHDR;
#endif
#ifdef IPV6_RECVTCLASS
__ss_int __ss_IPV6_RECVTCLASS = IPV6_RECVTCLASS;
#endif
#ifdef IPV6_RTHDR
__ss_int __ss_IPV6_RTHDR = IPV6_RTHDR;
#endif
#ifdef IPV6_TCLASS
__ss_int __ss_IPV6_TCLASS = IPV6_TCLASS;
#endif
#ifdef IPV6_UNICAST_HOPS
__ss_int __ss_IPV6_UNICAST_HOPS = IPV6_UNICAST_HOPS;
#endif
#ifdef IPV6_V6ONLY
__ss_int __ss_IPV6_V6ONLY = IPV6_V6ONLY;
#endif

/* send()/recv() flags */
#ifdef MSG_CTRUNC
__ss_int __ss_MSG_CTRUNC = MSG_CTRUNC;
#endif
#ifdef MSG_DONTROUTE
__ss_int __ss_MSG_DONTROUTE = MSG_DONTROUTE;
#endif
#ifdef MSG_OOB
__ss_int __ss_MSG_OOB = MSG_OOB;
#endif
#ifdef MSG_PEEK
__ss_int __ss_MSG_PEEK = MSG_PEEK;
#endif
#ifdef MSG_TRUNC
__ss_int __ss_MSG_TRUNC = MSG_TRUNC;
#endif
#ifdef MSG_WAITALL
__ss_int __ss_MSG_WAITALL = MSG_WAITALL;
#endif

/* getnameinfo() flags */
#ifdef NI_DGRAM
__ss_int __ss_NI_DGRAM = NI_DGRAM;
#endif
#ifdef NI_MAXHOST
__ss_int __ss_NI_MAXHOST = NI_MAXHOST;
#endif
#ifdef NI_MAXSERV
__ss_int __ss_NI_MAXSERV = NI_MAXSERV;
#endif
#ifdef NI_NAMEREQD
__ss_int __ss_NI_NAMEREQD = NI_NAMEREQD;
#endif
#ifdef NI_NOFQDN
__ss_int __ss_NI_NOFQDN = NI_NOFQDN;
#endif
#ifdef NI_NUMERICHOST
__ss_int __ss_NI_NUMERICHOST = NI_NUMERICHOST;
#endif
#ifdef NI_NUMERICSERV
__ss_int __ss_NI_NUMERICSERV = NI_NUMERICSERV;
#endif

/* socket types */
#ifdef SOCK_RAW
__ss_int __ss_SOCK_RAW = SOCK_RAW;
#endif
#ifdef SOCK_RDM
__ss_int __ss_SOCK_RDM = SOCK_RDM;
#endif
#ifdef SOCK_SEQPACKET
__ss_int __ss_SOCK_SEQPACKET = SOCK_SEQPACKET;
#endif

/* socket option levels */
#ifdef SOL_TCP
__ss_int __ss_SOL_TCP = SOL_TCP;
#else
__ss_int __ss_SOL_TCP = 6;
#endif
#ifdef SOL_UDP
__ss_int __ss_SOL_UDP = SOL_UDP;
#else
__ss_int __ss_SOL_UDP = 17;
#endif

/* socket options */
#ifdef SO_ACCEPTCONN
__ss_int __ss_SO_ACCEPTCONN = SO_ACCEPTCONN;
#endif
#ifdef SO_BROADCAST
__ss_int __ss_SO_BROADCAST = SO_BROADCAST;
#endif
#ifdef SO_DEBUG
__ss_int __ss_SO_DEBUG = SO_DEBUG;
#endif
#ifdef SO_DONTROUTE
__ss_int __ss_SO_DONTROUTE = SO_DONTROUTE;
#endif
#ifdef SO_ERROR
__ss_int __ss_SO_ERROR = SO_ERROR;
#endif
#ifdef SO_KEEPALIVE
__ss_int __ss_SO_KEEPALIVE = SO_KEEPALIVE;
#endif
#ifdef SO_LINGER
__ss_int __ss_SO_LINGER = SO_LINGER;
#endif
#ifdef SO_OOBINLINE
__ss_int __ss_SO_OOBINLINE = SO_OOBINLINE;
#endif
#ifdef SO_RCVBUF
__ss_int __ss_SO_RCVBUF = SO_RCVBUF;
#endif
#ifdef SO_RCVLOWAT
__ss_int __ss_SO_RCVLOWAT = SO_RCVLOWAT;
#endif
#ifdef SO_RCVTIMEO
__ss_int __ss_SO_RCVTIMEO = SO_RCVTIMEO;
#endif
#ifdef SO_SNDBUF
__ss_int __ss_SO_SNDBUF = SO_SNDBUF;
#endif
#ifdef SO_SNDLOWAT
__ss_int __ss_SO_SNDLOWAT = SO_SNDLOWAT;
#endif
#ifdef SO_SNDTIMEO
__ss_int __ss_SO_SNDTIMEO = SO_SNDTIMEO;
#endif
#ifdef SO_TYPE
__ss_int __ss_SO_TYPE = SO_TYPE;
#endif

/* TCP socket options */
#ifdef TCP_FASTOPEN
__ss_int __ss_TCP_FASTOPEN = TCP_FASTOPEN;
#endif
#ifdef TCP_KEEPCNT
__ss_int __ss_TCP_KEEPCNT = TCP_KEEPCNT;
#endif
#ifdef TCP_KEEPINTVL
__ss_int __ss_TCP_KEEPINTVL = TCP_KEEPINTVL;
#endif
#ifdef TCP_MAXSEG
__ss_int __ss_TCP_MAXSEG = TCP_MAXSEG;
#endif
#ifdef TCP_NODELAY
__ss_int __ss_TCP_NODELAY = TCP_NODELAY;
#endif

/* errno values */
#ifdef EAGAIN
__ss_int __ss_EAGAIN = EAGAIN;
#else
__ss_int __ss_EAGAIN = 11;
#endif
#ifdef EBADF
__ss_int __ss_EBADF = EBADF;
#else
__ss_int __ss_EBADF = 9;
#endif
#ifdef WIN32
/* the MSVC CRT defines EWOULDBLOCK as 140, but CPython's errno module
 * replaces it with WSAEWOULDBLOCK (10035), which is what winsock actually
 * reports; so on windows EAGAIN (11) != EWOULDBLOCK, unlike on POSIX */
__ss_int __ss_EWOULDBLOCK = WSAEWOULDBLOCK;
#elif defined(EWOULDBLOCK)
__ss_int __ss_EWOULDBLOCK = EWOULDBLOCK;
#else
__ss_int __ss_EWOULDBLOCK = 11;
#endif

double __ss_default_timeout = -1.0;

__ss_int socket::__ss_fileno() {
    if (_fd == SS_INVALID_SOCKET)
        return -1;
    return (__ss_int)this->_fd;
}


#ifdef WIN32
//not exactly the correct definition, but we only use it with ostringstream
std::string strerror(int e)
{
    std::ostringstream os;
    os << "socket error " << e;
    return os.str();
}
#endif

/* socket.error carrying the errno of the failed call, like OSError.errno.
 * Pass the errno explicitly when other calls (e.g. restoring blocking mode,
 * which on Windows resets WSAGetLastError()) come between the failure and
 * the throw. */
static error *make_error(const char *prefix, int e)
{
    std::ostringstream os;
    os << prefix << ": " << strerror(e) << " (errno " << e << ")";
    error *err = new error(new str(os.str().c_str()));
    err->__ss_errno = e;
    err->strerror = new str(std::string(strerror(e)).c_str());
    return err;
}

static error *make_error(const char *prefix)
{
    return make_error(prefix, ERRNO);
}

static timeout *make_timeout()
{
    return new timeout(timed_out);
}

/* CPython makes every socket it creates non-inheritable (PEP 446) */
static void set_fd_inheritable(socket_type fd, bool inheritable)
{
#ifdef WIN32
    if (!SetHandleInformation((HANDLE)fd, HANDLE_FLAG_INHERIT, inheritable ? HANDLE_FLAG_INHERIT : 0))
        throw make_error("set_inheritable");
#else
    int flags = ::fcntl(fd, F_GETFD);
    if (flags == -1)
        throw make_error("set_inheritable");
    flags = inheritable ? (flags & ~FD_CLOEXEC) : (flags | FD_CLOEXEC);
    if (::fcntl(fd, F_SETFD, flags) == -1)
        throw make_error("set_inheritable");
#endif
}

static bool get_fd_inheritable(socket_type fd)
{
#ifdef WIN32
    DWORD flags;
    if (!GetHandleInformation((HANDLE)fd, &flags))
        throw make_error("get_inheritable");
    return (flags & HANDLE_FLAG_INHERIT) != 0;
#else
    int flags = ::fcntl(fd, F_GETFD);
    if (flags == -1)
        throw make_error("get_inheritable");
    return (flags & FD_CLOEXEC) == 0;
#endif
}

static socket_type dup_socket_fd(socket_type fd)
{
#ifdef WIN32
    /* SOCKETs are not CRT file descriptors, so dup() does not apply;
     * duplicate the underlying socket the way CPython does. */
    WSAPROTOCOL_INFOW info;
    if (WSADuplicateSocketW(fd, GetCurrentProcessId(), &info) == SOCKET_ERROR)
        throw make_error("dup");
    socket_type r = WSASocketW(FROM_PROTOCOL_INFO, FROM_PROTOCOL_INFO, FROM_PROTOCOL_INFO, &info, 0, WSA_FLAG_OVERLAPPED);
    if (r == INVALID_SOCKET)
        throw make_error("dup");
#else
    int r = ::dup(fd);
    if (r == SOCKET_ERROR)
        throw make_error("dup");
#endif
    set_fd_inheritable(r, false);
    return r;
}

socket::socket(socket::wrap_fd_tag, socket_type fd, __ss_int family_, __ss_int type_, __ss_int proto_) {
    this->__class__ = cl_socket;
    this->family = family_;
    this->type = type_;
    this->proto = proto_;
    _fd = fd;
    apply_timeout(__ss_default_timeout);
}

str *socket::__repr__() {
    std::ostringstream os;
    if (_fd == SS_INVALID_SOCKET)
        os << "<socket.socket fd=-1";
    else
        os << "<socket.socket fd=" << _fd;
    os << ", family=" << family << ", type=" << type << ", proto=" << proto << ">";
    return new str(os.str().c_str());
}

void socket::__enter__() { }

void socket::__exit__() {
    close();
}

__ss_int socket::detach() {
    socket_type fd = _fd;
    _fd = SS_INVALID_SOCKET;
    return (__ss_int)fd;
}

socket *socket::dup() {
    socket *sock = new socket(wrap_fd_tag(), dup_socket_fd(_fd), family, type, proto);
    sock->apply_timeout(_timeout);
    return sock;
}

__ss_int socket::sendfile(file_binary *f, __ss_int offset, __ss_int count) {
    /* portable fallback implementation (chunked read/send loop), like
     * CPython uses on platforms without os.sendfile() */
    if (offset)
        f->seek(offset, 0);
    size_t total = 0;
    for (;;) {
        __ss_int toread = 8192;
        if (count >= 0) {
            __ss_int remaining = count - (__ss_int)total;
            if (remaining <= 0)
                break;
            if (toread > remaining)
                toread = remaining;
        }
        bytes *b = f->read(toread);
        size_t len = b->unit.size();
        if (len == 0)
            break;
        const char *s = b->unit.data();
        size_t off = 0;
        while (off < len)
            off += send(s + off, len - off, 0);
        total += len;
    }
    return (__ss_int)total;
}


__ss_int socket::getsockopt(__ss_int level, __ss_int optname) {
    int v = 0;
    socklen_t buflen = sizeof(v);
    if (::getsockopt(_fd, (int)level, (int)optname, SOCKOPT_CAST &v, &buflen) == SOCKET_ERROR)
        throw make_error("getsockopt");
    return (__ss_int)v;
}

__ss_int socket::connect_ex(socket::inet_address address) {
    try {
        connect(address);
    } catch (error *e) {
        return (__ss_int)e->__ss_errno;
    } catch (timeout *) {
        return __ss_EWOULDBLOCK;
    }
    return 0;
}

__ss_bool socket::get_inheritable() {
    return __mbool(get_fd_inheritable(_fd));
}

void *socket::set_inheritable(__ss_bool inheritable) {
    set_fd_inheritable(_fd, inheritable);
    return NULL;
}

file *socket::makefile(str *mode) {
    if(!mode)
        mode = new str("r");

#ifdef WIN32
	intptr_t fd;
#else
	int fd;
#endif
	FILE *fp;

#ifdef WIN32
	if (((fd = _open_osfhandle(_fd, O_BINARY)) < 0) ||
	    ((fd = ::dup(fd)) < 0) || ((fp = fdopen(fd, mode->c_str())) == NULL))
#else
	if ((fd = ::dup(_fd)) < 0 || (fp = fdopen(fd, mode->c_str())) == NULL)
#endif
	{
		/*if (fd >= 0)
			SOCKETCLOSE(fd);
		return s->errorhandler(); */
        throw make_error("makefile");
	}
    file *f = new file(fp);
    f->name = new str("<socket>");
    f->mode = mode;
    return f;
}

socket *socket::bind(const sockaddr *sa, socklen_t salen)
{
    if (::bind(_fd, sa, salen) == SOCKET_ERROR) {
        throw make_error("bind");
    }
    return this;
}

// python supports two special strings
static unsigned long int string_to_addr(const char *s)
{
    if (!*s)
        return INADDR_ANY;
    if (strcmp(s, "<broadcast>") == 0)
        return INADDR_BROADCAST;
#ifdef WIN32
    /* winsock doesn't have inet_aton() so we are forced to use inet_addr().
     * however, since python has the special form <broadcast> we can use
     * -1 as the error check here.
     */
    unsigned long int addr = inet_addr(s);
    if (addr != (unsigned long int)-1)
        return addr;
#else
    struct in_addr addr;
    if (::inet_aton(s, &addr))
        return addr.s_addr; // ip address
#endif
    /* try looking up the address in dns */
    struct hostent *he = ::gethostbyname(s);
    if (!he)
        throw new gaierror(host_not_found); /* CPython resolves via getaddrinfo() */
    return * reinterpret_cast<unsigned long *>( he->h_addr_list[0] );
}

// conver the python version of a address to the bsd socket variety
static void tuple_to_sin_addr(sockaddr_in *dst, socket::inet_address src)
{
    memset(dst, 0, sizeof(sockaddr_in));
    dst->sin_family = AF_INET;
    const char *host = src->first->c_str();
    dst->sin_addr.s_addr = (in_addr_t)string_to_addr(host);
    dst->sin_port = htons((uint16_t)src->second);
}

socket *socket::bind(socket::inet_address address)
{
    if (family != AF_INET)
        throw new ValueError(invalid_address);

    sockaddr_in sin;
    tuple_to_sin_addr(&sin, address);
    return bind(reinterpret_cast<sockaddr *>(&sin), sizeof(sin));
}

socket *socket::setsockopt(__ss_int level, __ss_int optname, __ss_int value) {
    /* pass a plain int, as CPython does: __ss_int is 64-bit by default, and
     * some option handlers (winsock TCP_*, big-endian kernels) do not accept
     * or misread a wider buffer */
    int v = (int)value;
    if (::setsockopt(_fd, (int)level, (int)optname, SOCKOPT_CAST &v, sizeof(v)) == SOCKET_ERROR)
        throw make_error("setsockopt");

    return this;
}

socket *socket::connect(socket::inet_address address) {
    if (family != AF_INET)
        throw new ValueError(invalid_address);
    const char *host = address->first->c_str();
    int port = (int)address->second;

    sockaddr_in sin;
    memset(&sin, 0, sizeof(sin));
    sin.sin_family = (sa_family_t)family;
    sin.sin_port = htons((uint16_t)port);
    sin.sin_addr.s_addr = (in_addr_t)string_to_addr(host);

    return connect(reinterpret_cast<sockaddr *>(&sin), sizeof(sin));
}

#ifndef WIN32
socket *socket::connect(pyseq<str *> *address)
{
    if (family != AF_UNIX)
        throw new ValueError(invalid_address);
    sockaddr_un smup;
    smup.sun_family = AF_UNIX;
    const str* __0 = address->__getitem__(0);
    if(__0->unit.size() >= sizeof(smup.sun_path))
        throw new error(new str("AF_UNIX path too long"));
    strcpy(smup.sun_path, __0->c_str());

    return connect(reinterpret_cast<sockaddr *>(&smup), sizeof(smup));
}
#endif /* ! WIN32 */


static void set_blocking(socket_type fd)
{
#ifdef WIN32
    u_long flag = 0;
    if (ioctlsocket(fd, FIONBIO, &flag) == SOCKET_ERROR)
#else
        //FIXME should probably only clear the O_NONBLOCKING flag
        if (::fcntl(fd, F_SETFL, 0) == SOCKET_ERROR)
#endif
        {
            throw make_error("fcntl");
        }
}

static void set_nonblocking(socket_type fd)
{
#ifdef WIN32
    u_long flag = 1;
    if (ioctlsocket(fd, FIONBIO, &flag) == SOCKET_ERROR)
#else
        if (::fcntl(fd, F_SETFL, O_NONBLOCK) == SOCKET_ERROR)
#endif
        {
            throw make_error("fcntl");
        }
}
socket *socket::connect(const sockaddr *sa, socklen_t salen)
{
    if (_blocking && _timeout > 0) {
        // temporarily set the socket to nonblocking
        set_nonblocking(_fd);
    }

    if (::connect(_fd, sa, salen) == SOCKET_ERROR) {
        /* read the error before anything else: on Windows a successful call
         * such as ioctlsocket() resets WSAGetLastError() to 0 */
        int e = ERRNO;
        bool in_progress = (e == EINPROGRESS);
#ifdef WIN32
        /* winsock reports a non-blocking connect in progress as WSAEWOULDBLOCK */
        in_progress = in_progress || (e == WSAEWOULDBLOCK);
#endif
	if (!in_progress) {
	    error *err = make_error("connect", e);
	    if (_blocking && _timeout > 0)
		set_blocking(_fd); // turn blocking back on
	    throw err;
	}
    }

    if (_blocking && _timeout > 0) {
        fd_set s;
        FD_ZERO(&s);
        FD_SET(_fd, &s);
#ifdef WIN32
        /* winsock signals a failed non-blocking connect through the
         * exceptfds set rather than by marking the socket writable (as
         * CPython's internal_select() also allows for) */
        fd_set x;
        FD_ZERO(&x);
        FD_SET(_fd, &x);
        fd_set *exceptfds = &x;
#else
        fd_set *exceptfds = 0;
#endif

        timeval to;
        to.tv_sec = static_cast<tv_sec_type>(_timeout);
        to.tv_usec = static_cast<tv_usec_type>(1000000 * (_timeout - (double)to.tv_sec));

        if (::select(_fd+1, 0, &s, exceptfds, &to) == SOCKET_ERROR) {
            error *err = make_error("select");
	    set_blocking(_fd); // turn blocking back on
            throw err;
	}
        bool ready = FD_ISSET(_fd, &s);
#ifdef WIN32
        ready = ready || FD_ISSET(_fd, &x);
#endif
        if (!ready) {
	    set_blocking(_fd); // turn blocking back on
	    throw make_timeout();
	}

        // get connection status
        int err = 0;
        socklen_t errsize = sizeof(err);
        if (::getsockopt(_fd, SOL_SOCKET, SO_ERROR, SOCKOPT_CAST &err, &errsize) == SOCKET_ERROR) {
            error *e2 = make_error("getsockopt");
	    set_blocking(_fd); // turn blocking back on
            throw e2;
	}

        set_blocking(_fd); // turn blocking back on

        if (err != 0)
            throw make_error("connect", err);
    }

    return this;
}

/* Put the socket in the mode a timeout value means in CPython: 0.0 is
 * non-blocking, a positive value is blocking with a timeout, and a negative
 * value (None) is blocking without one. Always sets the fd's blocking flag
 * explicitly, as BSD/macOS accept()ed sockets inherit O_NONBLOCK. */
void socket::apply_timeout(double val)
{
    if (val == 0) {
        set_nonblocking(_fd);
        _blocking = false;
        _timeout = 0;
    } else {
        set_blocking(_fd);
        _blocking = true;
        _timeout = val < 0 ? -1 : val;
    }
}

socket *socket::setblocking(__ss_int flag)
{
    /* setblocking(True) is settimeout(None), setblocking(False) is settimeout(0.0) */
    apply_timeout(flag ? -1 : 0);
    return this;
}

socket *socket::settimeout(double val)
{
    if (val < 0)
	throw new ValueError(new str("Timeout value out of range"));
    apply_timeout(val);
    return this;
}

socket *socket::shutdown(__ss_int how)
{
    if (::shutdown(_fd, (int)how) == SOCKET_ERROR)
        throw make_error("shutdown");
    return this;
}

void socket::write_wait()
{
    if (_blocking && _timeout > 0) {
        fd_set s;
        FD_ZERO(&s);
        FD_SET(_fd, &s);
        timeval to;
        to.tv_sec = static_cast<tv_sec_type>(_timeout);
        to.tv_usec = static_cast<tv_usec_type>(1000000 * (_timeout - (double)to.tv_sec));
        if (::select(_fd+1, 0, &s, 0, &to) == SOCKET_ERROR)
            throw make_error("select");
        if (! FD_ISSET(_fd, &s))
            throw make_timeout();
    }
}

size_t socket::send(const char *s, size_t len, int flags)
{
    write_wait();

    ssize_t r = ::send(_fd, s, len, flags);
    if (r == SOCKET_ERROR)
        throw make_error("send");
    return (size_t)r;
}

__ss_int socket::send(bytes *string, __ss_int flags) {
    return (__ss_int)send( string->unit.data(), string->unit.size(), (int)flags );
}

__ss_int socket::sendall(bytes *string, __ss_int flags) {
    const char *s = string->c_str();
    size_t offset = 0;
    size_t len = string->unit.size(); //FIXME is this guaranteed to be the same as the C string length, even if we are dealing with wide/unicode?

    while (offset < len)
        offset += send(s + offset, len - offset, (int)flags);
    return (__ss_int)len;
}

__ss_int socket::sendto(bytes* msg, __ss_int flags, socket::inet_address addr)
{
    write_wait();

    const char *buf = msg->unit.data();
    size_t buflen = msg->unit.size();

    sockaddr *sa;
    socklen_t salen;

    //FIXME hardcoded for AF_INET
    sockaddr_in sin;
    sa = reinterpret_cast<sockaddr *>(&sin);
    salen = sizeof(sin);

    tuple_to_sin_addr(&sin, addr);

    ssize_t len = ::sendto(_fd, buf, buflen, (int)flags, sa, salen);
    if (len == SOCKET_ERROR)
        throw make_error("sendto");

    return (__ss_int)len;
}

__ss_int socket::sendto(bytes* msg, socket::inet_address addr)
{
    return sendto(msg, 0, addr);
}

socket *socket::close()
{
    if (_fd != SS_INVALID_SOCKET) {
        socket_type fd = _fd;
        _fd = SS_INVALID_SOCKET;
        if (::CLOSE(fd) == SOCKET_ERROR)
#define STRINGIFY(x) #x
            throw make_error(STRINGIFY(CLOSE));
#undef STRINGIFY
    }
    return this;
}

void socket::read_wait()
{
    if (_blocking && _timeout > 0) {
        fd_set s;
        FD_ZERO(&s);
        FD_SET(_fd, &s);
        timeval to;
        to.tv_sec = static_cast<tv_sec_type>(_timeout);
        to.tv_usec = static_cast<tv_usec_type>(1000000 * (_timeout - (double)to.tv_sec));
        if (::select(_fd+1, &s, 0, 0, &to) == SOCKET_ERROR)
            throw make_error("select");
        if (! FD_ISSET(_fd, &s))
            throw make_timeout();
    }
}

bytes *socket::recv(__ss_int bufsize, __ss_int flags)
{
    read_wait();

    std::vector<char> buf((size_t)bufsize);
    ssize_t len = ::recv(_fd, buf.data(), (size_t)bufsize, (int)flags);
    if (len == SOCKET_ERROR)
        throw make_error("recv");
    return new bytes(buf.data(), (size_t)len);
}

/* dotted-quad string for an IPv4 address (winsock wants a non-const void *) */
static str *in_addr_to_str(const in_addr *addr)
{
    char ip[INET_ADDRSTRLEN];
    if (!::inet_ntop(AF_INET, (void *)addr, ip, sizeof(ip)))
        throw make_error("inet_ntop");
    return new str(ip);
}

static socket::inet_address sin_addr_to_tuple(const sockaddr_in *sin)
{
    return new tuple2<str *, __ss_int>(2, in_addr_to_str(&sin->sin_addr), static_cast<__ss_int>(ntohs(sin->sin_port)));
}

size_t socket::recvfrom(char *buf, size_t bufsize, int flags, sockaddr *sa, socklen_t *salen)
{
    read_wait();
    ssize_t len = ::recvfrom(_fd, buf, bufsize, flags, sa, salen);
    if (len == SOCKET_ERROR)
        throw make_error("recvfrom");
    return (size_t)len;
}

tuple2<bytes *, socket::inet_address> *socket::recvfrom(__ss_int bufsize, __ss_int flags)
{
    std::vector<char> buf((size_t)bufsize);
    struct sockaddr_in sin;
    socklen_t salen = sizeof(sin);
    size_t len = recvfrom(buf.data(), (size_t)bufsize, (int)flags, reinterpret_cast<sockaddr *>(&sin), &salen);
    return new tuple2<bytes *, inet_address>(2, new bytes(buf.data(), len), sin_addr_to_tuple(&sin));
}

socket::socket(__ss_int family_, __ss_int type_, __ss_int proto_, __ss_int fileno) {
    this->__class__ = cl_socket;
    _timeout = __ss_default_timeout;
    _blocking = true;

    if (fileno >= 0) {
        /* wrap an existing fd; like CPython, detect what wasn't given */
        _fd = (socket_type)fileno;
#ifdef WIN32
        /* getsockname() fails with WSAEINVAL on an unbound socket on
         * Windows, so (like CPython) ask winsock for the protocol info
         * instead, which also gives us the type and protocol */
        if (family_ < 0 || type_ < 0 || proto_ < 0) {
            WSAPROTOCOL_INFOW info;
            socklen_t len = sizeof(info);
            if (::getsockopt(_fd, SOL_SOCKET, SO_PROTOCOL_INFOW, SOCKOPT_CAST &info, &len) == SOCKET_ERROR)
                throw make_error("socket");
            if (family_ < 0)
                family_ = info.iAddressFamily;
            if (type_ < 0)
                type_ = info.iSocketType;
            if (proto_ < 0)
                proto_ = info.iProtocol;
        }
#else
        if (family_ < 0) {
            sockaddr_storage ss;
            socklen_t len = sizeof(ss);
            memset(&ss, 0, sizeof(ss));
            if (::getsockname(_fd, reinterpret_cast<sockaddr *>(&ss), &len) == SOCKET_ERROR)
                throw make_error("socket");
            family_ = ss.ss_family;
        }
        if (type_ < 0) {
            int v = 0;
            socklen_t len = sizeof(v);
            if (::getsockopt(_fd, SOL_SOCKET, SO_TYPE, SOCKOPT_CAST &v, &len) == SOCKET_ERROR)
                throw make_error("socket");
            type_ = v;
        }
        if (proto_ < 0) {
            proto_ = 0;
#ifdef SO_PROTOCOL
            int v = 0;
            socklen_t len = sizeof(v);
            if (::getsockopt(_fd, SOL_SOCKET, SO_PROTOCOL, SOCKOPT_CAST &v, &len) != SOCKET_ERROR)
                proto_ = v;
#endif
        }
#endif /* WIN32 */
    } else {
        if (family_ < 0)
            family_ = AF_INET;
        if (type_ < 0)
            type_ = SOCK_STREAM;
        if (proto_ < 0)
            proto_ = 0;
        _fd = ::socket((int)family_, (int)type_, (int)proto_);
        if (_fd == SS_INVALID_SOCKET)
            throw make_error("socket");
        set_fd_inheritable(_fd, false);
    }
    this->family = family_;
    this->type = type_;
    this->proto = proto_;
    apply_timeout(__ss_default_timeout);
}

socket::~socket()
{
    if (_fd != SS_INVALID_SOCKET)
        ::CLOSE(_fd); // ignore error since we can't throw
}

socket *socket::listen(__ss_int backlog)
{
    if(::listen(_fd, (int)backlog) == SOCKET_ERROR)
        throw make_error("listen");
    return this;
}

socket* socket::accept(sockaddr *sa, socklen_t *salen)
{
    if (_blocking && _timeout > 0) {
        fd_set s;
        FD_ZERO(&s);
        FD_SET(_fd, &s);
        timeval to;
        to.tv_sec = static_cast<tv_sec_type>(_timeout);
        to.tv_usec = static_cast<tv_usec_type>(1000000 * (_timeout - (double)to.tv_sec));
        if (::select(_fd+1, &s, 0, 0, &to) == SOCKET_ERROR)
            throw make_error("select");
        if (! FD_ISSET(_fd, &s))
            throw make_timeout();
    }
    socket_type r = ::accept(_fd, sa, salen);
    if (r == SS_INVALID_SOCKET)
        throw make_error("accept");
    set_fd_inheritable(r, false);
    return new socket(wrap_fd_tag(), r, family, type, proto);
}

#if 0
// UNIX sockets
tuple2<socket *, pyseq<str *> *> *socket::accept()
{
    sockaddr_un smup;
    socklen_t sunsize = sizeof(smup);

    socket *sock = accept(reinterpret_cast<sockaddr *>(&smup), &sunsize);
    str* addr = new str(smup.sun_path);
    return new tuple2<socket *, pyseq<str *> *>(2, sock, addr);
}
#endif

// INET sockets
tuple2<socket *, socket::inet_address> *socket::accept() {
    sockaddr_in sin;
    socklen_t sinsize = sizeof(sin);
    socket *sock = accept(reinterpret_cast<sockaddr *>(&sin), &sinsize);
    return new tuple2<socket *, inet_address>( 2, sock, sin_addr_to_tuple(&sin));
}

#ifndef WIN32
socket *socket::bind(pyseq<str *> *address)
{
    if (family != AF_UNIX)
        throw new ValueError(invalid_address);
    sockaddr_un smup;
    smup.sun_family = AF_UNIX;
    const str* __0 = address->__getitem__(0);
    if(__0->unit.size() >= sizeof(smup.sun_path))
        throw new error(new str("AF_UNIX path too long"));
    strcpy(smup.sun_path, __0->c_str());

    return bind(reinterpret_cast<sockaddr *>(&smup), sizeof(smup));
}
#endif /* ! WIN32 */

socket::inet_address socket::getpeername()
{
    struct sockaddr_in addr;
    socklen_t addrlen = sizeof(addr);
    if (::getpeername(_fd, reinterpret_cast<sockaddr *>(&addr), &addrlen) == SOCKET_ERROR)
        throw make_error("getpeername");
    return sin_addr_to_tuple(&addr);
}

socket::inet_address socket::getsockname()
{
    struct sockaddr_in addr;
    socklen_t addrlen = sizeof(addr);
    if (::getsockname(_fd, reinterpret_cast<sockaddr *>(&addr), &addrlen) == SOCKET_ERROR)
        throw make_error("getsockname");
    return sin_addr_to_tuple(&addr);
}

str *gethostname()
{
    char name[HOST_NAME_MAX];
    if (::gethostname(name, sizeof(name)) == -1)
        throw make_error("gethostname");
    return new str(name);
}

socket *create_connection(socket::inet_address address, double timeout, socket::inet_address source_address, __ss_bool all_errors)
{
    /* only one address is ever tried here, so all_errors makes no difference */
    (void)all_errors;
    socket *s = new socket(__ss_AF_INET, __ss_SOCK_STREAM, 0);
    if (timeout >= 0)
        s->settimeout(timeout);
    if (source_address)
        s->bind(source_address);
    s->connect(address);
    return s;
}

socket *fromfd(__ss_int fd, __ss_int family, __ss_int type, __ss_int proto)
{
    return new socket(socket::wrap_fd_tag(), dup_socket_fd((socket_type)fd), family, type, proto);
}

socket *create_server(socket::inet_address address, __ss_int family, __ss_int backlog, __ss_bool reuse_port, __ss_bool dualstack_ipv6)
{
    if (dualstack_ipv6)
        throw new ValueError(new str("dualstack_ipv6 not supported"));
    socket *s = new socket(family, __ss_SOCK_STREAM, 0);
#ifdef WIN32
    /* SO_REUSEADDR has different (unsafe) semantics on Windows; do what
     * CPython does and set SO_EXCLUSIVEADDRUSE instead. */
    s->setsockopt(SOL_SOCKET, SO_EXCLUSIVEADDRUSE, 1);
#else
    s->setsockopt(SOL_SOCKET, SO_REUSEADDR, 1);
#endif
    if (reuse_port) {
#ifdef SO_REUSEPORT
        s->setsockopt(SOL_SOCKET, SO_REUSEPORT, 1);
#else
        throw new ValueError(new str("SO_REUSEPORT not supported on this platform"));
#endif
    }
    s->bind(address);
    s->listen(backlog >= 0 ? backlog : __ss_SOMAXCONN);
    return s;
}

__ss_bool has_dualstack_ipv6()
{
    /* requires IPv6 sockaddr support, which this module does not have yet */
    return False;
}

tuple2<socket *, socket *> *socketpair(__ss_int family, __ss_int type, __ss_int proto)
{
    /* Emulated on every platform the way CPython does it on Windows (no
     * AF_UNIX support here either): a connected TCP loopback pair. */
    if (family != __ss_AF_INET)
        throw new ValueError(new str("Only AF_INET socket address family is supported"));
    if (type != __ss_SOCK_STREAM)
        throw new ValueError(new str("Only SOCK_STREAM socket type is supported"));
    if (proto != 0)
        throw new ValueError(new str("Only protocol zero is supported"));

    socket *lsock = new socket(family, type, proto);
    socket *csock = 0, *ssock = 0;
    try {
        /* the handshake is done in blocking mode whatever the default
         * timeout is; the pair returned gets the default timeout like any
         * newly created socket */
        lsock->setblocking(1);
        lsock->bind(new tuple2<str *, __ss_int>(2, new str("127.0.0.1"), 0));
        lsock->listen(1);
        csock = new socket(family, type, proto);
        csock->setblocking(1);
        /* a blocking connect to a local listening socket completes without
         * anyone calling accept() yet, so no non-blocking dance is needed */
        csock->connect(lsock->getsockname());
        ssock = lsock->accept()->__getfirst__();
    } catch (...) {
        if (csock)
            csock->close();
        lsock->close();
        throw;
    }
    lsock->close();
    csock->apply_timeout(__ss_default_timeout);
    return new tuple2<socket *, socket *>(2, ssock, csock);
}

__ss_int __ss_htonl(__ss_int x) {
    return (__ss_int)htonl((uint32_t)x);
}

__ss_int __ss_htons(__ss_int x) {
    return (__ss_int)htons((uint16_t)x);
}

__ss_int __ss_ntohl(__ss_int x) {
    return (__ss_int)ntohl((uint32_t)x);
}

__ss_int __ss_ntohs(__ss_int x) {
    return (__ss_int)ntohs((uint16_t)x);
}

//FIXME this should return None when no timeout is set
double getdefaulttimeout()
{
    if (__ss_default_timeout < 0)
        throw new error(new str("no timeout is set"));
    return __ss_default_timeout;
}

// FIXME this should allow the argument to be None
void *setdefaulttimeout(double x)
{
    if (x < 0)
        throw new ValueError(new str("Timeout value out of range"));
    __ss_default_timeout = x;
    return NULL;
}

void __init()
{
    __name__ = new str("socket");

    cl_socket = new class_("socket");
    cl_herror = new class_("herror");
    cl_gaierror = new class_("gaierror");
    cl_timeout = new class_("timeout");
    cl_error = new class_("error");

    // string constants used by this module
    invalid_address = new str("invalid address");
    timed_out = new str("timed out");
    host_not_found = new str("host not found");

#ifdef WIN32
    int iResult;
    WSADATA wsaData;

    // Initialize Winsock
    iResult = WSAStartup(MAKEWORD(2,2), &wsaData);
    if (iResult != 0) {
        throw new error(new str("WSAStartup failed"));
    }
#endif /* WIN32 */
}

void __exit()
{
#ifdef WIN32
    //FIXME
    // should call winsock finalization routine, but __exit() doesn't get called
    // except for the builtin module
#endif
}

/* (hostname, aliaslist, ipaddrlist) from a hostent, as gethostby*() return */
static __host_tuple *hostent_to_tuple(const hostent *he)
{
    list<str *> *aliases = new list<str *>();
    for (char **a = he->h_aliases; a && *a; a++)
        aliases->append(new str(*a));
    list<str *> *addrs = new list<str *>();
    if (he->h_addrtype == AF_INET)
        for (char **a = he->h_addr_list; a && *a; a++)
            addrs->append(in_addr_to_str(reinterpret_cast<const in_addr *>(*a)));
    return new __host_tuple(3, new str(he->h_name), aliases, addrs);
}

str *gethostbyname(str *hostname)
{
    hostent *he = ::gethostbyname(hostname->c_str());
    if (!he)
        throw new gaierror(host_not_found); /* CPython resolves via getaddrinfo() */
    return in_addr_to_str(reinterpret_cast<const in_addr *>(he->h_addr_list[0]));
}

__host_tuple *gethostbyname_ex(str *hostname)
{
    hostent *he = ::gethostbyname(hostname->c_str());
    if (!he)
        throw new gaierror(host_not_found); /* CPython resolves via getaddrinfo() */
    return hostent_to_tuple(he);
}

__host_tuple *gethostbyaddr(str *ip_address)
{
    /* like CPython, a hostname is resolved first */
    in_addr addr;
    addr.s_addr = (in_addr_t)string_to_addr(ip_address->c_str());
    hostent *he = ::gethostbyaddr(SOCKOPT_CAST &addr, sizeof(addr), AF_INET);
    if (!he)
        throw new herror(host_not_found);
    return hostent_to_tuple(he);
}

str *getfqdn(str *name)
{
    str *n = name ? name->strip() : new str("");
    if (n->__len__() == 0)
        n = gethostname();
    try {
        __host_tuple *t = gethostbyaddr(n);
        str *hostname = t->__getfirst__();
        str *dot = new str(".");
        if (hostname->find(dot) != -1)
            return hostname;
        list<str *> *aliases = t->__getsecond__();
        for (size_t i = 0; i < aliases->units.size(); i++)
            if (aliases->units[i]->find(dot) != -1)
                return aliases->units[i];
        return hostname;
    } catch (OSError *) {
        return n;
    }
}

tuple2<str *, str *> *getnameinfo(socket::inet_address sockaddr_, __ss_int flags)
{
    sockaddr_in sin;
    tuple_to_sin_addr(&sin, sockaddr_);
    char host[NI_MAXHOST], serv[NI_MAXSERV];
    int r = ::getnameinfo(reinterpret_cast<sockaddr *>(&sin), sizeof(sin), host, sizeof(host), serv, sizeof(serv), (int)flags);
    if (r != 0) {
        gaierror *e = new gaierror(new str(gai_strerror(r)));
        e->__ss_errno = r;
        throw e;
    }
    return new tuple2<str *, str *>(2, new str(host), new str(serv));
}

__ss_int getprotobyname(str *protocolname)
{
    protoent *pe = ::getprotobyname(protocolname->c_str());
    if (!pe)
        throw new error(new str("protocol not found"));
    return pe->p_proto;
}

__ss_int getservbyname(str *servicename, str *protocolname)
{
    servent *se = ::getservbyname(servicename->c_str(), protocolname ? protocolname->c_str() : NULL);
    if (!se)
        throw new error(new str("service/proto not found"));
    return ntohs((uint16_t)se->s_port);
}

str *getservbyport(__ss_int port, str *protocolname)
{
    if (port < 0 || port > 0xffff)
        throw new OverflowError(new str("getservbyport: port must be 0-65535."));
    servent *se = ::getservbyport(htons((uint16_t)port), protocolname ? protocolname->c_str() : NULL);
    if (!se)
        throw new error(new str("port/proto not found"));
    return new str(se->s_name);
}

list<tuple2<__ss_int, str *> *> *if_nameindex()
{
    list<tuple2<__ss_int, str *> *> *result = new list<tuple2<__ss_int, str *> *>();
#ifdef WIN32
    /* as CPython does: walk the adapters and name each one via if_indextoname() */
    ULONG size = 15000;
    std::vector<char> buf;
    IP_ADAPTER_ADDRESSES *adapters;
    ULONG r;
    do {
        buf.resize(size);
        adapters = reinterpret_cast<IP_ADAPTER_ADDRESSES *>(buf.data());
        r = GetAdaptersAddresses(AF_UNSPEC, GAA_FLAG_SKIP_ANYCAST | GAA_FLAG_SKIP_MULTICAST | GAA_FLAG_SKIP_DNS_SERVER, NULL, adapters, &size);
    } while (r == ERROR_BUFFER_OVERFLOW);
    if (r != ERROR_SUCCESS)
        throw new error(new str("if_nameindex: GetAdaptersAddresses failed"));
    for (IP_ADAPTER_ADDRESSES *a = adapters; a; a = a->Next) {
        char name[IF_NAMESIZE + 1];
        if (::if_indextoname(a->IfIndex, name))
            result->append(new tuple2<__ss_int, str *>(2, (__ss_int)a->IfIndex, new str(name)));
    }
#else
    struct if_nameindex *ni = ::if_nameindex();
    if (!ni)
        throw make_error("if_nameindex");
    for (struct if_nameindex *i = ni; i->if_index != 0; i++)
        result->append(new tuple2<__ss_int, str *>(2, (__ss_int)i->if_index, new str(i->if_name)));
    ::if_freenameindex(ni);
#endif
    return result;
}

__ss_int if_nametoindex(str *name)
{
    unsigned int index = ::if_nametoindex(name->c_str());
    if (index == 0)
        throw new error(new str("no interface with this name"));
    return (__ss_int)index;
}

str *if_indextoname(__ss_int index)
{
    if (index < 0 || index > (__ss_int)UINT_MAX)
        throw new OverflowError(new str("index is out of range"));
    char name[IF_NAMESIZE + 1];
    if (!::if_indextoname((unsigned int)index, name))
        throw new error(new str("no interface with this index"));
    return new str(name);
}

bytes *inet_aton(str *ip_string)
{
    in_addr addr;
#ifdef WIN32
    /* winsock has no inet_aton(); inet_addr() returns INADDR_NONE both for
     * errors and for 255.255.255.255, as CPython special-cases too */
    if (strcmp(ip_string->c_str(), "255.255.255.255") == 0)
        addr.s_addr = INADDR_NONE;
    else if ((addr.s_addr = inet_addr(ip_string->c_str())) == INADDR_NONE)
        throw new error(new str("illegal IP address string passed to inet_aton"));
#else
    if (!::inet_aton(ip_string->c_str(), &addr))
        throw new error(new str("illegal IP address string passed to inet_aton"));
#endif
    return new bytes(reinterpret_cast<const char *>(&addr.s_addr), sizeof(addr.s_addr));
}

str *inet_ntoa(bytes *packed_ip)
{
    if (packed_ip->unit.size() != sizeof(in_addr))
        throw new error(new str("packed IP wrong length for inet_ntoa"));
    in_addr addr;
    memcpy(&addr, packed_ip->unit.data(), sizeof(addr));
    return in_addr_to_str(&addr);
}

bytes *inet_pton(__ss_int address_family, str *ip_string)
{
    unsigned char packed[sizeof(in6_addr)];
    /* like CPython, an unsupported family is left to inet_pton() (OSError) */
    int r = ::inet_pton((int)address_family, ip_string->c_str(), packed);
    if (r == 0)
        throw new error(new str("illegal IP address string passed to inet_pton"));
    if (r < 0)
        throw make_error("inet_pton");
    return new bytes(reinterpret_cast<const char *>(packed), address_family == AF_INET ? sizeof(in_addr) : sizeof(in6_addr));
}

str *inet_ntop(__ss_int address_family, bytes *packed_ip)
{
    size_t len;
    if (address_family == AF_INET)
        len = sizeof(in_addr);
    else if (address_family == AF_INET6)
        len = sizeof(in6_addr);
    else
        throw new ValueError(new str("unknown address family"));
    if (packed_ip->unit.size() != len)
        throw new ValueError(new str("invalid length of packed IP address string"));
    unsigned char packed[sizeof(in6_addr)];
    memcpy(packed, packed_ip->unit.data(), len);
    char ip[INET6_ADDRSTRLEN];
    if (!::inet_ntop((int)address_family, (void *)packed, ip, sizeof(ip)))
        throw make_error("inet_ntop");
    return new str(ip);
}

void *close(__ss_int fd)
{
    if (::CLOSE((socket_type)fd) == SOCKET_ERROR)
        throw make_error("close");
    return NULL;
}

__ss_int dup(__ss_int fd)
{
    return (__ss_int)dup_socket_fd((socket_type)fd);
}

__ss_bool has_ipv6 = True;

} // module namespace

