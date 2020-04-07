# -*- coding: utf-8 -*-
import json
import threading

import redis
import scrapy

from ..generate_uid import UidUtils
from ..settings import REDIS_URI
from scrapy_redis.spiders import RedisSpider


class SougouSpider(RedisSpider):
    name = 'sougou'
    allowed_domains = ['kan.sogou.com']
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/80.0.3987.149 Safari/537.36',
        'Referer': '',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    }
    refer_url = 'http://kan.sogou.com/player/{}/'
    url = 'http://kan.sogou.com/updown.php?gid={}&op=get'

    def __init__(self, master=None, **kwargs):
        super().__init__(**kwargs)
        if master:
            u = UidUtils()
            redis_client = redis.from_url(REDIS_URI)

            uid = redis_client.get('{}_uid'.format(self.name))
            if not uid:
                # 设置开始ID
                uid = 1
            if isinstance(uid, bytes):
                uid = int(str(uid, 'utf-8'))
            t = threading.Thread(target=u.work,
                                 args=(self.name, uid, self.logger))
            t.setDaemon(True)
            t.start()

    def make_requests_from_url(self, url):
        headers = self.headers
        headers['Referer'] = self.refer_url.format(url)
        url = self.url.format(url)
        return scrapy.Request(url, headers=headers)

    def parse(self, response):
        data = json.loads(response.text)
        if data['code'] == 0:
            self.logger.info("success get useful id {}".format(response.url))

