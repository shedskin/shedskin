# put in the public domain by Salvatore Ferro

import select
import socket

class Request:

    def __init__(self, method, url, ver, headers, params):
        self.method = method
        self.url = url
        self.ver = ver
        self.headers = headers
        self.params = params

class WebServer:

    def __init__(self, port=50000):
        self.host = ''
        self.port = port
        self.backlog = 5
        self.size = 1024
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.server.bind((self.host, self.port))
        self.server.listen(self.backlog)

        self.input = [self.server.fileno()]
        self.running = 1
        self.mapSocks = {}

    def poll(self):
        #while running:

        inputready, outputready, exceptready = select.select(self.input, [], [])

        for s in inputready:
            if s == self.server.fileno():
                # handle the server socket 
                client, address = self.server.accept()
                self.input.append(client.fileno())
                self.mapSocks[client.fileno()] = client
                print("got client:", client.fileno())

            elif s in self.mapSocks.keys():
                # handle all other sockets 
                sock = self.mapSocks[s]
                data = sock.recv(self.size)
                if data:
                    #print "data detected", data
                    responseParams = {b"status":b"HTTP/1.0 200 OK"}
                    headers= {b"Content-Type":b"text/html"}

                    #responseParams["headers"] = {"Content-Type":"application/octet-stream"}                    
                    #responseHTML = "123123123";#self.handleRequest(self.parseRequest(data), responseParams)

                    responseHTML = self.handleRequest(self.parseRequest(data), responseParams, headers)

                    response = responseParams[b"status"] + b"\r\n"

                    for key in headers.keys():
                        response += key + b": " + headers[key] + b"\r\n"
                    response += b"\r\n"+responseHTML
                    print("sending response:*", response, "*")
                    '''
                    #response = "HTTP/1.0 200 OK\nContent-Type: text/html\n\n"+responseHTML+"\n\n"
                    sock.send(response);
                    '''
                    sock.send(response)
                    sock.close() 
                    self.input.remove(s)
                    #sock.send(data)
                else:
                    print("close from client detected")
                    sock.close() 
                    self.input.remove(s)


    def serve(self):
        while self.running:
            self.poll()
        self.server.close()

    def urlDecode(self, s):
        res = bytearray()
        max = len(s)
        skip=0
        for i in range(max):
            if (skip > 0): skip=skip-1; continue
            cur = s[i]
            if (cur == ord('+')): res.append(ord(' '))
            elif (cur == ord('%') and i <(max-2)):
                try:
                    res.append(int(s[i+1:i+3], 16))
                    skip=2
                except ValueError:
                    res.append(cur)
            else:
                res.append(cur)

        return bytes(res)

    def parseParams(self, params):
        ret = {b"":b""}
        del ret[b""]

        if (len(params)==0):
            return ret
        paramsCut = params.split(b"&")

        for paramPair in paramsCut:
            paramPairSplit = paramPair.split(b"=")
            val=b""
            if (len(paramPairSplit) > 0):
                val = self.urlDecode(paramPairSplit[1])
            ret[paramPairSplit[0]]=val

        return ret

    def parseRequest(self, data):
        print("got data:", data)
        data = data.replace(b"\r", b"")
        #print "got some data:" + data
        lines = data.split(b"\n")
        requestData = lines[0].split(b" ")

        #print "requestData:", requestData
        headerData={b"":b""}
        del headerData[b""]
        getFormData=False
        formData=b""
        for i in lines[1:]:
            if (getFormData):
                formData=i
            elif (b":" in i):
                headerSplit, sep, headerVal = i.partition(b":")
                headerData[headerSplit] = headerVal.strip()
            elif (i == b""):
                getFormData=True
        #print "headerData:", headerData
        parsedParams = self.parseParams(formData)

        url = requestData[1]
        if (b"?" in url):
            urlParamStr=url[url.find(b"?")+1:]
            urlParams = self.parseParams(urlParamStr)
            print("urlParams:", urlParams)

            parsedParams.update(urlParams)

        request = Request(requestData[0], requestData[1], requestData[2], headerData, parsedParams)
        #print "parsed:", request
        return request

    def handleRequest(self, request, responseParams, headers):
        print("got request method:", request.method, "url:", request.url)
        print("default responseParams:", responseParams)
        return b"<html>Hello, <B>world</b>!</html>"

WebServer().serve()
