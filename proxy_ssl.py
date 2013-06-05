import ssl
from OpenSSL import SSL
import requests
from cookielib import CookieJar, Cookie
from twisted.internet import reactor
from twisted.python import log
from twisted.web.client import Agent, CookieAgent, RedirectAgent
from twisted.web.http_headers import Headers
from twisted.internet.ssl import ClientContextFactory
from twisted.internet.defer import Deferred, succeed
from twisted.web.iweb import IBodyProducer
from zope.interface import implements
from twisted.internet.protocol import Protocol


class BeginningPrinter(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.data = ""

    def dataReceived(self, bytes):
        self.data += bytes

    def connectionLost(self, reason):
        print 'Finished receiving body:', reason.type, reason.value
        self.finished.callback(self.data)


def printBody(body):
    print ">>> body:", body

def getBody(response):
    print ">>>", response, response.code
    finished = Deferred()
    finished.addCallback(printBody)
    finished.addErrback(log.err)
    response.deliverBody(BeginningPrinter(finished))
    return finished

def response(resp):
    print ">>> got response:", resp

class WebClientContextFactory(ClientContextFactory):
    def verifyHost(self, connection, x509, errno, depth, ok):
        if not ok:
            print 'invalid cert from subject:', x509.get_subject()
            return True

        print ">>> verifyHost fine:", errno, depth, ok
        return True

    def getContext(self, hostname, port):
        print ">>> getContext", hostname, port
        ctx = ClientContextFactory.getContext(self)
        ctx.set_verify(SSL.VERIFY_NONE, self.verifyHost)
        return ctx


def main():
    c = Cookie(None, 'sid', '157272379', '443', '443', "10.0.199.8", None, None, '/', None, False, False, 'TestCookie', None, None, None)

    cj = CookieJar()
    cj.set_cookie(c)

    print ">>> cj:", cj

    contextFactory = WebClientContextFactory()
    agent = CookieAgent(RedirectAgent(Agent(reactor, contextFactory)), cj)

    d = agent.request('GET', 'https://10.0.199.8/datetime_get_request_periodic')

    d.addCallbacks(getBody, log.err)
    d.addCallback(lambda x: reactor.stop())
    reactor.run()


if __name__ == "__main__":
    # r = requests.get('https://10.0.199.8/datetime_get_request_periodic', cookies={'sid': '157272379'}, verify=False)
    # print ">>>", r.history, r.url, r.text

    main()
