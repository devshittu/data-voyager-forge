# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


import scrapy


class ScraperItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    images = scrapy.Field()
    videos = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    metadata = scrapy.Field()
