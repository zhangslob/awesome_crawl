# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import redis
import pymongo
from pymongo import errors


class ZhihuTopicPipeline(object):

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(spider.mongourl)
        self.db = self.client[spider.mongodb]

    def process_item(self, item, spider):
        name = type(item).__name__
        if name == 'ZhihuTopicItem':
            self.db[name].create_index('detail_id', unique=True)
        else:
            self.db[name].create_index('id', unique=True)
        try:
            self.db[name].insert(dict(item))
        except errors.DuplicateKeyError:
            spider.logger.debug('DuplicateKeyError with {}'.format(item['detail_id']))
        return item

    def close_spider(self,spider):
        self.client.close()


class RedisStartUrlsPipeline(object):
    """
    把详情页链接保存到 redis
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
        redis_key = 'parent:start_urls'
        url = 'https://www.zhihu.com/api/v3/topics/{}/children?limit=10&offset=0'.format(item['detail_id'])
        self.redis_client.sadd(redis_key, url)
        spider.logger.debug(
            '=========== Success push to REDIS with {} ==========='.format(item['detail_id']))
        return item
