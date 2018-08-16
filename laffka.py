#!/usr/bin/env python3
from app import app
from waitress import serve
from app.configuration import Configuration
if Configuration.btc_master_key=='':
    quit('Please edit app/configuration.py')

#Switch between waitress and development flask, if debugging/port not set, serving development on 5000
try:
    if Configuration.debugging==True:
        app.run(host='127.0.0.1',port=Configuration.port)
    else:
        serve(app,host='127.0.0.1', port=Configuration.port)
except AttributeError:
    serve(app, host='127.0.0.1', port=5000)