# -*- coding: utf-8 -*-

import json
import scrapy


class TopicSpider(scrapy.Spider):
    name = 'topic'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/topics']
    post_url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
    form_data = {
            'method': 'next',
            'params': {"topic_id": "", "offset": "", "hash_id": ""},
        }

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CONCURRENT_REQUESTS': 64,
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,
        'LOG_LEVEL': 'INFO',
        'RETRY_TIMES': 15,
        'DEFAULT_REQUEST_HEADERS': {
            "HOST":"www.zhihu.com",
            "Referer":"https://www.zhihu.com",
            'User_Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)"
                         " Chrome/55.0.2883.75 Safari/537.36 Maxthon/5.1.3.2000"
    },
        'REDIS_HOST': '127.0.0.1',
        'REDIS_PORT': '6379',
        'REDIS_DB': '0',
        'ITEM_PIPELINES': {
            # 'qq_news.pipelines.RedisStartUrlsPipeline': 301,
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 'qq_news.middlewares.ProxyMiddleware': 543,
        },
    }

    def parse(self, response):
        for i in response.xpath('//ul[@class="zm-topic-cat-main clearfix"]/li'):
            topic_id = ''.join(i.xpath('@data-id').extract())
            # todo

    def fuck_content(self, response):
        """
        example content
        "<div class="item"><div class="blk">↵<a target="_blank" href="/topic/19550434">↵<img src="https://pic3.zhimg.com/eab85c3ad_xs.jpg" alt="艺术">↵<strong>艺术</strong>↵</a>↵<p>艺术迄今依旧没有公认的定义，目前广义的艺术乃是由具有智能思考能…</p>↵↵<a id="t::-69" href="javascript:;" class="follow meta-item zg-follow"><i class="z-icon-follow"></i>关注</a>↵↵</div></div>"
        :param response:
        :return:
        """
        try:
            data = json.loads(response.text)['msg']
            for i in data:
                s = scrapy.Selector(text=i)
                url = s.xpath('//div/div/a[1]/@href').extract_first()

                yield url
        except Exception as e:
            self.logger.error('fuck_content wrong with url: {} {}'.format(e, response.url))
