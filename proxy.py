from cookielib import CookieJar
from pprint import pformat
import re
from urlparse import urlsplit, urlunsplit
import requests
from twisted.internet import reactor, threads
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent, CookieAgent, RedirectAgent
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
from tunneler import replace_links


cj = CookieJar()

def errback(err):
    print ">>> error", err.value, err.type
    print pformat(err.stack)
    print pformat(err.frames)


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

    @property
    def target_base(self):
        p = urlsplit(self.target)

        return urlunsplit((p.scheme, p.netloc, '', '', ''))

    def render_POST(self, request):
        self.tr = request
        return self.async_request('POST', request.args)

    def render_GET(self, request):
        self.tr = request
        return self.async_request('GET', request.args)

    def get_body(self, response):
        global cj
        # print ">>> get_body response: %d\n" % response.code
        # print ">>> get_body cookies: %s\n" % [c for c in cj]
        # print ">>> get_body headers: ", {(h[0], h[1]) for h in response.headers.getAllRawHeaders()}
        self.headers = {k: v[0] for k,v in response.headers.getAllRawHeaders()}
        # print ">>> get_body headers: %s\n" % self.headers

        # this will provide correct target_base for links replacement
        # if there were any redirects
        if 'Location' in self.headers:
            self.target = self.headers['Location']
            return self.async_request('GET')

        finished = Deferred()
        finished.addCallback(self.render_content)
        finished.addErrback(errback)
        return response.deliverBody(BeginningPrinter(finished))

    def async_request(self, method, data=None):
        global cj
        # agent = CookieAgent(RedirectAgent(Agent(reactor)), cj)
        agent = CookieAgent(Agent(reactor), cj)

        print ">>> request %s %s\n" % (method, self.target)
        # print ">>> cookies: %s\n" % cj
        # print ">>> data: %s\n" % data

        from twisted.web.http_headers import Headers
        body = ""

        if data:
            body = "&".join("%s=%s" % (k, v[0]) for k,v in data.items())

        # print ">>> body: %s\n" % body

        d = agent.request(method, self.target, Headers({}), StringProducer(body))
        d.addCallback(self.get_body)
        d.addErrback(errback)

        return NOT_DONE_YET

    def render_content(self, body):
        if not body:
            return

        global cookies

        print ">>> render %s\n" % self.target

        for k,v in self.headers.items():
            if k in ['Content-Type', 'Content-Length']:
                self.tr.setHeader(k, v)

        # replace links only in html content
        if 'cache.html' in self.target or not re.search("(javascript|css|html)", self.headers['Content-Type']):
            self.tr.write(body)
            return self.tr.finish()

        # make sure content-length is corrent for encoded content
        content = replace_links(body, self.client_host, self.target_base) #.encode('utf-8')
        self.tr.setHeader('content-length', len(content))
        self.tr.write(content)
        self.tr.finish()


class RegularView(Resource):
    isLeaf = True

    def render_GET(self, request):
        return "<html><body><pre>%s</pre></body></html>" % request.path


class BeginningPrinter(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.data = ""

    def dataReceived(self, bytes):
        self.data += bytes

    def connectionLost(self, reason):
        self.finished.callback(self.data)


from zope.interface import implements

from twisted.internet.defer import succeed
from twisted.web.iweb import IBodyProducer

class StringProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def stopProducing(self):
        pass

    def resumeProducing(self):
        pass

    def pauseProducing(self):
        pass

root = Dispatch()
factory = Site(root)
print ">>> running on 127.0.0.1:8880"
reactor.listenTCP(8880, factory)
reactor.run()
