# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter
from scrapy.conf import settings


class CSVPipeline(object):
    def __init__(self):
        self.files = {}
        self.exporter = None

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        try:
            fo = open(spider.output_file, 'w+b')
        except IOError as e:
            spider.crawler.engine.close_spider(spider, "ERROR: Can't create CSV file: " + str(e))
            return

        self.files[spider] = fo
        self.exporter = CsvItemExporter(fo)
        self.exporter.fields_to_export = settings.getlist("EXPORT_FIELDS")
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        if self.exporter is not None:
            self.exporter.finish_exporting()
            f = self.files.pop(spider)
            f.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
