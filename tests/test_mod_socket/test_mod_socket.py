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


def test_all():
    test_socket_loopback()


if __name__ == '__main__':
    test_all()
