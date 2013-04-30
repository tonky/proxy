import socket, os
import BaseHTTPServer, SimpleHTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
import ssl

host, port = "127.0.0.1", 4443

class SecureHTTPRequestHandler(BaseHTTPRequestHandler):
    def setup(self):
        print self
        print dir(self)
        print self.request
        print dir(self.request)
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)

httpd = BaseHTTPServer.HTTPServer((host, port), SecureHTTPRequestHandler)
# httpd.socket = ssl.wrap_socket(httpd.socket, certfile='/home/tonky/projects/server.pem', server_side=True)
print "serving HTTPS on %s:%d" % (host, port)
httpd.serve_forever()
