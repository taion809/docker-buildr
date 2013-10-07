from os import environ

#this sucks for testing, make it better later.
CELERY_BROKER_URL = "amqp://localhost:5672",
CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tokyo'
CELERY_ENABLE_UTC = True