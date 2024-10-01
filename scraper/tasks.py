from celery_app import app
from scraper.spiders.aggressive_spider import AggressiveSpider
from cms_detector import CMSDetector
import logging
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from celery_app import Celery
import subprocess
import redis

app = Celery('tasks', broker='redis://redis:6379/0')


@app.task
def scrape_news():
    # Example task
    subprocess.run(['scrapy', 'crawl', 'news_spider'])
    print("Scraping news...")


@app.task
def run_all_scrapers():
    logger = logging.getLogger('run_all_scrapers')
    logger.info("Starting scraping task")

    websites = [
        'https://naijaloaded.com.ng',
        'https://naijapals.com',
        # Add more websites as needed
    ]

    settings = get_project_settings()
    process = CrawlerProcess(settings)

    for site in websites:
        logger.info(f"Running aggressive spider for {site}")
        process.crawl(AggressiveSpider, start_urls=[site], allowed_domains=[
                      site.replace('https://', '').replace('http://', '').split('/')[0]])

    process.start(stop_after_crawl=False)


@app.task
def enqueue_urls():
    redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
    websites = [
        'https://naijaloaded.com.ng',
        'https://naijapals.com',
        # Add more websites as needed
    ]

    for url in websites:
        redis_client.sadd('scraper:start_urls', url)  # Enqueue the start URLs

# scraper/tasks.py
