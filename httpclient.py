#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust &
# Copyright 2023 William Boytinck
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
import urllib.parse

'''
# REFERENCES:
# https://pymotw.com/3/urllib.parse/index.html
# CMPUT 404 Lab 2 [snippets provided by the CMPUT 404 team]
# https://stackoverflow.com/questions/14551194/how-are-parameters-sent-in-an-http-post-request
'''
def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):
    # TODO: Review args for GET, (do they even work? Its not needed for the tests)
    # but I have a feeling hindle would sneak something in

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        #print("Successfully connected to socket!")
        return None

    def get_code(self, data):
        #print(f"My data: {data}" )
        # the first line of data will be the status code
        return int(data.split()[1])

    def get_headers(self,data):
        return None

    def get_body(self, data):
        #print(f"My data: {data}" )
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    # tests run GET and post, meaning code needs to be self.get_code
    # and body needs to be self.get_body
    def GET(self, url, args=None):
        # parse the url into useable components
        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname
        port = parsed.port
        path = parsed.path
        # default port to 80 if port not found
        # default path to root if path not found
        if not port:
            port = 80
        if not path or path[-1] != "/":
            path += "/"
       
        # this is NOT needed for free-tests.py
        # BUT, that being said, the function has an args
        # parameter, so might as well add this       
        if args:
            # another portion of the request needs to be added to the path
            request_data = urllib.parse.urlencode(args)
            path = path + "?" + request_data
        
        # connect to the socket with host & port
        self.connect(host,port)
        # make the request
        request = f"GET {path} HTTP/1.1\r\n"
        content_connection = f"Host: {host}\r\nConnection: close\r\n\r\n"    
        request += content_connection
        # send the request
        self.sendall(request)
        
        # After we send the request, wait for the server's response
        data = self.recvall(self.socket)
        # WE are done with the socket now, close it
        self.close()
        # get the response code
        code = self.get_code(data)
        # get the respones body
        body = self.get_body(data)
        # return the response
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname
        port = parsed.port
        path = parsed.path
        # make port to 80 if port not found
        # default path to root if path not found
        if not port:
            port = 80
        if not path or path[-1] != "/":
            path += "/"
        
        # POST arguments    
        if args:
            # encode the arguments if they exist
            request_data = urllib.parse.urlencode(args)
        else:
            # empty POST
            request_data = ""
        
        self.connect(host,port)
        # make the request
        request = f"POST {path} HTTP/1.1\r\n"
        content_length = f"Host: {host}\r\nContent-Length: {len(request_data)}\r\n"
        content_type = f"Content-Type: application/x-www/form-urlencoded\r\n"
        content_connection = f"Connection: close\r\n\r\n{request_data}"
        request = request + content_length + content_type + content_connection
        # send the request
        self.sendall(request)
        # After we send the request, wait for the server's response
        data = self.recvall(self.socket)
        # WE are done with the socket now, close it
        self.close()
        # get the response code
        code = self.get_code(data)
        # get the respones body
        body = self.get_body(data)
        # return the response
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
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
