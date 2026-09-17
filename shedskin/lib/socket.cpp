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

#include "socket.hpp"
#include <climits>
#include <fcntl.h>
#include <cerrno>

#ifndef WIN32
#include <unistd.h>
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
#ifdef EWOULDBLOCK
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

str* make_errstring(const char *prefix)
{
    std::ostringstream os;
    os << prefix << ": " << strerror(ERRNO) << " (errno " << ERRNO << ")";
    return new str( os.str().c_str() );
}

static socket_type dup_socket_fd(socket_type fd)
{
#ifdef WIN32
    /* SOCKETs are not CRT file descriptors, so dup() does not apply;
     * duplicate the underlying socket the way CPython does. */
    WSAPROTOCOL_INFOW info;
    if (WSADuplicateSocketW(fd, GetCurrentProcessId(), &info) == SOCKET_ERROR)
        throw new error(make_errstring("dup"));
    socket_type r = WSASocketW(FROM_PROTOCOL_INFO, FROM_PROTOCOL_INFO, FROM_PROTOCOL_INFO, &info, 0, WSA_FLAG_OVERLAPPED);
    if (r == INVALID_SOCKET)
        throw new error(make_errstring("dup"));
    return r;
#else
    int r = ::dup(fd);
    if (r == SOCKET_ERROR)
        throw new error(make_errstring("dup"));
    return r;
#endif
}

socket::socket(socket::wrap_fd_tag, socket_type fd, __ss_int family_, __ss_int type_, __ss_int proto_) {
    this->__class__ = cl_socket;
    this->family = family_;
    this->type = type_;
    this->proto = proto_;
    _fd = fd;
    _timeout = __ss_default_timeout;
    _blocking = true;
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
    sock->_blocking = _blocking;
    sock->_timeout = _timeout;
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


str *socket::getsockopt(__ss_int level, __ss_int optname, __ss_int value) {
    socklen_t buflen = (socklen_t)value;
    std::vector<char> buf(buflen);

    if (::getsockopt(_fd, (int)level, (int)optname, buf.data(), &buflen) == SOCKET_ERROR)
        throw new error(make_errstring("getsockopt"));

    return new str(buf.data(), buflen);
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
        throw new error(make_errstring("makefile"));
	}
    file *f = new file(fp);
    f->name = new str("<socket>");
    f->mode = mode;
    return f;
}

socket *socket::bind(const sockaddr *sa, socklen_t salen)
{
    if (::bind(_fd, sa, salen) == SOCKET_ERROR) {
        throw new error(make_errstring("bind"));
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
        throw new herror(host_not_found);
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
    if (::setsockopt(_fd, (int)level, (int)optname, SOCKOPT_CAST &value, sizeof(value)) == SOCKET_ERROR)
        throw new error(make_errstring("setsockopt"));

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
            throw new error(make_errstring("fcntl"));
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
            throw new error(make_errstring("fcntl"));
        }
}
socket *socket::connect(const sockaddr *sa, socklen_t salen)
{
    if (_blocking && _timeout > 0) {
        // temporarily set the socket to nonblocking
        set_nonblocking(_fd);
    }

    if (::connect(_fd, sa, salen) == SOCKET_ERROR) {
	if (ERRNO != EINPROGRESS) {
	    if (_blocking && _timeout > 0)
		set_blocking(_fd); // turn blocking back on
	    throw new error(make_errstring("connect"));
	}
    }

    if (_blocking && _timeout > 0) {
        fd_set s;
        FD_ZERO(&s);
        FD_SET(_fd, &s);

        timeval to;
        to.tv_sec = static_cast<tv_sec_type>(_timeout);
        to.tv_usec = static_cast<tv_usec_type>(1000000 * (_timeout - (double)to.tv_sec));

        if (::select(_fd+1, 0, &s, 0, &to) == SOCKET_ERROR) {
	    set_blocking(_fd); // turn blocking back on
            throw new error(make_errstring("select"));
	}
        if (! FD_ISSET(_fd, &s)) {
	    set_blocking(_fd); // turn blocking back on
	    throw new timeout(timed_out);
	}

        // get connection status
        int err = 0;
        socklen_t errsize = sizeof(err);
        if (::getsockopt(_fd, SOL_SOCKET, SO_ERROR, SOCKOPT_CAST &err, &errsize) == SOCKET_ERROR) {
	    set_blocking(_fd); // turn blocking back on
            throw new error(make_errstring("getsockopt"));
	}

        set_blocking(_fd); // turn blocking back on

        if (err != 0) {
            std::ostringstream os;
            os << "connect: " << strerror(err) << " (errno " << err << ")";
            const std::string& s2 = os.str();
            throw new error(new str( s2.c_str() ));
        }
    }

    return this;
}

