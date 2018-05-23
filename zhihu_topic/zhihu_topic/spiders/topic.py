# -*- coding: utf-8 -*-

import re
import json
import scrapy


class TopicSpider(scrapy.Spider):
    name = 'topic'
    allowed_domains = ['zhihu.com']
    # start_urls = ['https://www.zhihu.com/topics']
    post_url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
    form_data = {
            'method': 'next',
            'params': {"topic_id": "", "offset": "", "hash_id": ""},
        }

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CONCURRENT_REQUESTS': 64,
        'DOWNLOAD_DELAY': 0,
        # 'COOKIES_ENABLED': False,
        'LOG_LEVEL': 'DEBUG',
        'RETRY_TIMES': 15,

        'DEFAULT_REQUEST_HEADERS': {
            "HOST": "www.zhihu.com",
            "Referer": "https://www.zhihu.com",
            'User_Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/55.0.2883.75 Safari/537.36 Maxthon/5.1.3.2000"
    },
        'REDIS_HOST': '127.0.0.1',
        'REDIS_PORT': '6379',
        'REDIS_DB': '0',
        'ITEM_PIPELINES': {
            # 'qq_news.pipelines.RedisStartUrlsPipeline': 301,
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 'qq_news.middlewares.ProxyMiddleware': 543,
        },
    }

    def start_requests(self):
        url = ['https://www.zhihu.com/topics']
        for i, url in enumerate(url):
            yield scrapy.Request(url, callback=self.parse, meta={'cookiejar': 1})

    def parse(self, response):
        for i in response.xpath('//ul[@class="zm-topic-cat-main clearfix"]/li'):
            topic_id = ''.join(i.xpath('@data-id').extract())
            url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
            d = {
                "topic_id": topic_id,
                "offset": 40,
                "hash_id": ""}

            data = {
                'method': 'next',
                'params': json.dumps(d),
            }

            xsrf = response.xpath('/html/body/input/@value').extract_first()
            headers = {
                'origin': "https://www.zhihu.com",
                'accept-encoding': "gzip, deflate, br",
                'accept-language': "zh-CN,zh;q=0.9,en;q=0.8",
                'user-agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                              " Chrome/66.0.3359.181 Safari/537.36",
                'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
                'accept': "*/*",
                'referer': "https://www.zhihu.com/topics",
                'authority': "www.zhihu.com",
                'x-requested-with': "XMLHttpRequest",
                'x-xsrftoken': xsrf,
                'cache-control': "no-cache",
                }
            yield scrapy.FormRequest(url, formdata=data, headers=headers,
                                     meta={'cookiejar': response.meta['cookiejar']},
                                     callback=self.parse_content)
            # todo

    def parse_content(self, response):
        """
        :param response:
        :return:
        """
        topic_id = re.findall('href=\"/topic/\d+\"', response.text)
        pass
