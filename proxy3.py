import SocketServer
import requests
import re

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    cookie = ""

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(4096).strip()
        # print "{} wrote:".format(self.client_address[0])
        # print self.data

        host = re.search("Host: (\S+)", self.data).groups()[0]

        path = re.search("(GET|POST) (\S+)", self.data).groups()[1]

        cookie_match = re.search("Cookie: (.*)", self.data)

        if cookie_match:
            self.cookie = cookie_match.groups()[0]

        ref_match = re.search('Referer: (\S+)', self.data)
        tunnel_path_match = re.search("/tunnel/(\S+)", path)
        print ">>> path: ", path
        # print "||| ref_match: ", ref_match

        if tunnel_path_match and not ref_match:
            tunnel = tunnel_path_match.groups()[0]
            print ">>> tunnel: ", tunnel
            base = re.search("://(\S+)(\Z|/)", tunnel).groups()[0]
            print ">>> base: ", base
            r = requests.get(tunnel)
            # return self.request.sendall(r.content.replace(base, "http://"+host+"/tunnel/"+base))
            return self.request.sendall(r.content.replace(tunnel, "//"+host+"/tunnel/"+tunnel))

        if ref_match:
            ref = ref_match.groups()[0]
            print ">>> ref: ", ref
            tunnel_ref_match = re.search("/tunnel/(\S+)", ref)

            if tunnel_ref_match:
                tunnel = tunnel_ref_match.groups()[0]
                target = re.search("/tunnel/(\S+)", path).groups()[0]
                print ">>> tunnel: ", tunnel
                print ">>> getting target: ", target

                r = requests.get(target, headers={"Referer": tunnel, "Cookie": self.cookie})
                print ">>> response: ", r.status_code

                return self.request.sendall(r.content.replace(tunnel, "//"+host+"/tunnel/"+tunnel))
                # return self.request.sendall(r.content)

        return self.request.sendall(self.data.upper())

        # print r.raw, r.encoding
        # just send back the same data, but upper-cased
        # self.request.sendall(r.content)

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
