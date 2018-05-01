#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import scrapy
import demjson
from ..items import NewsUrlItem


class ListSpider(scrapy.Spider):
    name = 'qq_list'
    allowed_domains = ['qq.com']
    start_urls = ['http://www.qq.com/map/']
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
        'REDIS_HOST': '127.0.0.1',
        'REDIS_PORT': '6379',
        'REDIS_DB': '0',
        'ITEM_PIPELINES': {
            'qq_news.pipelines.RedisStartUrlsPipeline': 301,
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 'qq_news.middlewares.ProxyMiddleware': 543,
        },
    }

    def parse(self, response):
        """
        采集所有子分类的链接
        :param response:
        :return: detail response
        """
        urls_list = []
        for i in response.xpath('//*[@id="wrapCon"]/div/div[1]/div[2]/dl'):
            urls = i.xpath('dd/ul/li/strong/a/@href').extract() or i.xpath('dd/ul/li/a/@href').extract()
            urls_list.extend(i.strip() for i in urls)
        for url in urls_list:
            yield scrapy.Request(url, callback=self.parse_url)

    def parse_url(self, response):
        """
        去子分类下采集所有符合要求的详情链接，从移动端爬数据
        :param response: http://news.qq.com/
        :return:
        """
        pat = re.compile('http://new.qq.com/.*/.*.html')
        detail_urls = pat.findall(response.text)
        for url in detail_urls:
            item = NewsUrlItem()
            item['url'] = url
            yield item


