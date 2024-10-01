# cms_detector.py

from Wappalyzer import Wappalyzer, WebPage
import redis
import logging


class CMSDetector:
    def __init__(self, redis_host='redis', redis_port=6379):
        self.wappalyzer = Wappalyzer.latest()
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)
        self.logger = logging.getLogger(__name__)

    def detect_cms(self, url):
        cached_cms = self.redis_client.get(url)
        if cached_cms:
            cms = cached_cms.decode('utf-8')
            self.logger.debug(f"CMS for {url} retrieved from cache: {cms}")
            return cms

        try:
            webpage = WebPage.new_from_url(url)
            technologies = self.wappalyzer.analyze_with_versions_and_categories(
                webpage)
            cms = self.extract_cms(technologies)
            self.redis_client.set(url, cms)
            self.logger.debug(f"CMS for {url} detected: {cms}")
            return cms
        except Exception as e:
            self.logger.error(f"Error detecting CMS for {url}: {e}")
            return 'generic'

    def extract_cms(self, technologies):
        cms_list = ['WordPress', 'Drupal', 'Joomla',
                    'Magento', 'Wix', 'Squarespace']
        for tech in technologies.keys():
            if tech in cms_list:
                return tech.lower()
        return 'generic'
