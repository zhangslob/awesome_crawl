#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
from datetime import datetime
import scrapy
from scrapy_redis.spiders import RedisSpider
from ..items import AnswerItem
# todo API: https://www.zhihu.com/api/v3/topics/19552679/parent \ https://www.zhihu.com/api/v3/topics/19552679/children


class ParentSpider(RedisSpider):
    name = 'parent'
    allowed_domains = ['zhihu.com']

    children_url = 'https://www.zhihu.com/api/v3/topics/{}/children?limit={}&offset=0'
    question_url = 'https://www.zhihu.com/api/v3/topics/{}'

    mongourl = 'mongodb://127.0.0.1:27017'
    mongodb = name

    custom_settings = {
        'CONCURRENT_REQUESTS': 64,
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,
        'LOG_LEVEL': 'INFO',
        'RETRY_TIMES': 15,
        'REDIS_START_URLS_AS_SET': True,
        'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/55.0.2883.75 Safari/537.36 Maxthon/5.1.3.2000",

        'DEFAULT_REQUEST_HEADERS': {
            "HOST": "www.zhihu.com",
            "Referer": "https://www.zhihu.com",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/55.0.2883.75 Safari/537.36 Maxthon/5.1.3.2000"
    },
        'REDIS_HOST': '127.0.0.1',
        'REDIS_PORT': '6379',
        'REDIS_DB': '0',
        # 'MONGO_URL': 'mongodb://127.0.0.1:27017',
        # 'MONGO_DB': name,
        'ITEM_PIPELINES': {
            'zhihu_topic.pipelines.ZhihuTopicPipeline': 301,
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 'qq_news.middlewares.ProxyMiddleware': 543,
        },
    }

    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/66.0.3359.181 Safari/537.36",
        'referer': "https://www.zhihu.com/topics",
    }

    def make_request_from_data(self, data):
        url = self.children_url.format(data, 0)
        return scrapy.Request(url)

    def parse(self, response):
        try:
            data = json.loads(response.text)
            if data['paging']['is_end'] == 'true':
                return
            else:
                next_url = data['paging']['next']
                yield scrapy.Request(next_url)

                for i in data['data']:
                    url = i['url']
                    yield scrapy.Request(url, callback=self.get_count)

        except Exception as e:
            self.logger.error('parse {} error : {}'.format(response.url, e))

    def get_count(self, response):
        try:
            data = json.loads(response.text)
            item = AnswerItem()
            item.update(data)
            item['crawl_time'] = datetime.utcnow()
            yield item
        except Exception as e:
            self.logger.error('get_count {} error : {}'.format(response.url, e))

