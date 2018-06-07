# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    statuses_count = scrapy.Field()
    screen_name = scrapy.Field()
    profile_url = scrapy.Field()
    description = scrapy.Field()
    gender = scrapy.Field()
    followers_count = scrapy.Field()
    follow_count = scrapy.Field()
