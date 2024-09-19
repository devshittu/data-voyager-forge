from elasticsearch_dsl import (Search,
                               Document, Text, Date, connections, analyzer, tokenizer)
from newspaper import Article
from scrapy_redis.spiders import RedisSpider
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class NewsSpiderSpider(CrawlSpider):
    name = "news_spider"
    allowed_domains = ["mydomain.com"]
    start_urls = ["https://mydomain.com"]

    rules = (Rule(LinkExtractor(allow=r"Items/"), callback="parse_item", follow=True),)

    def parse_item(self, response):
        item = {}
        #item["domain_id"] = response.xpath('//input[@id="sid"]/@value').get()
        #item["name"] = response.xpath('//div[@id="name"]').get()
        #item["description"] = response.xpath('//div[@id="description"]').get()
        return item


# Define an Elasticsearch DSL document for the articles

# Define a custom analyzer (optional)
# my_analyzer = analyzer('custom_analyzer',
#                        tokenizer=tokenizer('standard'),
#                        filter=['lowercase', 'stop', 'snowball']
#                        )


# class ArticleDocument(Document):
#     title = Text(analyzer='snowball')  # Use snowball analyzer for title
#     text = Text(analyzer=my_analyzer)  # Use custom analyzer for text
#     published_date = Date()
#     author = Text()
#     url = Text()

#     class Index:
#         name = 'articles'  # Define the index name


# # Connect to the Elasticsearch instance
# connections.create_connection(hosts=['elasticsearch:9200'])


# class NewsSpider(RedisSpider):
#     name = 'news_spider'
#     redis_key = 'news:start_urls'

#     def parse(self, response):
#         # Extract article links from the page
#         article_links = response.css('a::attr(href)').getall()
#         for link in article_links:
#             if '/article/' in link:
#                 yield response.follow(link, self.parse_article)

#     def parse_article(self, response):
#         # Use Newspaper3k to extract article content
#         article = Article(response.url)
#         article.download()
#         article.parse()

#         # Create an ArticleDocument object for Elasticsearch
#         article_doc = ArticleDocument(
#             title=article.title,
#             text=article.text,
#             published_date=article.publish_date,
#             author=article.authors,
#             url=response.url
#         )

#         # Save the document to Elasticsearch
#         article_doc.save()

#         yield {
#             'title': article.title,
#             'text': article.text,
#             'published_date': article.publish_date,
#             'author': article.authors,
#             'url': response.url
#         }
