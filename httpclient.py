#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
#           2016 Geneva Giang
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import json

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    # try using regular expressions to parse the url
    def get_host_port(self,url):
        if url[:7] == "http://":
            url = url[7:]
        elif url[:8] == "https://":
            url = url[8:]

        try:
            host, others = url.split(':', 1)
        except:
            host, endpoint = url.split("/", 1)
            # default port if not given
            port = 80
        else:
            port, endpoint = others.split("/", 1)
        
        endpoint = "/" + endpoint

        return (host, int(port), endpoint)

    def connect(self, host, port):
        # use sockets!
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "-- Connect --"
        print (host,port)
        print "-------------"
        cs.connect((host, port))
        return cs

    def get_code(self, data):
        statusLine, others = data.split("\n", 1)
        httpVersion, statusCode, description = statusLine.split(" ", 2)
        print "\n\nCode: " + statusCode
        return int(statusCode)

    def get_headers(self,data):
        return None

    def get_body(self, data):
        index = data.find('\r\n\r\n')
        body = data[index+4:]
        print "\n\nBody:\n" + body
        return body


    # read everything from the socket
    def recvall(self, sock):
        response = bytearray()
        done = False
        while not done:
            # sock.setblocking(0)

            part = sock.recv(1024)

            if (part):
                response.extend(part)
            else:
                done = not part

        return str(response)

    def formulateGETRequest(self, host, port, endpoint):
        request = "GET " + endpoint + " HTTP/1.1\n" + \
                  "Host: " + host + ":" + str(port) + "\r\n\r\n"

        print "Request:\n" + request
        return request

    # make port default to 80 if not given?
    def sendRequest(self, request, host, port):
        cs = self.connect(host, port)
        cs.sendall(request)

        return cs

    def GET(self, url, args=None):
        (host, port, endpoint) = self.get_host_port(url)
        print "Host: %s\nPort: %d\nEndpoint: %s" % (host, port, endpoint)

        request = self.formulateGETRequest(host, port, endpoint)
        clientSocket = self.sendRequest(request, host, port)
        response = self.recvall(clientSocket)
        print "\n\nResponse: \n" + response

        code = self.get_code(response)
        body = self.get_body(response)

        print "--- Code : %d ---" % int(code)
        print "--- Body : \n%s ---" % body
        return HTTPResponse(code, body)


    def formulatePOSTRequest(self, host, port, endpoint, args):
        request = "POST " + endpoint + " HTTP/1.1\n" + \
                  "Host: " + host + ":" + str(port) + "\n" + \
                  "Content-Type: " + "application/x-www-form-urlencoded\n"

        if args != None:
            encoded_body = urllib.urlencode(args)
        else:
            encoded_body = ""
        request += "Content-Length: " + str(len(encoded_body)) + "\r\n\r\n"
        request += encoded_body

        print '\n\n' + request
        return request

    def POST(self, url, args=None):
        print args
        print len(json.dumps(args))

        (host, port, endpoint) = self.get_host_port(url)
        print "Host: %s\nPort: %d\nEndpoint: %s" % (host, port, endpoint)
        request = self.formulatePOSTRequest(host, port, endpoint, args)
        clientSocket = self.sendRequest(request, host, port)
        response = self.recvall(clientSocket)
        print "\n\nResponse: \n\n\n" + response

        code = self.get_code(response)
        body = self.get_body(response)

        print "--- Code : %d ---" % int(code)
        print "--- Body : \n%s ---" % body

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"

    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( command, sys.argv[1] )    
