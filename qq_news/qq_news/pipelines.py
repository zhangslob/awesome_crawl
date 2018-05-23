# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import redis
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
        self.db[self.collection_name].update({'articleid': item['articleid']}, {'$set': item}, True)
        return item


class RedisStartUrlsPipeline(object):
    """
    把详情页链接保存到 redis（qq_detail:start_urls）
    """
    def __init__(self, redis_host, redis_port, redis_db):
        self.redis_client = redis.StrictRedis(
            host=redis_host, port=redis_port, db=redis_db)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            redis_host=crawler.settings.get('REDIS_HOST'),
            redis_port=crawler.settings.get('REDIS_PORT'),
            redis_db=crawler.settings.get('REDIS_DB'),
        )

    def process_item(self, item, spider):
        if type(item).__name__ == 'NewsUrlItem':
            redis_key = 'qq_detail:start_urls'
            self.redis_client.sadd(redis_key, item['url'])
            spider.logger.debug(
                '=========== Success push start_urls to REDIS with url {} ==========='.format(item['url']))
            return item
