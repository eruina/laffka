import os
import laffka
import unittest
import tempfile
from lxml import html
from app import configuration
from app import db

class LaffkaTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, configuration.Configuration.database_url = tempfile.mkstemp()
        self.app = laffka.app.test_client()
        database = db.Database()
        database.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(configuration.Configuration.database_url)

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'Laffka' in rv.data
        
    def login(self, username, password):
        rv = self.app.get('/login')
        tree = html.fromstring(rv.data)
        token = tree.xpath('//input[@id="csrf_token"]/@value')
        return self.app.post('/login', data=dict(
            username=username,
            password=password,
            csrf_token=token
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('test', 'test')
        assert b'Orders' in rv.data
        rv = self.logout()
        assert b'Login' in rv.data
        rv = self.login('testx', 'test')
        assert b'Login' in rv.data
        rv = self.login('test', 'testx')
        assert b'Login' in rv.data

if __name__ == '__main__':
    unittest.main()
