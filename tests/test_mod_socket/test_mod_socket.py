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

    # non-zero proto: ValueError in shedskin (and CPython/Windows), OSError
    # in CPython on POSIX
    try:
        socket.socketpair(proto=6)
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
    assert len(consts) == 122

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
    assert socket.INADDR_UNSPEC_GROUP == 0xe0000000
    assert socket.INADDR_ALLHOSTS_GROUP == 0xe0000001
    assert socket.INADDR_MAX_LOCAL_GROUP == 0xe00000ff
    assert socket.IPPORT_RESERVED == 1024
    assert socket.EAGAIN == 11
    assert socket.EBADF == 9
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


def test_all():
    test_socket_loopback()
    test_attrs_repr()
    test_with()
    test_detach_dup_fromfd()
    test_create_server()
    test_sendfile()
    test_socketpair()
    test_constants()


if __name__ == '__main__':
    test_all()
