import json
import re
import scrapy
from scrapy.http import Response
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet import reactor
from rmq.utils.import_full_name import get_import_full_name
from items import ProjectItem
from pipelines import ProjectToDatabasePipeline
from commands.exporter.export import Exporter
import os
import datetime
from main import bot, dp
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from interface.data.config import logs


class DexScreenerSpider(scrapy.Spider):
    BASE_URL = 'https://dexscreener.com/'
    name = 'dexscreener'
    start_urls = ['https://api.dexscreener.com/latest/dex/pairs']

    custom_settings = {
        "ITEM_PIPELINES": {
            get_import_full_name(ProjectToDatabasePipeline): 310,
        },
        'DNS_TIMEOUT': 10,
    }

    def start_requests(self):
        self.logger.info(f'Sending request to {self.start_urls[0]}')
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse)

    def parse(self, response: Response):
        self.logger.info(f'Parsing response from {response.url}')
        data = json.loads(response.body)
        pairs = data.get('pairs', [])
        self.logger.info(f'Found {len(pairs)} pairs in response')
        for pair in pairs:
            item = ProjectItem()
            item['pair_id'] = pair['pairAddress']
            item['url'] = self.BASE_URL + 'pair/' + item['pair_id']
            item['title'] = pair['baseToken']['name'] + ' / ' + pair['quoteToken']['name']
            item['platform'] = 'www.dexscreener.com'
            self.logger.info(f'Created item for pair {item["title"]}')
            yield scrapy.Request(url=item['url'], callback=self.parse_detail, meta={'item': item})

    def parse_detail(self, response: Response):
        item = response.meta['item']
        self.logger.info(f'Parsing details for pair {item["title"]}')
        item['website'] = None
        item['telegram'] = None
        item['twitter'] = None

        # Example of extracting some additional details from the pair page
        # Modify the XPaths as per the actual structure of DexScreener pair pages
        contacts = response.xpath('//div[@class="social-links"]/a/@href').getall()
        if contacts:
            item['website'] = contacts[0] if 't.me' not in contacts[0] else None
            item['telegram'] = next((url for url in contacts if 't.me' in url), None)
            item['twitter'] = next((url for url in contacts if 'x.com' in url), None)

        yield item

    def errback_httpbin(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            self.logger.error(failure.getErrorMessage())
        else:
            self.logger.error(repr(failure))

    def closed(self, reason):
        self.logger.info(f'Spider closed: {reason}')
        exporter = Exporter()
        reactor.callLater(0, exporter.run, [], None)
