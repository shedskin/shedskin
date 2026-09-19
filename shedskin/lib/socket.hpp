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

#ifndef __SOCKET_HPP
#define __SOCKET_HPP

#include "builtin.hpp"

#if defined(WIN32)
#include <BaseTsd.h>
#include <stdlib.h>
typedef SSIZE_T ssize_t;
#endif

#ifdef WIN32

#include <io.h>

#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#define socklen_t int

typedef SOCKET socket_type;

#else

#include <sys/types.h>
#include <sys/socket.h>

typedef int socket_type;

#endif /* WIN32 */

using namespace __shedskin__;
namespace __socket__ {

class error;
class herror;
class gaierror;
class timeout;
class socket;

extern str *__name__;

/* The OSError constructor snapshots the C errno, which for the socket
   exceptions below is usually stale: on Windows the CRT errno is unrelated
   to WSAGetLastError(), and a timeout has no errno at all. So start from a
   plain message like CPython's OSError('msg'); make_error() in socket.cpp
   fills in errno/strerror for failed calls. */
inline void __init_plain_oserror(OSError *e, str *msg) {
    e->__init__(msg);
    e->__ss_errno = 0;
    e->strerror = 0;
    e->filename = 0;
}

extern class_ *cl_error;
class error : public OSError {
public:

    error(str *msg=0) : OSError(msg) {
        __class__ = cl_error;
        __init_plain_oserror(this, msg);
    }
    str *__str__() { return BaseException::__str__(); }
    str *__repr__() { return BaseException::__repr__(); }
};

extern class_ *cl_herror;
class herror : public OSError {
public:

    herror(str *msg=0) : OSError(msg) {
        __class__ = cl_herror;
        __init_plain_oserror(this, msg);
    }
    str *__str__() { return BaseException::__str__(); }
    str *__repr__() { return BaseException::__repr__(); }
};

extern class_ *cl_gaierror;
class gaierror : public OSError {
public:

    gaierror(str *msg=0) : OSError(msg) {
        __class__ = cl_gaierror;
        __init_plain_oserror(this, msg);
    }
    str *__str__() { return BaseException::__str__(); }
    str *__repr__() { return BaseException::__repr__(); }
};

extern class_ *cl_timeout;
class timeout : public OSError {
public:

    timeout(str *msg=0) : OSError(msg) {
        __class__ = cl_timeout;
        __init_plain_oserror(this, msg);
    }
    str *__str__() { return BaseException::__str__(); }
    str *__repr__() { return BaseException::__repr__(); }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_TimeoutError; } /* socket.timeout is TimeoutError */
#endif
};
extern class_ *cl_socket;
class socket : public object {
    double _timeout;
    bool _blocking;
    socket_type _fd;
    void read_wait();
    void write_wait();
    size_t send(const char *s, size_t len, int flags=0);
    socket *bind(const sockaddr *, socklen_t);
    socket *connect(const sockaddr *, socklen_t);
    socket *accept(sockaddr *, socklen_t *);
    size_t recvfrom(char *, size_t, int, sockaddr *, socklen_t *);
public:
    __ss_int family;
    __ss_int proto;
    __ss_int type;
    typedef tuple2<str *, __ss_int> *inet_address;

    socket(__ss_int family=-1, __ss_int type=-1, __ss_int proto=-1, __ss_int fileno=-1);
    /* internal: put the socket in the mode a timeout value means (0.0
       non-blocking, >0 timeout, <0 none) */
    void apply_timeout(double value);
    /* internal: adopt an existing fd instead of creating a new socket */
    struct wrap_fd_tag {};
    socket(wrap_fd_tag, socket_type fd, __ss_int family, __ss_int type, __ss_int proto);
    ~socket();
    str *__repr__();
    void __enter__();
    void __exit__();
    __ss_int __ss_fileno();
    __ss_int detach();
    socket *dup();
    __ss_int sendfile(file_binary *f, __ss_int offset=0, __ss_int count=-1);
    __ss_int getsockopt(__ss_int level, __ss_int optname);
    __ss_int connect_ex(inet_address address);
    __ss_bool get_inheritable();
    void *set_inheritable(__ss_bool inheritable);
    socket *bind(inet_address address);
    socket *bind(pyseq<str *> *address);
    file *makefile(str *flags=NULL);
    socket *setsockopt(__ss_int level, __ss_int optname, __ss_int value);
    socket *connect(inet_address address);
    socket *connect(pyseq<str *> *address);
    socket *setblocking(__ss_int flag);
    __ss_bool getblocking() { return __mbool(_blocking); }
    socket *shutdown(__ss_int how);
    __ss_int send(bytes *string, __ss_int flags=0);
    __ss_int sendall(bytes *string, __ss_int flags=0);
    __ss_int sendto(bytes *string, __ss_int flags, inet_address addr);
    __ss_int sendto(bytes *string, inet_address addr);
    /* sendto(data, address): the compiler appends the stub's address=0 default */
    __ss_int sendto(bytes *string, inet_address addr, __ss_int) { return sendto(string, addr); }
    socket *close();
    socket *settimeout(double value);
    double gettimeout() { return _timeout; }
    bytes *recv(__ss_int bufsize, __ss_int flags=0);
    tuple2<bytes *, inet_address> *recvfrom(__ss_int bufsize, __ss_int flags=0);
    socket *listen(__ss_int backlog);
    inet_address getpeername();
    inet_address getsockname();