socket *socket::setblocking(__ss_int flag)
{
    if (flag)  {
        //blocking mode
        _blocking = true;
	_timeout = __ss_default_timeout;	// use default value set by socket.setdefaulttimeout()
        set_blocking(_fd);
    } else {
        //non-blocking
        set_nonblocking(_fd);
        _blocking = false;
    }
    return this;
}

socket *socket::settimeout(double val)
{
    if (val < 0)
	throw new ValueError(new str("Timeout value out of range"));

    if (val == 0) { // s.settimeout(0.0) is equivalent to s.setblocking(0)
        set_nonblocking(_fd);
	_blocking = false;
    } else {
        set_blocking(_fd);
	_blocking = true;
	_timeout = val;
    }
    return this;
}

socket *socket::shutdown(__ss_int how)
{
    if (::shutdown(_fd, (int)how) == SOCKET_ERROR)
        throw new error(make_errstring("shutdown"));
    return this;
}

void socket::write_wait()
{
    if (_blocking && _timeout >= 0) {
        fd_set s;
        FD_ZERO(&s);
        FD_SET(_fd, &s);
        timeval to;
        to.tv_sec = static_cast<tv_sec_type>(_timeout);
        to.tv_usec = static_cast<tv_usec_type>(1000000 * (_timeout - (double)to.tv_sec));
        if (::select(_fd+1, 0, &s, 0, &to) == SOCKET_ERROR)
            throw new error(make_errstring("select"));
        if (! FD_ISSET(_fd, &s))
            throw new timeout(timed_out);
    }
}

size_t socket::send(const char *s, size_t len, int flags)
{
    write_wait();

    ssize_t r = ::send(_fd, s, len, flags);
    if (r == SOCKET_ERROR)
        throw new error(make_errstring("send"));
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
        throw new error(make_errstring("sendto"));

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
            throw new error(make_errstring(STRINGIFY(CLOSE)));
#undef STRINGIFY
    }
    return this;
}

void socket::read_wait()
{
    if (_blocking && _timeout >= 0) {
        fd_set s;
        FD_ZERO(&s);
        FD_SET(_fd, &s);
        timeval to;
        to.tv_sec = static_cast<tv_sec_type>(_timeout);
        to.tv_usec = static_cast<tv_usec_type>(1000000 * (_timeout - (double)to.tv_sec));
        if (::select(_fd+1, &s, 0, 0, &to) == SOCKET_ERROR)
            throw new error(make_errstring("select"));
        if (! FD_ISSET(_fd, &s))
            throw new timeout(timed_out);
    }
}

bytes *socket::recv(__ss_int bufsize, __ss_int flags)
{
    read_wait();

    std::vector<char> buf((size_t)bufsize);
    ssize_t len = ::recv(_fd, buf.data(), (size_t)bufsize, (int)flags);
    if (len == SOCKET_ERROR)
        throw new error(make_errstring("recv"));
    return new bytes(buf.data(), (size_t)len);
}

#ifdef WIN32
void inet_ntop(int proto, const in_addr *addr, char *dst, size_t len)
{
    int v = ntohl(addr->s_addr);
    sprintf(dst, "%d.%d.%d.%d", ((v>> 24) & 0xff) ,((v >> 16) & 0xff) ,((v >> 8) & 0xff) ,((v) & 0xff));
}
#endif

static socket::inet_address sin_addr_to_tuple(const sockaddr_in *sin)
{
    char ip[sizeof("xxx.xxx.xxx.xxx")];
    inet_ntop(AF_INET, &sin->sin_addr, ip, sizeof(ip));
    socket::inet_address addr = new tuple2<str *, __ss_int>(2, new str(ip), static_cast<__ss_int>(ntohs(sin->sin_port)));
    return addr;
}

