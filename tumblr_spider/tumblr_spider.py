#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhangslob
@file: tumblr_spider.py 
@time: 2018/12/06
@desc: a spider to download video and image on tumblr
"""
import os
import sys
import logging
import hashlib
import requests

from tenacity import *
from concurrent import futures
from scrapy.selector import Selector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')

headers = {
    'accept': 'text/html, */*; q=0.01',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'x-requested-with': 'XMLHttpRequest'
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
        # poipon2
        self.name = name
        self.base_url = 'http://{}.tumblr.com/page/{}'
        self.s = Session()
        self.s.session.headers.update({'referer': 'https://{}.tumblr.com/'.format(name)})
        self.page = 1

    def keep_download_next_page(self):
        """
        翻页并下载
        :return:
        """
        while True:
            response = self.download_html(self.base_url.format(self.name, self.page))
            if 'posts-no-posts content' not in response.text:
                media_url = self._parse_response(response.text)
                if media_url:
                    logging.info('crawl user: {} page: {} images: {}'.format(self.name, self.page, len(media_url)))
                    if media_url:
                        for url in media_url:
                            if not self._save_media(url):
                                self._save_media(url)

                self.page += 1

            else:
                # 当来到最后一页
                logging.info('user last page: {}'.format(self.base_url.format(self.name, self.page)))
                return

    @retry(stop=stop_after_attempt(5))
    def download_html(self, url):
        """
        下载网页，重试5次
        :param url:
        :return: html
        """
        return self.s.get(url, timeout=10, verify=False)

    @staticmethod
    def _parse_response(html):
        """
        解析图片或视频链接
        :param html:
        :return:
        """
        s = Selector(text=html)
        media_url = s.xpath('//div[@class="main"]/article/div/section[1]/div/div/figure/img/@src').extract()
        media_url.extend(s.xpath('//div[@class="main"]/article/div/section[1]/div/div/figure/video/source/@src').extract())
        return media_url if media_url else None

    def _save_media(self, url):
        """
        下载并保存媒体
        :param url:
        :return:
        """
        content = self.download_html(url).content
        file_folder = '{}/{}'.format(os.getcwd(), self.name)

        # 先创建文件夹
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)
            # '/Users/xxx/awesome_crawl/tumblr_spider/poipon2

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
        """
        程序主入口
        :return:
        """
        self.keep_download_next_page()


if __name__ == '__main__':
    args = sys.argv[1]
    names_list = []
    if args:
        names_list.extend(args.split(','))
    else:
        names_list.append('poipon2')

    with futures.ThreadPoolExecutor() as executor:
        for name in names_list:
            t = Tumblr(name)
            executor.submit(t.main())
