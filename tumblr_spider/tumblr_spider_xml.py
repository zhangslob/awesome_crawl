#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhangslob
@file: tumblr_spider_xml.py 
@time: 2018/12/11
@desc: 
"""

import os
import re
import sys
import logging
import hashlib
import requests

from tenacity import *
from concurrent import futures
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')

headers = {'accept': 'text/html, */*; q=0.01', 'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7', 'x-requested-with': 'XMLHttpRequest'}


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
        self.session.proxies.update(get_proxy())
        self.session.headers.update(headers)

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
        self.photo_url = 'https://{}.tumblr.com/api/read?type=photo&num=50&start={}'
        self.video_url = 'https://{}.tumblr.com/api/read?type=video&num=50&start={}'
        self.name = name
        self.s = Session()
        self.total_photo_page = None
        self.total_video_page = None

    @retry(stop=stop_after_attempt(5))
    def download_html(self, url):
        return self.s.get(url)

    def get_total_page(self):
        self.total_photo_page = re.findall("total=\"(\d+)\"",
                                           self.download_html(self.photo_url.format(self.name, 0)).text)[0] // 50
        self.total_video_page = re.findall("total=\"(\d+)\"",
                                           self.download_html(self.video_url.format(self.name, 0)).text)[0] // 50

    def parse_xml(self, html):

        root = ET.fromstring(html)
        resources = []
        if 'photo' in html:
            for item in root.iterfind('posts/post'):
                print(item.findtext('tumblelog'))
        else:
            for item in root.iterfind('posts/post'):
                print(item.findtext('video-player'))
        return resources

    def _save_media(self, url):
        content = self.download_html(url).content
        file_folder = '{}/{}'.format(os.getcwd(), self.name)

        # 先创建文件夹
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)

        if url[-3:] == 'mp4':
            file_path = '{}/{}.{}'.format(file_folder, hashlib.md5(content).hexdigest(), 'mp4')
        else:
            file_path = '{}/{}.{}'.format(file_folder, hashlib.md5(content).hexdigest(), 'jpg')

        if not os.path.exists(file_path):
            with open(file_path, 'wb') as f:
                f.write(content)
                f.close()
            logging.info('save image path: {}'.format(file_path))
            return True
        else:
            logging.debug("file already exists  with url: {}".format(url))
            return False

    def main(self):
        self.get_total_page()
        with futures.ThreadPoolExecutor(max_workers=50) as executor:
            for i in range(self.total_photo_page + 2):


