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

def ret_tasks(r, start=0, end=-1):
#    return r.lrange('job_list', 0, -1)
    job_list = r.lrange('job_list', start, end)
    jobs = []
    for j in job_list:
        if j is not None:
            print j
            o = json.loads(r.get(j))
            jobs.append({j: o})

    return list(enumerate(jobs))

@app.route('/')
def show_index():
    jobs = ret_tasks(app.redis)
    print jobs
    return render_template('index.html', jobs=jobs)

@app.route('/details/<int:job_id>')
def show_details(job_id):
    job = ret_tasks(app.redis, job_id, job_id).pop()

    return render_template('details.html', job=job)

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

    res = build.delay(repo=app.config['RS_REPO_URL'], tag=app.config['RS_TAG'])
    key = add_task(app.redis, res)
    
    flash("Task added: job:%s" % key, 'info')

    return redirect(url_for('show_index'))

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0')
