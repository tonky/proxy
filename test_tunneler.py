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
<link rel="xhr-socket" href='/_sockets' />
<a href='/admin'>target admin</a>
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
