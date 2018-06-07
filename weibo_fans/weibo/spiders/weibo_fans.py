#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'zhangslob'
__date__ = '18-6-5'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛
"""

import json
import scrapy
from ..items import WeiboItem


class WeiboSpider(scrapy.Spider):

    name = 'weibo'
    start_urls = ['https://m.weibo.cn/api/container/getIndex?containerid=1076031223178222'
                  '&page={}'.format(i) for i in range(1, 366)]

    repost = 'https://m.weibo.cn/api/statuses/repostTimeline?id={}&page={}'
    comment = 'https://m.weibo.cn/api/comments/show?id={}&page={}'
    attitudes = 'https://m.weibo.cn/api/attitudes/show?id={}&page={}'
    user = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}'

    custom_settings = {
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
        'MONGO_URL': 'mongodb://127.0.0.1:27017',
        'MONGO_DB': name,
        'ITEM_PIPELINES': {
            'weibo.pipelines.WeiboPipeline': 301,
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 'weibo.middlewares.ProxyMiddleware': 543,
        },
    }

    def parse(self, response):

        # 如果需要登录，就结束吧，这里并没有设置重新采集这个请求，可以写一个中间件来重试
        if 'passport' in response.url:
            return

        data = json.loads(response.text)
        if data['ok'] != 1:
            return

        for i in data['data']['cards']:
            mid = i['mblog'].get('id')

            # 去第一页查询总共有多少翻页，转发
            first_page = self.repost.format(mid, 1)
            yield scrapy.Request(first_page, callback=self.first_repost, meta={'mid': mid})

            # 评论
            comment = self.comment.format(mid, 1)
            yield scrapy.Request(comment, callback=self.first_comment, meta={'mid': mid})

            # 点赞
            attitudes = self.attitudes.format(mid, 1)
            yield scrapy.Request(attitudes, callback=self.first_attitudes, meta={'mid': mid})

    # 处理转发
    def first_repost(self, response):
        if 'passport' in response.url:
            return

        data = json.loads(response.text)
        if data['ok'] != 1:
            return

        total_number = data['data'].get('total_number')
        total_page = int(total_number // 55)
        mid = response.meta['mid']

        for i in range(1, total_page):
            url = self.repost.format(mid, i)
            yield scrapy.Request(url, callback=self.repost_data)

    def repost_data(self, response):
        if 'passport' in response.url:
            return

        data = json.loads(response.text)
        if data['ok'] != 1:
            return

        for i in data['data']['data']:
            user = dict()
            user['id'] = i['user']['id']
            user['statuses_count'] = i['user']['statuses_count']
            user['screen_name'] = i['user']['screen_name']
            user['profile_url'] = i['user']['profile_url']
            user['description'] = i['user']['description']
            user['gender'] = i['user']['gender']
            user['followers_count'] = i['user']['followers_count']
            user['follow_count'] = i['user']['follow_count']
            item = WeiboItem()
            item.update(user)
            yield item

    # 处理评论
    def first_comment(self, response):
        if 'passport' in response.url:
            return

        data = json.loads(response.text)
        if data['ok'] != 1:
            return

        total_number = data['data'].get('total_number')
        total_page = int(total_number // 55)
        mid = response.meta['mid']

        for i in range(1, total_page):
            url = self.comment.format(mid, i)
            yield scrapy.Request(url, callback=self.comment_data)

    def comment_data(self, response):
        if 'passport' in response.url:
            return

        data = json.loads(response.text)
        if data['ok'] != 1:
            return

        for i in data['data']['data']:
            user_id = i['user']['id']
            yield scrapy.Request(self.user.format(user_id), callback=self.user_data)

    # 处理点赞
    def first_attitudes(self, response):
        if 'passport' in response.url:
            return

        data = json.loads(response.text)
        if data['ok'] != 1:
            return

        total_number = data['data'].get('total_number')
        total_page = int(total_number // 55)
        mid = response.meta['mid']

        for i in range(1, total_page):
            url = self.attitudes.format(mid, i)
            yield scrapy.Request(url, callback=self.attitudes_data)

    def attitudes_data(self, response):
        if 'passport' in response.url:
            return

        data = json.loads(response.text)
        if data['ok'] != 1:
            return

        for i in data['data']['data']:
            user_id = i['user']['id']
            yield scrapy.Request(self.user.format(user_id), callback=self.user_data)

    def user_data(self, response):
        if 'passport' in response.url:
            return

        data = json.loads(response.text)
        if data['ok'] != 1:
            return

        item = WeiboItem()
        item['id'] = data['data']['userInfo']['id']
        item['statuses_count'] = data['data']['userInfo']['statuses_count']
        item['screen_name'] = data['data']['userInfo']['screen_name']
        item['profile_url'] = data['data']['userInfo']['profile_url']
        item['description'] = data['data']['userInfo']['description']
        item['gender'] = data['data']['userInfo']['gender']
        item['followers_count'] = data['data']['userInfo']['followers_count']
        item['follow_count'] = data['data']['userInfo']['follow_count']

        yield item
