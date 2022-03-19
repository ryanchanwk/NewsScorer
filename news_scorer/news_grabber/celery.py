import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_grabber.settings')

app = Celery('news_grabber')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
