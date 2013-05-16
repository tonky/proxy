from nose.tools import ok_
from tunneler import replace_links


class TestTunneler():
    def setUp(self):
        self.content = """
<html>
target home
<a href="/links">target relative links</a>
<a href='http://localhost:9000/links'>target absolute links</a>
<form accept-charset="UTF-8" action='/admin/' method='post' id='login-form'>
<input type='hidden' name='csrfmiddlewaretoken' value='UHgzrXl1EmbuPVxIobyk9BJPwBIC5t69' />
</form>
<a href='http://localhost:9000/links'>target absolute links</a>
<img class="graph-loading dots" src="/images/spinners/octocat-spinner-128.gif" width="64">
<SCRIPT src = '/acd_common.js' language="JavaScript" type="text/javascript"> </SCRIPT>
<FORM NAME="accedian_login" ACTION=/login METHOD=POST>
document.writeln("<FORM action=goform/g8032_clear?idx=")
<link rel="xhr-socket" href='/_sockets' />
background:url('/media/static/images/content-bg-middle.png?2b35c60e7ed0')
<a href='/admin'>target admin</a>
<link href="default.css">
["/radius_cfg.asp", "RADIUS"]
indexOf("["+menu_id+"]")==-1
<img alt="Communicate" src="https://a248.e.akamai.net/assets.github.com/images/modules/home/communicate.png?1360648847" />

"""

    def test_replace_links(self):
        new_body = replace_links(self.content, 'http://localhost:8000/tunnel', 'http://localhost:9000')
        print new_body
        ok_("<a href='http://localhost:8000/tunnel/http://localhost:9000/links'>target absolute links</a>" in new_body)
        ok_('<a href="http://localhost:8000/tunnel/http://localhost:9000/links">target relative links</a>' in new_body)
        ok_("<a href='http://localhost:8000/tunnel/http://localhost:9000/admin'>target admin</a>" in new_body)
        ok_("action='http://localhost:8000/tunnel/http://localhost:9000/admin/' method='post'" in new_body)
        ok_('src="http://localhost:8000/tunnel/http://localhost:9000/images/spinners/octocat-spinner-128.gif"' in new_body)
        ok_("href='http://localhost:8000/tunnel/http://localhost:9000/_sockets'" in new_body)
        ok_("<SCRIPT src='http://localhost:8000/tunnel/http://localhost:9000/acd_common.js' language=\"JavaScript\"" in new_body)
        ok_('<FORM NAME="accedian_login" ACTION="http://localhost:8000/tunnel/http://localhost:9000/login" METHOD=POST>' in new_body)
        ok_('<FORM action=goform/g8032_clear?idx=' in new_body)
        ok_("background:url('http://localhost:8000/tunnel/http://localhost:9000/media/static/images/content-bg-middle.png?2b35c60e7ed0')" in new_body)
        ok_('["http://localhost:8000/tunnel/http://localhost:9000/radius_cfg.asp", "RADIUS"]' in new_body)
        ok_('indexOf("["+menu_id+"]")==-1' in new_body)
        ok_('"http://localhost:8000/tunnel/http://localhost:9000/default.css"' in new_body)
        ok_('src="https://a248.e' in new_body)
