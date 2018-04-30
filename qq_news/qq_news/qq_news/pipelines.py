# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo


class MongoPipeline(object):

    collection_name = 'qq_news'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_db = mongo_db
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[self.mongo_db]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db['user'].update({'articleid': item['articleid']}, {'$set': item}, True)
        return item
