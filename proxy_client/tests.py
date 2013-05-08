from django.test import TestCase


class ClientTest(TestCase):
    def test_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('client home' in resp.content)

    def test_internal_links(self):
        resp = self.client.get('/tunnel/http://localhost:9000/links')
        print resp
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('target home' in resp.content)
        self.assertTrue('<a href="http://testserver/tunnel/http://localhost:9000/">target home</a>' in resp.content)

    def test_tunnel(self):
        resp = self.client.get('/tunnel/http://localhost:9000')
        print resp
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('target home' in resp.content)
        self.assertTrue('<a href="http://testserver/tunnel/http://localhost:9000/links">target relative links</a>' in resp.content)
