# scraper/spiders/aggressive_spider.py

from ..base_spider import BaseSpider
from scrapy_selenium import SeleniumRequest
from ..items import ScraperItem
import logging


class AggressiveSpider(BaseSpider):
    name = 'aggressive_spider'

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url, callback=self.parse_page, wait_time=10, screenshot=False)

    def parse(self, response):
        self.logger.info(f"Parsing page: {response.url}")
        yield from self.extract_articles(response)
        yield from self.follow_links(response)
        yield from self.handle_pagination(response)
        yield from self.handle_infinite_scroll(response)

    def parse_page(self, response):
        self.logger.info(f"Parsing page: {response.url}")
        # Try multiple methods to extract content
        yield from self.extract_articles(response)
        yield from self.follow_links(response)
        yield from self.handle_pagination(response)
        yield from self.handle_infinite_scroll(response)

    def extract_articles(self, response):
        articles = response.css('article') or response.xpath(
            '//div[contains(@class, "post")]')
        for article in articles:
            item = self.extract_content(article)
            yield item

    def extract_articles(self, response):
        articles_selectors = [
            '//article',
            '//div[contains(@class, "post")]',
            '//div[contains(@class, "entry")]',
            '//div[contains(@class, "content")]',
        ]

        for selector in articles_selectors:
            articles = response.xpath(selector)
            if articles:
                self.logger.debug(f"Found articles using selector: {selector}")
                for article in articles:
                    item = ScraperItem()
                    item['title'] = article.xpath(
                        './/h1//text() | .//h2//text()').get(default='').strip()
                    item['content'] = ' '.join(article.xpath(
                        './/p//text() | .//div//text()').getall()).strip()
                    item['images'] = article.xpath('.//img/@src').getall()
                    item['videos'] = article.xpath(
                        './/video/@src | .//iframe/@src').getall()
                    item['date'] = article.xpath(
                        './/time/@datetime | .//span[contains(@class, "date")]//text()').get(default='').strip()
                    item['url'] = response.url
                    item['metadata'] = {
                        'author': article.xpath('.//span[contains(@class, "author")]//text() | .//a[contains(@rel, "author")]//text()').get(default='').strip(),
                        'tags': article.xpath('.//a[contains(@rel, "tag")]//text()').getall(),
                    }
                    yield item
                break

    def follow_links(self, response):
        links = response.css('a::attr(href)').getall()
        for link in links:
            if self.is_valid_link(link):
                yield SeleniumRequest(url=link, callback=self.parse_page)

    def is_valid_link(self, link):
        if link.startswith('http') and self.allowed_domains[0] not in link:
            return False
        if 'login' in link or 'signup' in link:
            return False
        return True

    def handle_pagination(self, response):
        next_page = response.css(
            'a.next::attr(href), a.next-page::attr(href), li.next a::attr(href)').get()
        if next_page:
            self.logger.debug(
                f"Following pagination to next page: {next_page}")
            yield response.follow(next_page, self.parse_page)

    def handle_infinite_scroll(self, response):
        # If infinite scroll is detected, handle it
        if 'infinite-scroll' in response.text.lower():
            self.logger.debug(
                "Infinite scroll detected, invoking parse_infinite_scroll")
            yield SeleniumRequest(url=response.url, callback=self.parse_infinite_scroll, wait_time=10, screenshot=False)
