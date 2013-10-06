from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

from docker import Client
from celery import Celery
from tasks import build

import json

app = Flask(__name__)
app.config.from_object('flask_config')
app.config.from_envvar('BUILDR_CONFIG', silent=True)

dc = Client(base_url='unix://var/run/docker.sock', version='1.5')

@app.route('/')
def show_index():
    images = dc.containers()
    return render_template('index.html', images=images)

@app.route('/payload', methods=['POST'])
def start_build():
    payload = json.loads(request.form['payload'])
    if not payload:
        abort(400)
    elif payload['repository']['name'] is not app.config['RS_REPO']:
        abort(401)

    res = build()

if __name__ == '__main__':
    app.run('0.0.0.0')