    //INET
    tuple2<socket *, inet_address> *accept();

};

extern str * __name__;
void __init();
socket *create_connection(socket::inet_address address, double timeout=-1, socket::inet_address source_address=0, __ss_bool all_errors=False);
void *close(__ss_int fd);
__ss_int dup(__ss_int fd);
socket *fromfd(__ss_int fd, __ss_int family, __ss_int type, __ss_int proto=0);
socket *create_server(socket::inet_address address, __ss_int family=2, __ss_int backlog=-1, __ss_bool reuse_port=False, __ss_bool dualstack_ipv6=False);
__ss_bool has_dualstack_ipv6();
tuple2<socket *, socket *> *socketpair(__ss_int family=2, __ss_int type=1, __ss_int proto=0);
typedef tuple3<str *, list<str *> *, list<str *> *> __host_tuple;
str *gethostbyname(str *hostname);
__host_tuple *gethostbyname_ex(str *hostname);
__host_tuple *gethostbyaddr(str *ip_address);
tuple2<str *, str *> *getnameinfo(socket::inet_address sockaddr, __ss_int flags);
__ss_int getprotobyname(str *protocolname);
__ss_int getservbyname(str *servicename, str *protocolname=0);
str *getservbyport(__ss_int port, str *protocolname=0);
list<tuple2<__ss_int, str *> *> *if_nameindex();
__ss_int if_nametoindex(str *name);
str *if_indextoname(__ss_int index);
bytes *inet_aton(str *ip_string);
str *inet_ntoa(bytes *packed_ip);
bytes *inet_pton(__ss_int address_family, str *ip_string);
str *inet_ntop(__ss_int address_family, bytes *packed_ip);
__ss_int __ss_htonl(__ss_int);
__ss_int __ss_htons(__ss_int);
__ss_int __ss_ntohl(__ss_int);
__ss_int __ss_ntohs(__ss_int);
extern __ss_bool has_ipv6;
double getdefaulttimeout();
void *setdefaulttimeout(double x);
str *gethostname();
str *getfqdn(str *name=0);

