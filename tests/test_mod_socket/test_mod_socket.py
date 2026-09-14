import os
import socket


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


def test_all():
    test_socket_loopback()
    test_attrs_repr()
    test_with()
    test_detach_dup_fromfd()
    test_create_server()
    test_sendfile()


if __name__ == '__main__':
    test_all()
