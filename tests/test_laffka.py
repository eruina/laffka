import os
import laffka
import unittest
import tempfile
import hashlib
from lxml import html
from app import configuration
from app import db

class LaffkaTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, configuration.Configuration.database_url = tempfile.mkstemp()
        self.app = laffka.app.test_client()
        self.app.testing=True
        database = db.Database()
        database.init_db()
        self.add_item()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(configuration.Configuration.database_url)
        
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

    def set_session(self):
        admin_key=hashlib.sha224(configuration.Configuration.secret_key.encode('utf-8')).hexdigest()
        with self.app as c:
            with c.session_transaction() as sess:
                sess['adminkey'] = admin_key

    def add_item(self):
        self.set_session()
        rv = self.app.post('/admin_item', data=dict(
            name='test item',
            price=1,
            avail=-1,
            description='A truly <b>useless</b> stuff',
            index=1,
            pcs='1,5,10'
        ), follow_redirects=True)

class LoginLogout(LaffkaTestCase):
    def onLoginSuccessShouldDisplayOrders(self):
        rv = self.login('test', 'test')
        assert b'Orders' in rv.data

    def onLogoutShouldDisplayLogin(self):
        self.login('test', 'test')
        rv = self.logout()
        assert b'Login' in rv.data

    def onLoginFailureShouldDisplayLogin(self):
        rv = self.login('testx', 'test')
        assert b'Login' in rv.data
        rv = self.login('test', 'testx')
        assert b'Login' in rv.data

class Homepage(LaffkaTestCase):
    def testItemIsPresentOnHomepage(self):
        rv = self.app.get('/')
        assert b'test item' in rv.data

class ItemDetailsPage(LaffkaTestCase) :
    def setUp(self):
        super().setUp()
        self.rv = self.app.get('/item/1')
        self.tree = html.fromstring(self.rv.data)
        
    def testItemOneDescriptionIsUselessStuffWithHtml(self):
        assert b'A truly <b>useless</b> stuff' in self.rv.data

    def testItemDetailsSelectorContains1and5and10(self):
        select = self.tree.xpath('//select//option/@value')
        assert select == ['1','5','10']

    def testAddToCart(self):
        submit = self.tree.xpath('//form//input[type="submit"]')
        assert b'Add to cart' in submit
    
if __name__ == '__main__':
    unittest.main()