# awesome_crawl（优美的爬虫）

### [1、腾讯新闻的全站爬虫](https://github.com/zhangslob/awesome_crawl/tree/master/qq_news/qq_news)

**采集策略**

从[网站地图](http://www.qq.com/map/)出发，找出所有子分类，从每个子分类中再寻找详情页面的链接。

首先寻找每条新闻的ID，然后移动端采集具体内容。

再去找一些推荐新闻的接口，做一个“泛爬虫”。
