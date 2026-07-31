# put in the public domain
# minimal test client for webserver.py -- connects, sends a single GET
# request, and prints the response. Lets you check the compiled webserver
# by hand instead of just trusting that it built.
#
# usage: client [path]
#   e.g. client "/hello?name=world"

import socket
import sys

def str_to_bytes(s):
    b = bytearray()
    for c in s:
        b.append(ord(c))
    return bytes(b)

def main():
    host = '127.0.0.1'
    port = 50000
    path = '/'
    if len(sys.argv) > 1:
        path = sys.argv[1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    request = b"GET " + str_to_bytes(path) + b" HTTP/1.0\r\nHost: localhost\r\n\r\n"
    sock.sendall(request)

    response = bytearray()
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response.extend(chunk)
    sock.close()

    print("--- response ---")
    print(bytes(response))

main()
