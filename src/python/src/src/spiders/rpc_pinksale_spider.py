import json
import scrapy
from scrapy.http import Response
from scrapy.utils.project import get_project_settings
from scrapy.core.downloader.handlers.http11 import TunnelError

from rmq.utils.decorators import rmq_callback, rmq_errback
from rmq.pipelines.item_producer_pipeline import ItemProducerPipeline
from rmq.utils.import_full_name import get_import_full_name
from rmq.extensions.rpc_task_consumer import RPCTaskConsumer
from rmq.spiders import TaskToSingleResultSpider


class Pinksalespider(TaskToSingleResultSpider):
    name = 'pinksale_rpc'
    custom_settings = {
        "ITEM_PIPELINES": {
            get_import_full_name(ItemProducerPipeline): 310,
        }
    }
    project_settings = get_project_settings()
    # domain = 'www.pinksale.finance'
    start_urls = ['https://api.pinksale.finance/api/v1/pool/list?page=1&limit=21&excludeChainIds[]=97&excludeChainIds[]=501423', 'https://www.pinksale.finance/launchpads']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_queue_name = 'project_task'
        self.reply_to_queue_name = 'project_reply'
        self.result_queue_name = 'project_result'
        
        self.completion_strategy = RPCTaskConsumer.CompletionStrategies.REQUESTS_BASED
    
    def next_request(self, _delivery_tag, msg_body):
        data = json.loads(msg_body)
        return scrapy.Request(
            data["url"], 
            callback=self.parse,
            errback=self.errback
            )
     
    @rmq_callback        
    def parse(self, response: Response):
        print(response.body)
        
    @rmq_errback
    def errback(self, failure):
        if failure.check(TunnelError):
            self.logger.info("TunnelError. Copy request")
            yield failure.request.copy()
        else:
            self.logger.warning(f"IN ERRBACK: {repr(failure)}")