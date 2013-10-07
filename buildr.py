from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

from docker import Client
from celery import Celery
from tasks import build, push

import redis
import json

#import config
import config.flask_settings

app = Flask(__name__)
app.config.from_object('config.flask_settings')
app.config.from_envvar('BUILDR_FLASK_CONFIG', silent=True)

app.redis = redis.Redis('localhost')

ec = Client(base_url='unix://var/run/docker.sock', version='1.5')

def add_task(r, job_id):
    key = r.lpush("job_list", 'celery-task-meta-%s' % job_id)
    r.ltrim('job_list', 0, 99)
    return key

def ret_tasks(r):
    return r.lrange('job_list', 0, -1)

@app.route('/')
def show_index():
    jobs = ret_tasks(app.redis)

    return render_template('index.html', jobs=jobs)

@app.route('/images')
def show_images():
    images = ec.images()
    return render_template('images.html', images=images)

@app.route('/containers')
def show_containers():
    req = request.args.get('all', '')
    if req:
        containers = ec.containers(all=True)
    else:
        containers = ec.containers(all=False)

    return render_template('containers.html', containers=containers)

@app.route('/api/image/remove', methods=['POST'])
def image_remove():
    image = request.form['repo']
    if not image:
        flash("Empty image name", 'error')
    else:
        res = ec.remove_image(image)
        flash("Removed image: %s" % image, 'success')


    return redirect(url_for('show_images'))

@app.route('/api/container/remove', methods=['POST'])
def container_remove():
    container = request.form['cid']
    if not container:
        flash("Empty container id", 'error')
    else:
        res = ec.remove_container(container)
        flash("Removed container: %s" % container, 'success')

    return redirect(url_for('show_containers'))

@app.route('/payload', methods=['POST'])
def start_build():
    payload = json.loads(request.form['payload'])
    if not payload:
        abort(400)
    elif payload['repository']['name'] is not app.config['RS_REPO']:
        abort(401)

    res = build(app.config['RS_REPO_URL'], app.config['RS_TAG'])
    key = add_task(app.redis, res)
    
    flash("Task added: job:%s" % key, 'info')

    return redirect(url_for('show_index'))

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0')