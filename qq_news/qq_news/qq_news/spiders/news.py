#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import scrapy


class ExampleSpider(scrapy.Spider):
    name = 'qq'
    allowed_domains = ['qq.com']
    start_urls = ['http://www.qq.com/map/']

    mobile_url = 'https://xw.qq.com/cmsid/{}'
    recommend_url = 'https://pacaio.match.qq.com/xw/relate?num=6&id=20180425A0VYZO&callback=__jp1'  # 推荐新闻
    mobile_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38' \
                ' (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'

    custom_settings = {
        'CONCURRENT_REQUESTS': 64,
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,
        'DEFAULT_REQUEST_HEADERS': {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
        }
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
            url_ = self.mobile_url.format(url.split('/')[-1].split('.')[0])
            yield scrapy.Request(url_, callback=self.parse_content,
                                 headers={'User-Agent': self.mobile_ua, 'Referer': url},)

    def parse_content(self, response):
        """
        采集详情页数据，从移动端采集会比较简单
        :param response: https://xw.qq.com/cmsid/20180426A0XFTS
        :return: 
        """
        try:   # TODO FIX IT
            data = ''.join(re.findall(r'globalConfig\s=\s(\{.*?\});', response.text, re.S))
            title = ''.join(re.findall('title:\s(.*?),', data))
            articleid = ''.join(re.findall('articleid:\s(.*?),', data))
            channel = ''.join(re.findall('channel:\s(.*?),', data))
            cid = ''.join(re.findall('cid:\s(.*?),', data))
            commentNumber = ''.join(re.findall('title:\s(.*?),', data))
            pass
        except Exception as e:
            self.logger.error('parse_content {}, {}, {}'.format(e, response.url, response.text))
