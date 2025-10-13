import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_project.settings')

app = Celery('weather_project')

# Load Django settings for Celery with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Use Redis URL from environment variable or default
REDIS_URL = os.environ.get(
    'REDIS_URL',
    'redis://default:jdBZQLOnJFfLuSKEFhuGDpewnjyvJMKp@ballast.proxy.rlwy.net:36272'
)

app.conf.broker_url = REDIS_URL
app.conf.result_backend = REDIS_URL

app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# Auto-discover tasks.py in installed apps
app.autodiscover_tasks()
