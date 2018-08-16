import json
import requests
#import electrum
import app.db
from app import configuration
class Bitcoin:
    btc_eur = ...  # type: object

    def __init__(self):
        self.get_rate()
    def update_txs(self):
        '''
        update trasnactions stored in database (paid status)
        :return:
        '''
        database=app.db.Database()
        import time
        cut_off = int(time.time()) - configuration.Configuration.check_cutoff
        txes=database.get_orders(cut_off)
        for tx in txes:
            r=requests.get(configuration.Configuration.tx_url+tx.btc_address)
            cash=int(r.content)/(100000000)
            if tx.paid!=cash:
                database.update_paid(tx.btc_address,cash)

    def update_btc_rate(self):
        '''
        Updates btc exchange rate to self.object and call on update
        :return:
        '''
        r = requests.get('https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=EUR')
        data = r.json()
        self.btc_eur = (data['EUR'])
        self.db_update()
    def db_update(self):
        '''
        Calls on database update for rate
        :return:
        '''
        database = app.db.Database()
        database.update_btc_rate(self.btc_eur)
    def get_rate(self):
        '''
        Returns btc rate
        :return:
        '''
        database=app.db.Database()
        database.db_cursor.execute('SELECT * FROM btc')
        self.btc_eur=database.db_cursor.fetchone()[0]
    class order:
        '''
        Order class
        '''
        address=''
        address_salt=''
        wif_key=''
        private_key=''
        order_index=-1
        paid=False
        btc_address=''
        def __init__(self,item_index,address,adress_salt,item_amount,order_price):
            database=app.db.Database()
            from bitmerchant.wallet import Wallet
            if configuration.Configuration.btc_net=="Test":
                from bitmerchant.network import BitcoinTestNet
                wallet = Wallet.from_master_secret(configuration.Configuration.btc_master_key,network=BitcoinTestNet)
            else:
                from bitmerchant.network import BitcoinMainNet
                wallet = Wallet.from_master_secret(configuration.Configuration.btc_master_key,network=BitcoinMainNet)
            self.order_index=database.make_order(item_index,address,adress_salt,item_amount,order_price)
            child_wallet = wallet.get_child(self.order_index, is_prime=False)
            self.wif_key=child_wallet.export_to_wif()
            self.btc_address=child_wallet.to_address()
            self.private_key=child_wallet.get_private_key_hex()
            database.update_order(self.order_index,self.wif_key,self.btc_address,self.private_key)
            #update and make order can be joined


