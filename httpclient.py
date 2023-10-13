#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # Get the request code from the data 
        code = data.split("\r\n")[0].split(" ")[1]
        try:
            return int(code)
        except:
            print("There was an error getting the code")

    def get_headers(self, data):
        # Get the header from the data
        header = data.split("\r\n\r\n")[0]
        return header

    def get_body(self, data):
        # Get the body from data
        body = data.split("\r\n\r\n")[1]
        return body
    
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

    def GET(self, url, args=None):
        code = 500
        body = ""
        parsed = urllib.parse.urlparse(url)

        # Split up parsed into the host, port, and path
        host = parsed.hostname
        port = parsed.port
        path = parsed.path
        query = parsed.query

        if (port == None):
            port = 80 # The default port
        if (path == "" or path == None):
            path = "/" # Root request
        if (query != None):
            path = path + "?" + query

        # Connect to the host and port
        self.connect(host, port)

        # Send the request
        self.sendall("GET " + path + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: Close\r\n\r\n")

        
        content = self.recvall(self.socket)
        code = self.get_code(content)
        body = self.get_body(content)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        parsed = urllib.parse.urlparse(url)
        # Split up parsed into the host, port, and path
        host = parsed.hostname
        port = parsed.port
        path = parsed.path
        query = parsed.query

        if (port == None):
            port = 80
        if (path == "" or path == None):
            path = "/"
        if (query != None):
            path = path + "?" + query

        # check the form data
        form_data = None
        if args == None:
            form_data = ""
        else:
            form_data = "&"
            for key, value in args.items():
                form_data += (key + "=" + value + "&")


        # Connect to the host and port
        self.connect(host, port)

        # Send the request
        self.sendall(f'POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(form_data)}\r\nConnection: Close\r\n\r\n{form_data}')
        # self.sendall("POST " + path + " HTTP/1.1\r\nHost: " + host + "\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: " + str(len(form_data)) + "\r\n Connection: Close \r\n\r\n" + form_data) # For some reason this doesnt work???

        content = self.recvall(self.socket)
        code = self.get_code(content)
        body = self.get_body(content)

        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "POST"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))

