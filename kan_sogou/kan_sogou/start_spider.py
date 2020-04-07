#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhujian
@file  : start_spider.py
@time  : 2020/4/7
@desc  :
       
"""

from scrapy.cmdline import execute

execute('scrapy crawl sougou -a master=True'.split())
