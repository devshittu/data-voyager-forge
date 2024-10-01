from celery import Celery
from celery.schedules import crontab

# Initialize Celery
app = Celery(
    'scraper',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
    include=['scraper.tasks']
)

# Optionally configure Celery settings
app.conf.update(
    result_expires=3600,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

app.conf.beat_schedule = {
    'run-scrapers-every-15-minutes': {
        'task': 'tasks.run_all_scrapers',
        'schedule': crontab(minute='*/15'),
    },
}

app.conf.timezone = 'UTC'

# celery_app.py
