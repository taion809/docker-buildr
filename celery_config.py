from os import environ

#this sucks for testing, make it better later.
CELERY_BROKER_URL= environ['CELERY_BROKER_URL'] or "amqp://localhost:5672",
CELERY_RESULT_BACKEND= environ['CELERY_RESULT_BACKEND'] or "redis://localhost:6379"
CELERY_TASK_SERIALIZER= environ['CELERY_TASK_SERIALIZER'] or 'json'
CELERY_RESULT_SERIALIZER= environ['CELERY_RESULT_SERIALIZER'] or 'json'
CELERY_TIMEZONE= environ['CELERY_TIMEZONE'] or 'Asia/Tokyo'
CELERY_ENABLE_UTC= environ['CELERY_ENABLE_UTC'] or True