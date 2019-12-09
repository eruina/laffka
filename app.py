#!/usr/bin/python3

import os

from flask import Flask
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config['REDIS_URL'] = 'redis://redis:6379/0'

redis = FlaskRedis(app)


@app.route('/')
def counter():
    return '{0} {1} {2}'.format('Hello! You have visited me:',str(redis.incr('web2_counter')),' times.')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
