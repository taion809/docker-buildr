from __future__ import absolute_import
from celery import Celery
from docker import Client

celery = Celery('tasks')

celery.config_from_object('celery_config')

dc = Client(base_url='unix://var/run/docker.sock', version='1.5')

@celery.task(name='tasks.build')
def build(repo, tag):
    return dc.build(repo, tag)

@celery.task(name='tasks.push')
def push(repository):
    return dc.push(repository)

@celery.task(name='tasks.rmi')
def rmi(repository):
    return dc.remove_image(repository)

@celery.task(name='tasks.rm')
def rm(container):
    return dc.remove_container(container)

if __name__ == '__main__':
    celery.start()