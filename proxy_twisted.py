import re
from urlparse import urlsplit, urlunsplit
import requests
from twisted.internet import reactor, threads
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
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
        return self.async_request(request, requests.post)

    def render_GET(self, request):
        return self.async_request(request, requests.get)

    def get_url(self, requests_method, data):
        global cookies

        result = requests_method(self.target, cookies=cookies, data=data, verify=False)

        return result

    def async_request(self, twisted_request, requests_method):
        def errback(err):
            print ">>> error", err.value, err.type, err.stack, err.frames

        # content = self.get_url(requests_method, twisted_request.args)
        # return self.render_content(content, twisted_request)

        d = threads.deferToThread(self.get_url, requests_method, twisted_request.args)
        d.addCallback(self.render_content, twisted_request)
        d.addErrback(errback)

        return NOT_DONE_YET

    def render_content(self, r, twisted_request):
        global cookies

        for k,v in r.headers.items():
            if k in ['content-type', 'content-length']:
                twisted_request.setHeader(k, v)

        # make sure to store cookies if we get them, to reuse when actually returning
        # the page to the browser, usually login state and session id is stored there
        if dict(r.cookies):
            cookies = dict(r.cookies)

        # replace links only in html content
        if 'cache.html' in self.target or not re.search("(javascript|css|html)", r.headers['Content-Type']):
            twisted_request.write(r.content)
            return twisted_request.finish()

        content = replace_links(r.text, self.client_host, self.target_base).encode('utf-8')
        twisted_request.setHeader('content-length', len(content))

        content = replace_links(r.text, self.client_host, self.target_base).encode('utf-8')
        twisted_request.setHeader('content-length', len(content))

        twisted_request.write(content)
        twisted_request.finish()


class RegularView(Resource):
    isLeaf = True

    def render_GET(self, request):
        return "<html><body><pre>%s</pre></body></html>" % request.path



root = Dispatch()
factory = Site(root)
reactor.listenTCP(8880, factory)
reactor.run()
