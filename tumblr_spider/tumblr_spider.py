#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhangslob
@file: tumblr_spider.py 
@time: 2018/12/06
@desc: a spider to download video and image on tumblr
"""

import requests
from scrapy.selector import Selector


headers = {
    'authority': 'poipon2.tumblr.com',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'referer': ''
}


def get_proxy():
    """
    export http_proxy=http://127.0.0.1:1087;export https_proxy=http://127.0.0.1:1087;
    必须是可以访问Google的代理
    :return:
    """
    proxy = 'http://127.0.0.1:1087'
    return {"http": proxy, 'https': proxy}


class Session(object):
    def __init__(self):
        self.session = requests.session()

    def get(self, url, **kwargs):
        retry_times = 0
        while True:
            try:
                res = self.session.get(url, **kwargs)
                return res
            except Exception:
                retry_times += 1
                if retry_times > 20:
                    return None
                else:
                    continue


class Tumblr(object):
    def __init__(self, name):
        self.name = name
        self.base_url = 'http://{}.tumblr.com/page/{}'
        self.proxies = get_proxy()
        self.headers = headers
        self.headers['referer'] = 'https://{}.tumblr.com/'.format(name)
        self.s = Session()

    def keep_download_next_page(self):
        """
        翻页并下载
        :return:
        """
        page = 1
        while True:
            try:
                response = self.s.get(
                    self.base_url.format(page), headers=self.headers, timeout=10,
                    proxies=self.proxies)
                if 'posts-no-posts content' not in response.text:
                    self._parse_response(response.text)

            except Exception as e:
                print(e)

    @staticmethod
    def _parse_response(html):
        """
        解析图片或视频链接
        :param html:
        :return:
        """
        s = Selector(text=html)

    def _download_media(self, url):
        """
        下载并保存
        :param url:
        :return:
        """
