from flask import Flask, session
import app.bitcoin
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app import configuration
from waitress import serve

database=app.db.Database()
bitcoin_object=app.bitcoin.Bitcoin()

#cron jobs described later
def update_rate():
    bitcoin_object.update_btc_rate()
def update_orders():
    bitcoin_object.update_txs()

scheduler =BackgroundScheduler()
scheduler.start()

#update_rate
scheduler.add_job(
    func=update_rate,
    trigger=IntervalTrigger(seconds=app.configuration.Configuration.update_rate_sec),
    id='update btc rate',
    name='update btc rate',
    replace_existing=True
)
#update_orders
scheduler.add_job(
    func=update_orders,
    trigger=IntervalTrigger(seconds=app.configuration.Configuration.update_tx_sec),
    id='update_orders',
    name='update orders',
    replace_existing=True
)

atexit.register(lambda : scheduler.shutdown())

app =Flask(__name__)
app.config['WTF_CSRF_ENABLED']=configuration.Configuration.wtf_csrf
app.config['SECRET_KEY']=configuration.Configuration.secret_key

from app import routes
