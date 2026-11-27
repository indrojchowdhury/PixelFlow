import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Read every setting that starts with CELERY_ from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Find tasks.py inside every app listed in INSTALLED_APPS
app.autodiscover_tasks()