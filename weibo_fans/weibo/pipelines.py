# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from pymongo import errors


class WeiboPipeline(object):
    def open_spider(self, spider):
        self.client = pymongo.MongoClient()
        self.db = self.client[spider.mongodb]

    def process_item(self, item, spider):
        name = type(item).__name__
        self.db[name].create_index('id', unique=True)
        try:
            self.db[name].insert(dict(item))
        except errors.DuplicateKeyError:
            spider.logger.debug('DuplicateKeyError with {}'.format(item['detail_id']))
        return item

    def close_spider(self, spider):
        self.client.close()
