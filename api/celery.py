# import os
# from celery import Celery
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_project.settings')
#
# app = Celery('weather_project')
#
# app.config_from_object('django.conf:settings', namespace='CELERY')
#
# # connect to redis.io free db
# app.conf.broker_url = (
#     os.environ.get('REDIS_URL', 'redis://redis-15101.c328.europe-west3-1.gce.redns.redis-cloud.com:15101/0'))
# app.conf.result_backend = (
#     os.environ.get('REDIS_URL', 'redis://redis-15101.c328.europe-west3-1.gce.redns.redis-cloud.com:15101/0'))
# app.conf.task_serializer = 'json'
# app.conf.result_serializer = 'json'
# app.conf.accept_content = ['json']
#
# app.autodiscover_tasks()