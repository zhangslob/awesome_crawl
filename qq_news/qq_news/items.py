# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsUrlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()


class NewsDetailItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    articleid = scrapy.Field()
    channel = scrapy.Field()
    cid = scrapy.Field()
    commentNumber = scrapy.Field()
    comments = scrapy.Field()
    contents = scrapy.Field()
    ext_data = scrapy.Field()
    fisoriginal = scrapy.Field()
    id = scrapy.Field()
    img = scrapy.Field()
    isOm = scrapy.Field()
    isGreat = scrapy.Field()
    kurl = scrapy.Field()
    pubtime = scrapy.Field()
    src = scrapy.Field()
    url = scrapy.Field()
    plink = scrapy.Field()
    mid = scrapy.Field()
    linkurl = scrapy.Field()
    sitename = scrapy.Field()