size_t socket::recvfrom(char *buf, size_t bufsize, int flags, sockaddr *sa, socklen_t *salen)
{
    read_wait();
    ssize_t len = ::recvfrom(_fd, buf, bufsize, flags, sa, salen);
    if (len == SOCKET_ERROR)
        throw new error(make_errstring("recvfrom"));
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

socket::socket(__ss_int family_, __ss_int type_, __ss_int proto_) {
    this->__class__ = cl_socket;

    this->family = family_;
    this->type = type_;
    this->proto = proto_;
    _fd = ::socket((int)family_, (int)type_, (int)proto_);
    if (_fd == SOCKET_ERROR)
        throw new error(make_errstring("socket"));
    _timeout = __ss_default_timeout;
    _blocking = true;
}

socket::~socket()
{
    if (_fd != SS_INVALID_SOCKET)
        ::CLOSE(_fd); // ignore error since we can't throw
}

socket *socket::listen(__ss_int backlog)
{
    if(::listen(_fd, (int)backlog) == SOCKET_ERROR)
        throw new error(make_errstring("listen"));
    return this;
}

socket* socket::accept(sockaddr *sa, socklen_t *salen)
{
    if (_blocking && _timeout >= 0) {
        fd_set s;
        FD_ZERO(&s);
        FD_SET(_fd, &s);
        timeval to;
        to.tv_sec = static_cast<tv_sec_type>(_timeout);
        to.tv_usec = static_cast<tv_usec_type>(1000000 * (_timeout - (double)to.tv_sec));
        if (::select(_fd+1, &s, 0, 0, &to) == SOCKET_ERROR)
            throw new error(make_errstring("select"));
        if (! FD_ISSET(_fd, &s))
            throw new timeout(timed_out);
    }
    int r;
    if ((r = ::accept(_fd, sa, salen)) == SOCKET_ERROR) {
        throw new error(make_errstring("accept"));
    }
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
        throw new error(make_errstring("getpeername"));
    return sin_addr_to_tuple(&addr);
}

socket::inet_address socket::getsockname()
{
    struct sockaddr_in addr;
    socklen_t addrlen = sizeof(addr);
    if (::getsockname(_fd, reinterpret_cast<sockaddr *>(&addr), &addrlen) == SOCKET_ERROR)
        throw new error(make_errstring("getsockname"));
    return sin_addr_to_tuple(&addr);
}

str *gethostname()
{
    char name[HOST_NAME_MAX];
    if (::gethostname(name, sizeof(name)) == -1)
        throw new herror(make_errstring("gethostname"));
    return new str(name);
}

socket *create_connection(socket::inet_address address, double timeout, socket::inet_address source_address)
{
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
        lsock->bind(new tuple2<str *, __ss_int>(2, new str("127.0.0.1"), 0));
        lsock->listen(1);
        csock = new socket(family, type, proto);
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
    return new tuple2<socket *, socket *>(2, ssock, csock);
}

__ss_int _ss_htonl(__ss_int x) {
    return (__ss_int)htonl((uint32_t)x);
}

__ss_int _ss_htons(__ss_int x) {
    return (__ss_int)htons((uint16_t)x);
}

__ss_int _ss_ntohl(__ss_int x) {
    return (__ss_int)ntohl((uint32_t)x);
}

__ss_int _ss_ntohs(__ss_int x) {
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

str *gethostbyname(str *hostname)
{
    hostent *he = ::gethostbyname(hostname->c_str());
    if (!he)
        throw new herror(host_not_found);
    char ip[sizeof("xxx.xxx.xxx.xxx")];
    uint32_t addr = htonl((uint32_t)(*((int *) he->h_addr_list[0])) );
    sprintf(ip, "%d.%d.%d.%d", ((addr >> 24) & 0xff), ((addr >> 16) & 0xff), ((addr >> 8) & 0xff), (addr & 0xff));
    return new str(ip);
}

str *inet_aton(str *x)
{
    unsigned long int addr = string_to_addr(x->c_str());
    return new str((char *) &addr, 4);
}

str *inet_ntoa(str *x)
{
    const char *s = x->c_str();
    int addr = *((int *) s);
    char ip[sizeof("xxx.xxx.xxx.xxx")];
    sprintf(ip, "%d.%d.%d.%d", ((addr >> 24) & 0xff), ((addr >> 16) & 0xff), ((addr >> 8) & 0xff), (addr & 0xff));
    return new str(ip);
}

__ss_bool has_ipv6()
{
    return False;
}

} // module namespace

