# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuTopicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    detail_id = scrapy.Field()
    topic_id = scrapy.Field()
    crawl_time = scrapy.Field()


class AnswerItem(scrapy.Item):
    unanswered_count = scrapy.Field()
    best_answerers_count = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    father_count = scrapy.Field()
    excerpt = scrapy.Field()
    introduction = scrapy.Field()
    followers_count = scrapy.Field()
    avatar_url = scrapy.Field()
    best_answers_count = scrapy.Field()
    type = scrapy.Field()
    id = scrapy.Field()
    questions_count = scrapy.Field()
    crawl_time = scrapy.Field()
