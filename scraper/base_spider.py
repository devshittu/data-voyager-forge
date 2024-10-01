import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy_redis.spiders import RedisSpider
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time


class BaseSpider(RedisSpider):
    # Use Redis for request storage and scheduling
    redis_key = 'scraper:start_urls'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': 800,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
        },
        'RETRY_TIMES': 5,
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'REDIS_START_URLS_AS_SET': True,  # Avoid duplicates in Redis
    }

    def parse(self, response):
        raise NotImplementedError("Subclasses must implement parse method")

    def parse_infinite_scroll(self, response):
        driver = response.meta['driver']
        self.logger.info("Starting infinite scroll parsing")
        scroll_pause_time = 1
        max_scroll_attempts = 50
        scroll_attempt = 0
        last_height = driver.execute_script(
            "return document.body.scrollHeight")

        while scroll_attempt < max_scroll_attempts:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempt += 1
                self.logger.debug(
                    f"No new content after scrolling, attempt {scroll_attempt}")
            else:
                scroll_attempt = 0
                last_height = new_height

        html = driver.page_source
        response = scrapy.Selector(text=html)
        self.parse(response)

    def extract_content(self, response):
        items = {}
        items['title'] = response.css(
            'h1::text, h2::text, h3::text').get(default='').strip()
        items['content'] = ' '.join(response.css(
            'p::text, div.content::text, article::text').getall()).strip()
        items['images'] = response.css('img::attr(src)').getall()
        items['videos'] = response.css(
            'video::attr(src), iframe::attr(src)').getall()
        items['url'] = response.url
        items['date'] = response.css(
            'time::attr(datetime), span.date::text').get(default='').strip()
        items['metadata'] = {
            'author': response.css('span.author::text, a[rel="author"]::text').get(default='').strip(),
            'tags': response.css('a[rel="tag"]::text').getall(),
            'categories': response.css('a[rel="category tag"]::text').getall(),
        }
        return items

    def parse_pagination(self, response, callback=None):
        next_page = response.css(
            'a.next::attr(href), a.next-page::attr(href), li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback or self.parse)

# scraper/base_spider.py
