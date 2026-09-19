import os
import socket
import sys


def test_socket_loopback():
    # bind to port 0 so the OS picks a free ephemeral port; avoids
    # collisions between test runs and works the same on every platform
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 0))
    server.listen(1)
    port = server.getsockname()[1]
    assert port > 0

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', port))

    conn, addr = server.accept()
    client.sendall(b'hello')
    data = conn.recv(5)
    assert data == b'hello'

    conn.close()
    client.close()
    server.close()


def test_attrs_repr():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    assert s.family == socket.AF_INET
    assert s.type == socket.SOCK_STREAM
    assert s.proto == 0
    r = repr(s)
    assert r.startswith('<socket.socket fd=')
    assert 'family=' in r and 'type=' in r and 'proto=' in r
    s.close()
    s.close()  # close() is idempotent


def test_with():
    with socket.socket() as s:
        assert s.fileno() != -1
        assert s.family == socket.AF_INET  # default family/type
        assert s.type == socket.SOCK_STREAM


def test_detach_dup_fromfd():
    s = socket.socket()
    d = s.dup()
    assert d.family == s.family
    assert d.type == s.type
    assert d.fileno() != s.fileno()
    d.close()

    fd = s.detach()
    assert fd != -1
    assert s.fileno() == -1  # after detach, socket no longer owns an fd

    s2 = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
    assert s2.family == socket.AF_INET
    assert s2.fileno() != -1
    s2.close()


def test_create_server():
    # backlog is keyword-only in CPython, so pass it by name
    server = socket.create_server(('127.0.0.1', 0), backlog=2)
    port = server.getsockname()[1]
    assert port > 0
    assert server.family == socket.AF_INET  # default family

    client = socket.socket()
    client.connect(('127.0.0.1', port))
    conn, addr = server.accept()
    client.sendall(b'hi')
    assert conn.recv(2) == b'hi'
    conn.close()
    client.close()
    server.close()

    assert socket.has_dualstack_ipv6() in (True, False)


def test_sendfile():
    fname = 'sendfile_testdata.bin'
    payload = b'0123456789' * 100
    with open(fname, 'wb') as f:
        f.write(payload)

    server = socket.create_server(('127.0.0.1', 0))
    port = server.getsockname()[1]
    client = socket.socket()
    client.connect(('127.0.0.1', port))
    conn, addr = server.accept()

    # whole file
    with open(fname, 'rb') as f:
        n = client.sendfile(f)
    assert n == len(payload)
    received = b''
    while len(received) < len(payload):
        received += conn.recv(4096)
    assert received == payload

    # offset and count
    with open(fname, 'rb') as f:
        n = client.sendfile(f, 5, 10)
    assert n == 10
    assert conn.recv(10) == payload[5:15]

    conn.close()
    client.close()
    server.close()
    os.remove(fname)


def test_byteorder():
    # round trips work on any endianness
    assert socket.ntohs(socket.htons(0x1234)) == 0x1234
    assert socket.ntohl(socket.htonl(0x12345678)) == 0x12345678
    assert socket.htons(0) == 0 and socket.htonl(0) == 0
    # a 16-bit value in network order is either unchanged or byte-swapped
    assert socket.htons(0x1234) in (0x1234, 0x3412)
    assert socket.htonl(1) in (1, 1 << 24)


