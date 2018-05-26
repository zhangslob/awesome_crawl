# -*- coding: utf-8 -*-

import re
import json
from datetime import datetime
import scrapy
from ..items import ZhihuTopicItem
# todo API: https://www.zhihu.com/api/v3/topics/19552679/parent \ https://www.zhihu.com/api/v3/topics/19552679/children


class TopicSpider(scrapy.Spider):
    name = 'topic'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/topics']
    post_url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
    form_data = {
            'method': 'next',
            'params': {"topic_id": "", "offset": "", "hash_id": ""},
        }
    offset = 0

    mongourl = 'mongodb://127.0.0.1:27017'
    mongodb = name

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CONCURRENT_REQUESTS': 64,
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,
        'LOG_LEVEL': 'INFO',
        'RETRY_TIMES': 15,
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
            'zhihu_topic.pipelines.RedisStartUrlsPipeline': 304,
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 'qq_news.middlewares.ProxyMiddleware': 543,
        },
    }

    headers = {
        'origin': "https://www.zhihu.com",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.9,en;q=0.8",
        'user-agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/66.0.3359.181 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
        'accept': "*/*",
        'referer': "https://www.zhihu.com/topics",
        'authority': "www.zhihu.com",
        'x-requested-with': "XMLHttpRequest",
        'x-xsrftoken': '',
        'cache-control': "no-cache",
    }

    def parse(self, response):
        xsrf = response.xpath('/html/body/input/@value').extract_first()
        headers = self.headers
        headers['x-xsrftoken'] = xsrf

        while True:
            for i in response.xpath('//ul[@class="zm-topic-cat-main clearfix"]/li'):
                topic_id = ''.join(i.xpath('@data-id').extract())
                url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
                item = {"topic_id": topic_id, "offset": self.offset, "hash_id": ""}

                data = {
                    'method': 'next',
                    'params': json.dumps(item),
                }

                yield scrapy.FormRequest(url, formdata=data, headers=headers,
                                         meta={'item': item, 'xsrf': xsrf},
                                         callback=self.parse_content)

    def parse_content(self, response):
        """
        其实这里应该分开，会比较好看。把topic_id储存到redis里，然后重新在写一个爬虫来专门处理detail_id
        先这样这吧，虽然看起来很丑。。哈哈
        :param response:
        :return:
        """
        results = json.loads(response.text)

        # 如果本页还存在，请求下一页，同时解析这些数据
        if results['msg']:
            url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
            self.offset += 20
            topic_id = response.meta['item'].get('topic_id')
            xsrf = response.meta['item'].get('xsrf')
            item = {"topic_id": topic_id, "offset": self.offset, "hash_id": ""}

            detail_id = re.findall('href=\"/topic/(\d+)\"', ''.join(results['msg']))
            for id in detail_id:
                crawl_time = datetime.utcnow()
                item_ = ZhihuTopicItem()
                item_['detail_id'] = id
                item_['topic_id'] = topic_id
                item_['crawl_time'] = crawl_time
                yield item_

            headers = self.headers
            headers['x-xsrftoken'] = xsrf
            data = {
                'method': 'next',
                'params': json.dumps(item),
            }

            yield scrapy.FormRequest(url, formdata=data, headers=headers,
                                     meta={'item': item},
                                     callback=self.parse_content)

        else:
            pass
