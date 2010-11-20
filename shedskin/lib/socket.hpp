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

#ifdef WIN32

#include <io.h>

#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#define socklen_t int

typedef SOCKET socket_type;

#else

#include <sys/types.h>
#include <sys/socket.h>

typedef int socket_type;
extern int __ss_AI_PASSIVE;

#endif /* WIN32 */

using namespace __shedskin__;
namespace __socket__ {

class error;
class herror;
class gaierror;
class timeout;
class socket;

extern __ss_int default_0;
extern __ss_int default_1;

extern str *__name__;

extern class_ *cl_error;
class error : public Exception {
public:

    error(str *msg=0) : Exception(msg) {
        __class__ = cl_error;
    }
};

extern class_ *cl_herror;
class herror : public Exception {
public:

    herror(str *msg=0) : Exception(msg) {
        __class__ = cl_herror;
    }
};

extern class_ *cl_gaierror;
class gaierror : public Exception {
public:

    gaierror(str *msg=0) : Exception(msg) {
        __class__ = cl_gaierror;
    }
};

extern class_ *cl_timeout;
class timeout : public Exception {
public:

    timeout(str *msg=0) : Exception(msg) {
        __class__ = cl_timeout;
    }
};
extern class_ *cl_socket;
class socket : public object {
    double _timeout;
    bool _blocking;
    socket_type _fd;
    void read_wait();
    void write_wait();
    int send(const char *s, size_t len, int flags=0);
    socket *bind(const sockaddr *, socklen_t);
    socket *connect(const sockaddr *, socklen_t);
    socket *accept(sockaddr *, socklen_t *);
    ssize_t recvfrom(char *, size_t, int, sockaddr *, socklen_t *);
public:
    __ss_int family;
    __ss_int proto;
    __ss_int type;
    typedef tuple2<str *, __ss_int> *inet_address;

    socket(__ss_int family=2, __ss_int type=1, __ss_int proto=0);
    ~socket();
    __ss_int __ss_fileno();
    str *getsockopt(__ss_int level, __ss_int optname, __ss_int value);
    socket *bind(inet_address address);
    socket *bind(pyseq<str *> *address);
    file *makefile(str *flags=NULL);
    socket *setsockopt(__ss_int level, __ss_int optname, __ss_int value);
    socket *connect(inet_address address);
    socket *connect(pyseq<str *> *address);
    socket *setblocking(__ss_int flag);
    socket *shutdown(__ss_int how);
    __ss_int send(str *string, __ss_int flags=0);
    __ss_int sendall(str *string, __ss_int flags=0);
    __ss_int sendto(str *string, __ss_int flags, inet_address addr);
    __ss_int sendto(str *string, inet_address addr);
    socket *close();
    socket *settimeout(double value);
    double gettimeout() { return _timeout; }
    str *recv(__ss_int bufsize, __ss_int flags=0);
    tuple2<str *, inet_address> *recvfrom(__ss_int bufsize, __ss_int flags=0);
    socket *listen(__ss_int backlog);
    inet_address getpeername();
    inet_address getsockname();

    //INET
    tuple2<socket *, inet_address> *accept();

};

extern str * __name__;
void __init();
str *gethostbyname(str *hostname);
str *inet_aton(str *x);
str *inet_ntoa(str *x);
__ss_int __ss_htonl(__ss_int);
__ss_int __ss_htons(__ss_int);
__ss_int __ss_ntohl(__ss_int);
__ss_int __ss_ntohs(__ss_int);
__ss_bool has_ipv6();
double getdefaulttimeout();
void *setdefaulttimeout(double x);
str *gethostname();

extern __ss_int __ss_SOCK_STREAM, __ss_AF_INET, __ss_AF_INET6, __ss_AF_UNIX, __ss_SOCK_DGRAM, __ss_SOL_IP, __ss_SOL_SOCKET, __ss_IP_TOS, __ss_IP_TTL;
extern __ss_int __ss_SHUT_RD, __ss_SHUT_WR, __ss_SHUT_RDWR, __ss_SOMAXCONN, __ss_SO_REUSEADDR;
extern __ss_int __ss_INADDR_ANY, __ss_INADDR_LOOPBACK, __ss_INADDR_NULL, __ss_INADDR_BROADCAST;

} // module namespace
#endif
