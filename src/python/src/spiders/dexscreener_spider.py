import scrapy
import cloudscraper

class DexScreenerSpider(scrapy.Spider):
    name = 'dexscreener'
    start_urls = ['https://dexscreener.com/?rankBy=trendingScoreH24&order=desc']

    def start_requests(self):
        scraper = cloudscraper.create_scraper()
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse, meta={'scraper': scraper})

    def parse(self, response):
        scraper = response.meta['scraper']
        content = scraper.get(response.url).text[:1000]
        response = scrapy.http.HtmlResponse(url=response.url, body=content, encoding='utf-8')
        print(response.text)