def test_inet():
    assert socket.inet_aton('127.0.0.1') == b'\x7f\x00\x00\x01'
    assert socket.inet_aton('255.255.255.255') == b'\xff\xff\xff\xff'
    assert socket.inet_ntoa(b'\x7f\x00\x00\x01') == '127.0.0.1'
    assert socket.inet_ntoa(socket.inet_aton('192.168.1.2')) == '192.168.1.2'
    try:
        socket.inet_aton('300.1.1.1')
        assert False
    except OSError:
        pass
    try:
        socket.inet_ntoa(b'abc')
        assert False
    except OSError:
        pass

    assert socket.inet_pton(socket.AF_INET, '10.0.0.1') == b'\x0a\x00\x00\x01'
    assert socket.inet_ntop(socket.AF_INET, b'\x0a\x00\x00\x01') == '10.0.0.1'
    v6 = socket.inet_pton(socket.AF_INET6, '::1')
    assert v6 == b'\x00' * 15 + b'\x01'
    assert socket.inet_ntop(socket.AF_INET6, v6) == '::1'
    assert socket.inet_ntop(socket.AF_INET6, socket.inet_pton(socket.AF_INET6, '2001:db8::1')) == '2001:db8::1'
    try:
        socket.inet_pton(socket.AF_INET6, 'not an address')
        assert False
    except OSError:
        pass
    try:
        socket.inet_ntop(socket.AF_INET, b'\x00' * 16)
        assert False
    except ValueError:
        pass
    try:
        socket.inet_pton(socket.AF_UNSPEC, '1.2.3.4')
        assert False
    except OSError:
        pass
    try:
        socket.inet_ntop(socket.AF_UNSPEC, b'\x00' * 4)
        assert False
    except ValueError:
        pass


def test_names():
    assert socket.has_ipv6 in (True, False)
    assert socket.gethostname() != ''
    assert socket.gethostbyname('127.0.0.1') == '127.0.0.1'
    assert socket.gethostbyname('localhost') == '127.0.0.1'
    assert socket.getfqdn('') != ''
    assert socket.getfqdn('127.0.0.1') != ''
    assert socket.getfqdn() == socket.getfqdn('')
    name, aliases, addrs = socket.gethostbyname_ex('127.0.0.1')
    assert name != '' and addrs == ['127.0.0.1']
    name, aliases, addrs = socket.gethostbyaddr('127.0.0.1')
    assert name != '' and '127.0.0.1' in addrs
    try:
        socket.gethostbyname('no.such.host.invalid')
        assert False
    except socket.gaierror:
        pass
    try:
        socket.gethostbyaddr('no.such.host.invalid')
        assert False
    except OSError:  # gaierror or herror
        pass
    assert socket.getfqdn('no.such.host.invalid') == 'no.such.host.invalid'

    assert socket.getnameinfo(('127.0.0.1', 80), socket.NI_NUMERICHOST | socket.NI_NUMERICSERV) == ('127.0.0.1', '80')
    assert socket.getprotobyname('tcp') == socket.IPPROTO_TCP
    assert socket.getprotobyname('udp') == socket.IPPROTO_UDP
    assert socket.getservbyname('http', 'tcp') == 80
    assert socket.getservbyname('http') == 80
    assert socket.getservbyport(80, 'tcp') == 'http'
    assert socket.getservbyport(80) == 'http'
    try:
        socket.getservbyname('no-such-service-xyz')
        assert False
    except OSError:
        pass
    try:
        socket.getservbyport(70000)
        assert False
    except OverflowError:
        pass

    ifs = socket.if_nameindex()
    assert len(ifs) > 0
    for index, name in ifs:
        assert index > 0 and name != ''
        assert socket.if_nametoindex(name) == index
        assert socket.if_indextoname(index) == name
    try:
        socket.if_nametoindex('no-such-interface-xyz')
        assert False
    except OSError:
        pass
    try:
        socket.if_indextoname(-1)
        assert False
    except OverflowError:
        pass


def test_udp():
    a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    b = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    assert a.type == socket.SOCK_DGRAM
    a.bind(('127.0.0.1', 0))
    b.bind(('127.0.0.1', 0))
    assert b.sendto(b'dgram', a.getsockname()) == 5
    data, addr = a.recvfrom(100)
    assert data == b'dgram'
    assert addr == b.getsockname()
    assert a.sendto(b'back', 0, addr) == 4
    data, addr = b.recvfrom(100, 0)
    assert data == b'back' and addr == a.getsockname()
    a.close()
    b.close()


