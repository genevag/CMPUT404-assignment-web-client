#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
import select
import sys

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        # Rules taken from : https://regex101.com/r/aO0wR7/2 2016-01-29
        rules = "(?P<Protocol>[a-zA-Z]+\://)?(?P<Host>(?:(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]\d?|0)\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]\d?|0))|[a-zA-Z0-9\-\.]*\.+[a-zA-Z]*)(?P<Port>:(?:6553[0-5]|655[0-2]\d|65[0-4]\d{2}|6[0-4]\d{3}|[1-5]\d{4}|[1-9]\d{0,3}))?(?P<Location>/(?:[a-zA-Z0-9\-\._\?\,\'/\\\+&amp;%\$#\=~]*)[^\.\,\)\(\s]?)?"
        a = re.match(rules, url)

        httpProtocol = a.group("Protocol")
        host = a.group("Host")
        port = a.group("Port")
        endpoint = a.group("Location")

        if not port:
            port = 80
        else:
            port = int(port[1:])

        if not endpoint:
            endpoint = '/'

        return (host, port, endpoint)

    def connect(self, host, port):
        # use sockets!
        try:
            cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cs.connect((host, port))
            return cs
        except Exception, e:
            if e.strerror == "nodename nor servname provided, or not known":  # Error 8
                errorMsg = "Could not connect to %s:%s" % (host,port)
                print errorMsg
                raise e
                # sys.exit(errorMsg)
            else:
                raise


    def get_code(self, data):
        statusLine, others = data.split("\n",1)
        httpVersion, statusCode, description = statusLine.split(" ", 2)
        return int(statusCode)

    def get_headers(self,data):
        header, body = data.split("\r\n\r\n", 1)
        return header

    def get_body(self, data):
        header, body = data.split("\r\n\r\n", 1)
        return body


    # read everything from the socket
    def recvall(self, sock):
        response = bytearray()
        done = False

        while not done:
            part = sock.recv(1024)

            if (part):
                response.extend(part)
            else:
                done = not part

        return str(response)


    def formulateGETRequest(self, host, port, endpoint, args):
        if args != None:
            encoded_url_params = urllib.urlencode(args)
            if endpoint[-1] != '?':
                endpoint = endpoint + '?' + encoded_url_params

        # print encoded_url_params
        # print endpoint

        request = "GET " + endpoint + " HTTP/1.1\n" + \
                  "Host: " + host + ":" + str(port) + '\n' + \
                  "Connection: close" + "\r\n\r\n"


        print '--------- REQUEST -------'
        print request
        return request

    # make port default to 80 if not given?
    def sendRequest(self, request, sock):
        sock.sendall(request)
        return sock


    def GET(self, url, args=None):
        (host, port, endpoint) = self.get_host_port(url)
        
        sock = self.connect(host, port)

        request = self.formulateGETRequest(host, port, endpoint, args)
        
        self.sendRequest(request, sock)

        response = self.recvall(sock)
        print '--------- RESPONSE -------'
        print response

        headers = self.get_headers(response)
        code = self.get_code(headers)
        body = self.get_body(response)

        print body

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

        print '--------- REQUEST -------'
        print request
        
        return request

    def POST(self, url, args=None):
        (host, port, endpoint) = self.get_host_port(url)

        sock = self.connect(host, port)
        
        request = self.formulatePOSTRequest(host, port, endpoint, args)
        
        self.sendRequest(request, sock)
        
        response = self.recvall(sock)
        print '--------- RESPONSE -------'
        print response

        code = self.get_code(response)
        body = self.get_body(response)

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
        print client.command( sys.argv[1] )   
