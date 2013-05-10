import re
from urlparse import urlsplit, urlunsplit
import requests
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site
from tunneler import replace_links


cookies = {}


class Dispatch(Resource):
    def getChild(self, name, request):
        scheme = "http"

        if request.isSecure():
            scheme = "https"

        tunnel_path_match = re.search("/tunnel/(\S+)", request.uri)

        if tunnel_path_match:
            client_host = "%s://%s:%d/tunnel" % (scheme, request.getHost().host, request.getHost().port)
            target = tunnel_path_match.groups()[0]

            return Tunnel(client_host, target)

        return RegularView()


class Tunnel(Resource):
    isLeaf = True

    def __init__(self, client_host, target):
        Resource.__init__(self)
        self.target = target
        self.client_host = client_host

        p = urlsplit(target)

        self.target_base = urlunsplit((p.scheme, p.netloc, '', '', ''))

    def render_POST(self, request):
        return self.render_request(request, requests.post)

    def render_GET(self, request):
        return self.render_request(request, requests.get)

    def render_request(self, twisted_request, requests_method):
        global cookies

        r = requests_method(self.target, cookies=cookies, data=twisted_request.args)

        for k,v in r.headers.items():
            if k in ['Content-Type', 'Content-Length']:
                twisted_request.setHeader(k, v)

        # make sure to store cookies if we get them, to reuse when actually returning
        # the page to the browser, usually login state and session id is stored there
        if dict(r.cookies):
            cookies = dict(r.cookies)

        # replace links only in html content
        if not re.search("html", r.headers['Content-Type']):
            return r.content

        content = replace_links(r.text, self.client_host, self.target_base)

        return content.encode('utf-8')


class RegularView(Resource):
    isLeaf = True

    def render_GET(self, request):
        return "<html><body><pre>%s</pre></body></html>" % request.path



root = Dispatch()
factory = Site(root)
reactor.listenTCP(8000, factory)
reactor.run()
