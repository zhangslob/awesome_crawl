#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhujian
@file  : generate_uid.py
@time  : 2020/4/7
@desc  :
       生成随机uid
"""
import random
import time

import redis

from .settings import REDIS_URI


class UidUtils(object):

    def __init__(self):
        self.redis_client = redis.from_url(REDIS_URI)
        self.uid = 0

    def watch_uid_num(self, spider):
        """
        检测redis中的数量
        :param spider: 判断不同爬虫
        :return: bool
        """
        redis_key = '{}:start_urls'.format(spider)
        uid = self.redis_client.llen(redis_key)
        if uid > 20000:
            return False
        else:
            return True

    def gen_uid(self, spider):
        """
        ID生成器，一次性生成20000个uid
        :return: 生成器
        """
        while True:
            js = 0
            result = list()
            while js < 20000:
                js += 1
                num1 = self.uid
                # 间隔是1000
                self.uid += 1000
                num_id = random.randint(num1, self.uid)
                result.append(num_id)
            # 将进度持久化到redis中
            self.redis_client.set('{}_uid'.format(spider), self.uid)
            yield result

    def work(self, spider, uid, logger):
        """
        开始工作，检查redis队列长度，如果小于预期，则定时插入数据
        :param logger:
        :param spider:
        :param uid:
        :return:
        """
        self.uid = uid
        while True:
            # TODO: Use redis pipeline execution.
            if self.watch_uid_num(spider):
                uid_list = next(self.gen_uid(spider))
                redis_key = '{}:start_urls'.format(spider)
                # sadd或者lpush都可以，因为已经在生成ID的时候去过重了
                self.redis_client.lpush(redis_key, *uid_list)
                logger.info("spider {} gen uid {}".format(spider, self.uid))
            time.sleep(3)
