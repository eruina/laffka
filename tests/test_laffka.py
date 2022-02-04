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
        self.add_hidden_item()

    def dispatch(self, url):
        self.rv = self.app.get(url, follow_redirects=True)
        self.tree = html.fromstring(self.rv.data)

    def postDispatch(self, url, data):
        self.rv = self.app.post(url, data=data, follow_redirects=True)
        self.tree = html.fromstring(self.rv.data)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(configuration.Configuration.database_url)

    def login(self, username, password):
        self.dispatch('/login')
        token = self.tree.xpath('//input[@id="csrf_token"]/@value')
        self.postDispatch('/login', dict(
            username=username,
            password=password,
            csrf_token=token))

    def logout(self):
        return self.dispatch('/logout')

    def set_session(self):
        admin_key=hashlib.sha224(configuration.Configuration.secret_key.encode('utf-8')).hexdigest()
        with self.app as c:
            with c.session_transaction() as sess:
                sess['adminkey'] = admin_key

    def add_item(self):
        self.set_session()
        self.postDispatch('/admin_item', dict(
            name='test item',
            price=1,
            avail=100,
            description='A truly <b>useless</b> stuff',
            index=1,
            pcs='1,5,10'
        ))

    def add_hidden_item(self):
        self.set_session()
        self.postDispatch('/admin_item', dict(
            name='hidden item',
            price=1,
            avail=0,
            description='A truly <b>invisible</b> stuff',
            index=2,
            pcs='1,5,10'
        ))

class LoginLogout(LaffkaTestCase):
    def testOnLoginSuccessShouldDisplayOrders(self):
        self.login('test', 'test')
        assert b'Orders' in self.rv.data

    def testOnLogoutShouldDisplayLogin(self):
        self.login('test', 'test')
        self.logout()
        assert b'Login' in self.rv.data

    def testOnLoginFailureShouldDisplayLogin(self):
        self.login('testx', 'test')
        assert b'Login' in self.rv.data
        self.login('test', 'testx')
        assert b'Login' in self.rv.data

class Homepage(LaffkaTestCase):
    def setUp(self):
        super().setUp()
        self.rv = self.app.get('/')

    def testShouldContainLinkToCart(self):
        assert b'href="/cart"' in self.rv.data

class ProductsPage(LaffkaTestCase):
    def setUp(self):
        super().setUp()
        self.dispatch('/products')

    def testItemIsPresentOnProductsPage(self):
        assert b'test item' in self.rv.data

    def testItemDetailsSelectorContains1and5and10(self):
        select = self.tree.xpath('//select//option/@value')
        self.assertEqual(['1','5','10'], select)

    def testAddToCart(self):
        submit = self.tree.xpath('//form[@action="/add"]/input[@type="submit"]/@value')
        self.assertIn('Add to cart', submit)

class ItemDetailsPage(LaffkaTestCase) :
    def setUp(self):
        super().setUp()
        self.dispatch('/item/1')

    def testItemOneDescriptionIsUselessStuffWithHtml(self):
        self.assertIn(b'A truly <b>useless</b> stuff',self.rv.data)

    def testItemDetailsSelectorContains1and5and10(self):
        select = self.tree.xpath('//select//option/@value')
        self.assertEqual(['1','5','10'], select)

    def testAddToCart(self):
        submit = self.tree.xpath('//form[@action="/add"]/input[@type="submit"]/@value')
        self.assertIn('Add to cart', submit)

class CartTestCase(LaffkaTestCase):
    def setUp(self):
        super().setUp()
        self.postDispatch('/add', dict(
            item=1,
            quantity=5,
        ))
        self.dispatch('/cart')

class CartPageTest(CartTestCase):
    def testQtyInCartShouldBeFive(self):
        self.assertEqual(['5'], self.tree.xpath('//td[@id="quantity"]/text()'))

    def testShouldContainsRemoveItemLink(self):
        self.assertEqual(['/delete/1'], self.tree.xpath('//a[@class="btnRemoveAction"]/@href'))

    def testShouldContainsLinkToHomepage(self):
        self.assertIsNotNone(self.tree.xpath('//a[@href="/"]'))

    def testTotalShouldBeFive(self):
        self.assertEqual(['5.0'], self.tree.xpath('//td[@class="total_price"]/text()'))
        
if __name__ == '__main__':
    unittest.main()
