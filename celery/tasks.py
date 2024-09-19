from celery import Celery
import subprocess

app = Celery('tasks', broker='redis://redis:6379/0')


@app.task
def scrape_news():
    subprocess.run(['scrapy', 'crawl', 'news_spider'])

# celery/tasks.py
