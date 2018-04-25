# -*- coding: utf-8 -*-
import scrapy


class ExampleSpider(scrapy.Spider):
    name = 'qq'
    allowed_domains = ['qq.com']
    start_urls = ['http://www.qq.com/map/']

    recommend_url = 'https://pacaio.match.qq.com/xw/relate?num=6&id=20180425A0VYZO&callback=__jp1'  # 推荐新闻
    # https://pacaio.match.qq.com/irs/rcd?cid=35&token=4d1ddbd5ea23e1ec0cdd44a6ebe8dec6&num=20&page=2&expIds=20180425A1EV59%7C20180425A1811E%7Ci0637cpjxs7%7C20180425A17Q4M%7C20180425A16TS3%7C20180425A16CVB%7C20180425A169J3%7C20180425A15JYI%7C20180425A14YTW%7C20180425A13VV0%7Co0564gbiu9b%7Cq0637sx6bch%7C20180425A0YCYE%7C20180425A0UNVM%7C20180425A0PLBZ%7C20180425A19G4O%7C20180425A1RKMV%7Cr0637ypfft7%7C20180425A0ZM3B%7C20180425A1ODQV&callback=__jp3

    def parse(self, response):
        """
        采集所有子分类的链接
        :param response:
        :return: detail response
        """
        urls_list = []
        for i in response.xpath('//*[@id="wrapCon"]/div/div[1]/div[2]/dl'):
            urls = i.xpath('dd/ul/li/strong/a/@href').extract() or i.xpath('dd/ul/li/a/@href').extract()
            urls_list.extend(i.strip() for i in urls)
        for url in urls_list:
            yield scrapy.Request(url, callback=self.parse_url)

    def parse_url(self, response):
        """
        去子分类下采集所有符合要求的详情链接
        :param response: http://news.qq.com/
        :return:
        """

