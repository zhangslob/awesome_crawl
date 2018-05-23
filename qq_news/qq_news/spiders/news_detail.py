#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import scrapy
import demjson
from ..items import NewsDetailItem
from scrapy_redis.spiders import RedisSpider


class DetailSpider(RedisSpider):
    name = 'qq_detail'
    allowed_domains = ['qq.com']
    default_value = '暂无数据'

    mobile_url = 'https://xw.qq.com/cmsid/{}'
    recommend_url = 'https://pacaio.match.qq.com/xw/relate?num=6&id=20180425A0VYZO&callback=__jp1'  # 推荐新闻
    mobile_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38' \
                ' (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'

    custom_settings = {
        'CONCURRENT_REQUESTS': 64,
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,
        'LOG_LEVEL': 'INFO',
        'RETRY_TIMES': 15,
        'DEFAULT_REQUEST_HEADERS': {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
        },
        'MONGO_URI': 'localhost:27017',
        'MONGO_DATABASE': 'awesome_crawl',
        'REDIS_START_URLS_AS_SET': True,
        'ITEM_PIPELINES': {
            'qq_news.pipelines.MongoPipeline': 301,
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 'qq_news.middlewares.ProxyMiddleware': 543,
        },
    }

    def parse(self, response):
        """
        采集详情页数据，从移动端采集会比较简单
        :param response: https://xw.qq.com/cmsid/20180426A0XFTS
        :return:
        """
        url_ = self.mobile_url.format(response.url.split('/')[-1].split('.')[0])
        yield scrapy.Request(url_, callback=self.parse_detail,
                             headers={'User-Agent': self.mobile_ua, 'Referer': response.url},)

    def parse_detail(self, response):
        try:
            if response.url == 'https://xw.qq.com/404.html':
                return

            item = NewsDetailItem()
            data = ''.join(re.findall(r'globalConfig\s=\s(\{.*?\});', response.text, re.S))
            json_data = demjson.decode(data)

            for k, v in zip(list(json_data.keys()), list(json_data.values())):
                item[k] = v
            yield item
        except Exception as e:
            self.logger.error('parse_content error {}, {}, {}'.format(e, response.url, response.text))
