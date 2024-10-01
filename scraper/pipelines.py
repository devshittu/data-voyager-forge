# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from elasticsearch import Elasticsearch, exceptions as es_exceptions
import logging
from itemadapter import ItemAdapter


class ScraperPipeline:
    def process_item(self, item, spider):
        return item

# scraper/pipelines.py


class ElasticsearchPipeline:
    def __init__(self):
        self.es = Elasticsearch(['http://elasticsearch:9200'])
        self.index_name = 'scraped_content'
        self.logger = logging.getLogger(__name__)

    def process_item(self, item, spider):
        try:
            self.es.index(index=self.index_name, body=dict(item))
            self.logger.info(
                f"Indexed item to Elasticsearch: {item.get('url', 'N/A')}")
        except es_exceptions.ConnectionError as e:
            self.logger.error(f"Elasticsearch connection error: {e}")
        except Exception as e:
            self.logger.error(f"Error indexing item: {e}")
        return item