def test_stream_methods():
    server = socket.create_server(('127.0.0.1', 0))
    port = server.getsockname()[1]
    client = socket.socket()
    client.connect(('127.0.0.1', port))
    conn, addr = server.accept()

    # getpeername/getsockname pair up
    assert client.getpeername() == conn.getsockname()
    assert conn.getpeername() == client.getsockname()
    assert addr == client.getsockname()

    # send/recv with flags
    assert client.send(b'peek') == 4
    assert conn.recv(4, socket.MSG_PEEK) == b'peek'
    assert conn.recv(4) == b'peek'

    # getsockopt (int form)
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    assert conn.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY) != 0
    assert conn.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE) == socket.SOCK_STREAM
    assert conn.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) == 0

    # blocking mode
    assert conn.getblocking()
    conn.setblocking(False)
    assert not conn.getblocking()
    try:
        conn.recv(10)  # nothing pending, so does not block
        assert False
    except OSError:
        pass
    conn.setblocking(True)
    assert conn.getblocking()

    # timeouts
    conn.settimeout(0.05)
    assert conn.gettimeout() == 0.05
    # settimeout(0.0) is setblocking(False) and vice versa, and
    # setblocking(True) drops the timeout again (as settimeout(None) does)
    conn.settimeout(0.0)
    assert not conn.getblocking()
    assert conn.gettimeout() == 0.0
    conn.setblocking(True)
    assert conn.getblocking()
    conn.settimeout(0.05)
    conn.setblocking(False)
    assert conn.gettimeout() == 0.0
    conn.setblocking(True)
    conn.settimeout(0.05)
    try:
        conn.recv(10)
        assert False
    except socket.timeout:
        pass
    try:
        conn.recv(10)
        assert False
    except OSError:  # timeout is an OSError
        pass
    try:
        conn.recv(10)
        assert False
    except TimeoutError:  # socket.timeout is TimeoutError
        pass
    server.settimeout(0.05)
    try:
        server.accept()
        assert False
    except socket.timeout:
        pass
    try:
        conn.settimeout(-1.0)
        assert False
    except ValueError:
        pass

    # inheritable flag: sockets are created non-inheritable (PEP 446)
    assert not client.get_inheritable()
    client.set_inheritable(True)
    assert client.get_inheritable()
    client.set_inheritable(False)
    assert not client.get_inheritable()

    # shutdown: peer reads EOF
    client.shutdown(socket.SHUT_WR)
    conn.settimeout(5.0)
    assert conn.recv(10) == b''

    conn.close()
    client.close()
    server.close()


def test_makefile():
    # not exercised on windows: a socket handle is not a CRT file descriptor
    if sys.platform == 'win32':
        return
    a, b = socket.socketpair()
    f = a.makefile('w')
    f.write('line one\n')
    f.flush()
    assert b.recv(9) == b'line one\n'
    b.sendall(b'line two\n')
    g = a.makefile('r')
    assert g.readline() == 'line two\n'
    f.close()
    g.close()
    a.close()
    b.close()


def test_connect_ex():
    server = socket.create_server(('127.0.0.1', 0))
    port = server.getsockname()[1]
    client = socket.socket()
    assert client.connect_ex(('127.0.0.1', port)) == 0
    conn, addr = server.accept()
    conn.close()
    client.close()
    server.close()

    # grab a free port and close it again, so nobody is listening there
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    client = socket.socket()
    assert client.connect_ex(('127.0.0.1', port)) != 0
    client.close()
    client = socket.socket()
    try:
        client.connect(('127.0.0.1', port))
        assert False
    except socket.error as e:
        # ECONNREFUSED
        if sys.platform == 'win32':
            assert e.errno == 10061
        elif sys.platform == 'darwin':
            assert e.errno == 61
        else:
            assert e.errno == 111
    except OSError:  # socket.error is an OSError
        assert False
    client.close()


def test_create_connection():
    server = socket.create_server(('127.0.0.1', 0))
    port = server.getsockname()[1]
    client = socket.create_connection(('127.0.0.1', port), 2.0)
    assert client.gettimeout() == 2.0
    conn, addr = server.accept()
    client.sendall(b'cc')
    assert conn.recv(2) == b'cc'
    conn.close()
    client.close()
    # source_address and all_errors
    client = socket.create_connection(('127.0.0.1', port), source_address=('127.0.0.1', 0), all_errors=True)
    assert client.getsockname()[0] == '127.0.0.1'
    conn, addr = server.accept()
    conn.close()
    client.close()
    server.close()