extern __ss_int __ss_SOCK_STREAM, __ss_AF_INET, __ss_AF_INET6, __ss_AF_UNIX, __ss_SOCK_DGRAM, __ss_SOL_IP, __ss_SOL_SOCKET, __ss_IP_TOS;
extern __ss_int __ss_SHUT_RD, __ss_SHUT_WR, __ss_SHUT_RDWR, __ss_SOMAXCONN, __ss_SO_REUSEADDR;
extern __ss_int __ss_INADDR_ANY, __ss_INADDR_LOOPBACK, __ss_INADDR_NONE, __ss_INADDR_BROADCAST;
extern __ss_int __ss_AF_APPLETALK, __ss_AF_DECnet, __ss_AF_IPX, __ss_AF_SNA, __ss_AF_UNSPEC;
extern __ss_int __ss_AI_PASSIVE, __ss_AI_ADDRCONFIG, __ss_AI_ALL, __ss_AI_CANONNAME, __ss_AI_NUMERICHOST, __ss_AI_NUMERICSERV, __ss_AI_V4MAPPED;
extern __ss_int __ss_EAI_AGAIN, __ss_EAI_BADFLAGS, __ss_EAI_FAIL, __ss_EAI_FAMILY, __ss_EAI_MEMORY, __ss_EAI_NODATA;
extern __ss_int __ss_EAI_NONAME, __ss_EAI_SERVICE, __ss_EAI_SOCKTYPE;
extern __ss_int __ss_IPPORT_RESERVED, __ss_IPPORT_USERRESERVED;
extern __ss_int __ss_INADDR_ALLHOSTS_GROUP, __ss_INADDR_MAX_LOCAL_GROUP, __ss_INADDR_UNSPEC_GROUP;
extern __ss_int __ss_IPPROTO_AH, __ss_IPPROTO_DSTOPTS, __ss_IPPROTO_EGP, __ss_IPPROTO_ESP, __ss_IPPROTO_FRAGMENT, __ss_IPPROTO_HOPOPTS;
extern __ss_int __ss_IPPROTO_ICMP, __ss_IPPROTO_ICMPV6, __ss_IPPROTO_IDP, __ss_IPPROTO_IGMP, __ss_IPPROTO_IP, __ss_IPPROTO_IPV6;
extern __ss_int __ss_IPPROTO_NONE, __ss_IPPROTO_PIM, __ss_IPPROTO_PUP, __ss_IPPROTO_RAW, __ss_IPPROTO_ROUTING, __ss_IPPROTO_SCTP;
extern __ss_int __ss_IPPROTO_TCP, __ss_IPPROTO_UDP;
extern __ss_int __ss_IP_ADD_MEMBERSHIP, __ss_IP_ADD_SOURCE_MEMBERSHIP, __ss_IP_BLOCK_SOURCE, __ss_IP_DROP_MEMBERSHIP, __ss_IP_DROP_SOURCE_MEMBERSHIP, __ss_IP_HDRINCL;
extern __ss_int __ss_IP_MULTICAST_IF, __ss_IP_MULTICAST_LOOP, __ss_IP_MULTICAST_TTL, __ss_IP_OPTIONS, __ss_IP_PKTINFO, __ss_IP_RECVTOS;
extern __ss_int __ss_IP_RECVTTL, __ss_IP_TTL, __ss_IP_UNBLOCK_SOURCE;
extern __ss_int __ss_IPV6_CHECKSUM, __ss_IPV6_HOPLIMIT, __ss_IPV6_HOPOPTS, __ss_IPV6_JOIN_GROUP, __ss_IPV6_LEAVE_GROUP, __ss_IPV6_MULTICAST_HOPS;
extern __ss_int __ss_IPV6_MULTICAST_IF, __ss_IPV6_MULTICAST_LOOP, __ss_IPV6_PKTINFO, __ss_IPV6_RECVRTHDR, __ss_IPV6_RECVTCLASS, __ss_IPV6_RTHDR;
extern __ss_int __ss_IPV6_TCLASS, __ss_IPV6_UNICAST_HOPS, __ss_IPV6_V6ONLY;
extern __ss_int __ss_MSG_CTRUNC, __ss_MSG_DONTROUTE, __ss_MSG_OOB, __ss_MSG_PEEK, __ss_MSG_TRUNC, __ss_MSG_WAITALL;
extern __ss_int __ss_NI_DGRAM, __ss_NI_MAXHOST, __ss_NI_MAXSERV, __ss_NI_NAMEREQD, __ss_NI_NOFQDN, __ss_NI_NUMERICHOST;
extern __ss_int __ss_NI_NUMERICSERV;
extern __ss_int __ss_SOCK_RAW, __ss_SOCK_RDM, __ss_SOCK_SEQPACKET;
extern __ss_int __ss_SOL_TCP, __ss_SOL_UDP;
extern __ss_int __ss_SO_ACCEPTCONN, __ss_SO_BROADCAST, __ss_SO_DEBUG, __ss_SO_DONTROUTE, __ss_SO_ERROR, __ss_SO_KEEPALIVE;
extern __ss_int __ss_SO_LINGER, __ss_SO_OOBINLINE, __ss_SO_RCVBUF, __ss_SO_RCVLOWAT, __ss_SO_RCVTIMEO, __ss_SO_SNDBUF;
extern __ss_int __ss_SO_SNDLOWAT, __ss_SO_SNDTIMEO, __ss_SO_TYPE;
extern __ss_int __ss_TCP_FASTOPEN, __ss_TCP_KEEPCNT, __ss_TCP_KEEPINTVL, __ss_TCP_MAXSEG, __ss_TCP_NODELAY;
extern __ss_int __ss_EAGAIN, __ss_EBADF, __ss_EWOULDBLOCK;

} // module namespace
#endif
