#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhangslob
@file: zhaopin_positions.py 
@time: 2018/12/14
@desc: 
"""

import os
import requests

import pymongo

from concurrent import futures

from zs_factor import getip

mongodb_uri = 'mongodb://127.0.0.1:27017/zhihu'
client = pymongo.MongoClient(os.environ.get('MONGODB_URL', mongodb_uri))
db = client.get_database()['zhihu_positions']
db.create_index('id', unique=True)


def get_ip():
    while True:
        proxy = getip('dailiyun', group='', num=20)
        # TODO 把能用的代理找出来
        if proxy:
            # print(proxy)
            return {'http': proxy, 'https': proxy}


headers = {
    # 'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'accept': '*/*',
    'referer': 'https://www.zhihu.com/zhaopin/employment/positions',
    'authority': 'www.zhihu.com',
    'x-requested-with': 'Fetch',
}


def main(i):
    url = 'https://www.zhihu.com/api/v4/jobs/positions?offset={}&limit=20'
    try:
        response = requests.get(url.format(20*i), timeout=15, headers=headers, proxies=get_ip())
    except Exception as e:
        return main(i)

    for data in response.json()['data']:
        try:
            db.insert_one(data)
        except pymongo.errors.DuplicateKeyError:
            pass
    print('success')


if __name__ == '__main__':
    with futures.ThreadPoolExecutor(max_workers=50) as executor:
        for i in range(1302):
            executor.submit(main, i)

