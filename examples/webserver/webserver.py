# put in the public domain by Salvatore Ferro

import select
import socket

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
                    responseParams = {"status":"HTTP/1.0 200 OK"}
                    headers= {"Content-Type":"text/html"}

                    #responseParams["headers"] = {"Content-Type":"application/octet-stream"}                    
                    #responseHTML = "123123123";#self.handleRequest(self.parseRequest(data), responseParams)

                    responseHTML = self.handleRequest(self.parseRequest(data), responseParams, headers)

                    response = responseParams["status"] + "\r\n"

                    for key in headers.keys():
                        response += key + ": " + headers[key] +"\r\n"
                    response += "\r\n"+responseHTML
                    print("sending response:*" + response+"*")
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

    def fromHex(self, hexStr):
        ret=chr(int(hexStr, 16))
        return ret

    def ishex(self, chr):
        x = ord(chr)
        return (x >= ord('0') and x <= ord('9')) or (x >= ord('a') and x <= ord('f')) or (x >= ord('A') and x <= ord('F'))


    def urlDecode(self, s):
        res = ""
        max = len(s)
        skip=0
        for i in range(max):
            if (skip > 0): skip=skip-1; continue
            cur = s[i]
            if (cur == '+'): cur = ' '
            elif (cur == '%' and i <(max-2) and self.ishex(s[i+1]) and self.ishex(s[i+2])):
                cur=self.fromHex(s[i+1:i+3])
                skip=2
            res += cur

        return res

    def parseParams(self, params):
        ret = {}

        if (len(params)==0):
            return
        paramsCut = params.split("&")

        for paramPair in paramsCut:
            paramPairSplit = paramPair.split("=")
            val=""
            if (len(paramPairSplit) > 0):
                val = self.urlDecode(paramPairSplit[1])
            ret[paramPairSplit[0]]=val

        return ret

    def parseRequest(self, data):
        print("got data:" + data)
        data = data.replace("\r", "")
        #print "got some data:" + data
        lines = data.split("\n")
        requestData = lines[0].split(" ")

        #print "requestData:", requestData
        headerData={}
        getFormData=False
        formData=None
        for i in lines[1:]:
            if (getFormData):
                formData=i
            elif (":" in i):
                headerSplit = i.split(":")[0]
                #print "headerSplit:", headerSplit
                headerData[headerSplit] = i[len(headerSplit)+1:].strip()
            elif (i == ""):
                getFormData=True
        #print "headerData:", headerData
        parsedParams = self.parseParams(formData)
        if (parsedParams == None):parsedParams={}

        url = requestData[1]
        urlParams = {}
        if ("?" in url):
            urlParamStr=url[url.find("?")+1:]
            urlParams = self.parseParams(urlParamStr)
            print("urlParams:", urlParams)

            parsedParams.update(urlParams)

        request = {"method":requestData[0], "url":requestData[1], "ver":requestData[2], "headers":headerData, "params":parsedParams}
        #print "parsed:", request
        return request

    def handleRequest(self, request, responseParams, headers):
        print("got request:", request)
        print("default responseParams:", responseParams)
        return "<html>Hello, <B>world</b>!</html>"

WebServer().serve()
