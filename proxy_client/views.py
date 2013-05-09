import re
from urlparse import urlsplit, urlunsplit
from django.http import HttpResponse
import requests
import settings
from tunneler import replace_links


# tunnel the request. the client holds cookies and sends them with each request,
# adding headers and using appropriate method and scheme
def tunnel(request, target_url):
    # figure out the scheme and url for the tunnel, used to replace all the 
    # links in the target html
    scheme = "http"

    if request.is_secure():
        scheme = "https"

    tunnel_base = "%s://%s/%s" % (scheme, request.get_host(), "tunnel")

    # get the base url of the target, so we could rewrite relative links with it
    p = urlsplit(target_url)
    target_base = urlunsplit((p.scheme, p.netloc, '', '', ''))

    if request.method == 'GET':
        r = requests.get(target_url, cookies=settings.cookies, data=request.GET.dict())
    else:
        r = requests.post(target_url, cookies=settings.cookies, data=request.POST.dict())

    # make sure to store cookies if we get them, to reuse when actually returning
    # the page to the browser, usually login state and session id is stored there
    if dict(r.cookies):
        settings.cookies = dict(r.cookies)

    content = r.content

    # replace links only in html content
    if re.search("html", r.headers['Content-Type']):
        content = replace_links(r.text, tunnel_base, target_base)

    resp = HttpResponse(content)

    # make sure browser gets correct CT for the tunneled files
    resp['Content-Type'] = r.headers['Content-Type']

    return resp

def home(request):
    return HttpResponse("""
<html>
client home <br/> <br/>
<a href="/links">client relative links</a> <br/>
<a href="http://localhost:8000/links">client absolute links</a> <br/>
<a href="/admin">client admin</a> <br/>
<a href="http://localhost:8000/tunnel/https://github.com">github</a> <br/>
</html>
""")

def links(request):
    return HttpResponse("""
Ok, links <br/> <br/>
<a href="/">client home</a> <br/>
<a href="/admin">client admin</a> <br/>
<a href="http://localhost:8000/tunnel/http://localhost:9000">target home</a> <br/>
<a href="http://localhost:8000/tunnel/http://localhost:9000/admin">target admin</a> <br/>
<a href="http://google.com">client google</a>
</html>
""")
