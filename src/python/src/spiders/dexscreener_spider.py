import scrapy

from rmq.utils.import_full_name import get_import_full_name
from items import ProjectItem
from pipelines import ProjectToDatabasePipeline

class DexScreenerSpider(scrapy.Spider):
    name = 'dexscreener'
    start_urls = ['https://dexscreener.com/?rankBy=volume&order=desc&maxAge=24']
    
    custom_settings = {
        "ITEM_PIPELINES": {
            get_import_full_name(ProjectToDatabasePipeline): 310,
        },
        'DNS_TIMEOUT': 10,
    }

    def parse(self, response):
        self.logger.info(f'Parsing response from {response.url}')
        
        # Print the first 1000 characters of the response body
        content = response.text[:1000]
        self.logger.info(f'Content (first 1000 characters): {content}')