def test_fileno_close_dup():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    fd = s.detach()
    # wrapping an fd detects the family/type
    w = socket.socket(fileno=fd)
    assert w.family == socket.AF_INET
    assert w.type == socket.SOCK_DGRAM
    assert w.fileno() == fd
    fd2 = socket.dup(fd)
    assert fd2 != fd
    socket.close(fd2)
    try:
        socket.close(fd2)  # already closed
        assert False
    except OSError:
        pass
    w.close()

    # wrapping a bound fd, with the proto also detected (except on macOS,
    # which has no SO_PROTOCOL, so CPython reports 0 there too)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    s.bind(('127.0.0.1', 0))
    name = s.getsockname()
    w = socket.socket(fileno=s.detach())
    assert w.family == socket.AF_INET
    assert w.type == socket.SOCK_STREAM
    if sys.platform != 'darwin':
        assert w.proto == socket.IPPROTO_TCP
    assert w.getsockname() == name
    w.close()

    # fromfd with an explicit proto
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    assert s.proto == socket.IPPROTO_TCP
    f = socket.fromfd(s.fileno(), socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    assert f.proto == socket.IPPROTO_TCP
    f.close()
    s.close()


def test_create_server_args():
    # reuse_port: SO_REUSEPORT on posix, a ValueError on windows (as in CPython)
    if sys.platform == 'win32':
        try:
            socket.create_server(('127.0.0.1', 0), reuse_port=True)
            assert False
        except ValueError:
            pass
    else:
        s = socket.create_server(('127.0.0.1', 0), reuse_port=True)
        assert s.getsockname()[1] > 0
        s.close()
    s = socket.create_server(('127.0.0.1', 0), family=socket.AF_INET)
    assert s.family == socket.AF_INET
    s.close()
    try:
        socket.create_server(('127.0.0.1', 0), dualstack_ipv6=True)
        assert False
    except ValueError:
        pass


def test_socketpair():
    # defaults only: CPython on POSIX gives an AF_UNIX pair, while shedskin
    # (like CPython on Windows) emulates it with a connected AF_INET pair
    a, b = socket.socketpair()
    assert a.family == b.family
    assert a.type == socket.SOCK_STREAM and b.type == socket.SOCK_STREAM
    assert a.fileno() != b.fileno()
    a.sendall(b'ping')
    assert b.recv(4) == b'ping'
    b.sendall(b'pong')
    assert a.recv(4) == b'pong'
    a.close()
    b.close()

    # default timeout 0.0 makes the pair non-blocking (as in CPython)
    socket.setdefaulttimeout(0.0)
    a, b = socket.socketpair()
    assert not a.getblocking() and not b.getblocking()
    socket.setdefaulttimeout(5.0)
    a, b = socket.socketpair()
    assert a.getblocking() and b.getblocking()
    assert a.gettimeout() == 5.0 and b.gettimeout() == 5.0
    a.sendall(b'ping')
    assert b.recv(4) == b'ping'
    a.close()
    b.close()
    socket.setdefaulttimeout(0.0)
    with socket.socket() as s:
        assert not s.getblocking()

    # non-zero proto: ValueError in shedskin (and CPython/Windows), OSError
    # in CPython on POSIX
    try:
        socket.socketpair(proto=6)
        assert False
    except (ValueError, OSError):
        pass
    # likewise for other families/types (only the defaults are supported here)
    try:
        socket.socketpair(socket.AF_UNSPEC)
        assert False
    except (ValueError, OSError):
        pass
    try:
        socket.socketpair(socket.AF_INET, socket.SOCK_DGRAM)
        assert False
    except (ValueError, OSError):
        pass


def test_constants():
    # touch every module constant, so a missing definition breaks the build
    consts = [
        socket.AF_APPLETALK, socket.AF_DECnet, socket.AF_IPX, socket.AF_SNA,
        socket.AF_UNSPEC, socket.AI_ADDRCONFIG, socket.AI_ALL, socket.AI_CANONNAME,
        socket.AI_NUMERICHOST, socket.AI_NUMERICSERV, socket.AI_PASSIVE, socket.AI_V4MAPPED,
        socket.EAGAIN, socket.EAI_AGAIN, socket.EAI_BADFLAGS, socket.EAI_FAIL,
        socket.EAI_FAMILY, socket.EAI_MEMORY, socket.EAI_NODATA, socket.EAI_NONAME,
        socket.EAI_SERVICE, socket.EAI_SOCKTYPE, socket.EBADF, socket.EWOULDBLOCK,
        socket.INADDR_ALLHOSTS_GROUP, socket.INADDR_MAX_LOCAL_GROUP, socket.INADDR_NONE, socket.INADDR_UNSPEC_GROUP,
        socket.IPPORT_RESERVED, socket.IPPORT_USERRESERVED, socket.IPPROTO_AH, socket.IPPROTO_DSTOPTS,
        socket.IPPROTO_EGP, socket.IPPROTO_ESP, socket.IPPROTO_FRAGMENT, socket.IPPROTO_HOPOPTS,
        socket.IPPROTO_ICMP, socket.IPPROTO_ICMPV6, socket.IPPROTO_IDP, socket.IPPROTO_IGMP,
        socket.IPPROTO_IP, socket.IPPROTO_IPV6, socket.IPPROTO_NONE, socket.IPPROTO_PIM,
        socket.IPPROTO_PUP, socket.IPPROTO_RAW, socket.IPPROTO_ROUTING, socket.IPPROTO_SCTP,
        socket.IPPROTO_TCP, socket.IPPROTO_UDP, socket.IPV6_CHECKSUM, socket.IPV6_HOPLIMIT,
        socket.AF_INET, socket.AF_INET6, socket.SOCK_STREAM, socket.SOCK_DGRAM,
        socket.INADDR_ANY, socket.INADDR_BROADCAST, socket.INADDR_LOOPBACK, socket.SOMAXCONN,
        socket.SOL_SOCKET, socket.SO_REUSEADDR,
        socket.IPV6_HOPOPTS, socket.IPV6_JOIN_GROUP, socket.IPV6_LEAVE_GROUP, socket.IPV6_MULTICAST_HOPS,
        socket.IPV6_MULTICAST_IF, socket.IPV6_MULTICAST_LOOP, socket.IPV6_PKTINFO, socket.IPV6_RECVRTHDR,
        socket.IPV6_RECVTCLASS, socket.IPV6_RTHDR, socket.IPV6_TCLASS, socket.IPV6_UNICAST_HOPS,
        socket.IPV6_V6ONLY, socket.IP_ADD_MEMBERSHIP, socket.IP_ADD_SOURCE_MEMBERSHIP, socket.IP_BLOCK_SOURCE,
        socket.IP_DROP_MEMBERSHIP, socket.IP_DROP_SOURCE_MEMBERSHIP, socket.IP_HDRINCL, socket.IP_MULTICAST_IF,
        socket.IP_MULTICAST_LOOP, socket.IP_MULTICAST_TTL, socket.IP_OPTIONS, socket.IP_PKTINFO,
        socket.IP_RECVTOS, socket.IP_TOS, socket.IP_TTL,  # IP_RECVTTL: CPython >= 3.14 only
        socket.IP_UNBLOCK_SOURCE, socket.MSG_CTRUNC, socket.MSG_DONTROUTE, socket.MSG_OOB,
        socket.MSG_PEEK, socket.MSG_TRUNC, socket.MSG_WAITALL, socket.NI_DGRAM,
        socket.NI_MAXHOST, socket.NI_MAXSERV, socket.NI_NAMEREQD, socket.NI_NOFQDN,
        socket.NI_NUMERICHOST, socket.NI_NUMERICSERV, socket.SHUT_RD, socket.SHUT_RDWR,
        socket.SHUT_WR, socket.SOCK_RAW, socket.SOCK_RDM, socket.SOCK_SEQPACKET,
        socket.SOL_IP, socket.SOL_TCP, socket.SOL_UDP, socket.SO_ACCEPTCONN,
        socket.SO_BROADCAST, socket.SO_DEBUG, socket.SO_DONTROUTE, socket.SO_ERROR,
        socket.SO_KEEPALIVE, socket.SO_LINGER, socket.SO_OOBINLINE, socket.SO_RCVBUF,
        socket.SO_RCVLOWAT, socket.SO_RCVTIMEO, socket.SO_SNDBUF, socket.SO_SNDLOWAT,
        socket.SO_SNDTIMEO, socket.SO_TYPE, socket.TCP_FASTOPEN, socket.TCP_KEEPCNT,
        socket.TCP_KEEPINTVL, socket.TCP_MAXSEG, socket.TCP_NODELAY,
    ]
    assert len(consts) == 132

    # values fixed by IANA or by CPython itself, so the same on all platforms
    assert socket.AF_UNSPEC == 0
    assert socket.IPPROTO_IP == 0
    assert socket.IPPROTO_ICMP == 1
    assert socket.IPPROTO_TCP == 6
    assert socket.IPPROTO_UDP == 17
    assert socket.IPPROTO_IPV6 == 41
    assert socket.IPPROTO_ICMPV6 == 58
    assert socket.IPPROTO_RAW == 255
    assert socket.SOL_TCP == socket.IPPROTO_TCP
    assert socket.SOL_UDP == socket.IPPROTO_UDP
    assert socket.MSG_OOB == 1
    assert socket.MSG_PEEK == 2
    assert socket.SHUT_RD == 0
    assert socket.SHUT_WR == 1
    assert socket.SHUT_RDWR == 2
    assert socket.INADDR_NONE == 0xffffffff
    assert socket.INADDR_ANY == 0
    assert socket.INADDR_BROADCAST == 0xffffffff
    assert socket.INADDR_LOOPBACK == 0x7f000001
    assert socket.SOMAXCONN > 0
    assert socket.INADDR_UNSPEC_GROUP == 0xe0000000
    assert socket.INADDR_ALLHOSTS_GROUP == 0xe0000001
    assert socket.INADDR_MAX_LOCAL_GROUP == 0xe00000ff
    assert socket.IPPORT_RESERVED == 1024
    assert socket.EBADF == 9
    # errno values differ per platform: linux/windows CRT use 11, BSD/macOS 35
    if sys.platform == 'darwin':
        assert socket.EAGAIN == 35
    else:
        assert socket.EAGAIN == 11
    # equal on POSIX; on windows CPython uses WSAEWOULDBLOCK (10035) instead
    if sys.platform == 'win32':
        assert socket.EWOULDBLOCK == 10035
    else:
        assert socket.EWOULDBLOCK == socket.EAGAIN

    # actually usable as socket options
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    s.close()


def test_default_timeout():
    # last, as the default timeout stays in effect for later sockets
    socket.setdefaulttimeout(1.5)
    assert socket.getdefaulttimeout() == 1.5
    s = socket.socket()
    assert s.gettimeout() == 1.5
    assert s.getblocking()
    s.close()
    try:
        socket.setdefaulttimeout(-1.0)
        assert False
    except ValueError:
        pass

    # timed-out recv on a socket created under the default timeout, and a
    # fresh recv afterwards (the data has landed by then even on macOS)
    server = socket.create_server(('127.0.0.1', 0))
    port = server.getsockname()[1]
    socket.setdefaulttimeout(0.05)
    client = socket.socket()
    client.connect(('127.0.0.1', port))
    conn, addr = server.accept()
    assert conn.gettimeout() == 0.05
    try:
        conn.recv(10)
        assert False
    except socket.timeout as e:
        assert str(e) == 'timed out'
    client.sendall(b'x')
    conn.settimeout(5.0)
    assert conn.recv(1) == b'x'
    conn.close()
    client.close()
    server.close()

    # 0.0: new sockets are non-blocking
    socket.setdefaulttimeout(0.0)
    s = socket.socket()
    assert not s.getblocking()
    assert s.gettimeout() == 0.0
    s.close()
    fd = socket.socket().detach()
    w = socket.socket(fileno=fd)
    assert not w.getblocking()
    w.close()


def test_all():
    test_socket_loopback()
    test_attrs_repr()
    test_with()
    test_detach_dup_fromfd()
    test_create_server()
    test_sendfile()
    test_byteorder()
    test_inet()
    test_names()
    test_udp()
    test_stream_methods()
    test_makefile()
    test_connect_ex()
    test_create_connection()
    test_fileno_close_dup()
    test_create_server_args()
    test_socketpair()
    test_constants()
    test_default_timeout()


if __name__ == '__main__':
    test_all()
