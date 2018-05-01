# awesome_crawl（优美的爬虫）

### [1、腾讯新闻的全站爬虫](https://github.com/zhangslob/awesome_crawl/tree/master/qq_news/qq_news)

**采集策略**

从[网站地图](http://www.qq.com/map/)出发，找出所有子分类，从每个子分类中再寻找详情页面的链接。

首先寻找每条新闻的ID，然后移动端采集具体内容。

再去找一些推荐新闻的接口，做一个“泛爬虫”。

**说明**

整套系统中分为两部分，一套是生产者，专门去采集qq新闻的链接，然后存放到redis中，一套是消费者，从redis中读取这些链接，解析详情数据。
所有配置文件都是爬虫中的`custom_settings`中，可以自定义。

如果需要设置代理，请在`middlewares.ProxyMiddleware`中设置。

**qq_list**: 这个爬虫是生产者。运行之后，在你的redis服务器中会出现`qq_detail:start_urls`，即种子链接


**qq_detail**: 这个爬虫是生消费者，运行之后会消费redis里面的数据，如下图：


![](https://i.imgur.com/j81d8AP.png)

## TODO

1. 增加更多新闻链接的匹配，从推荐接口处获得更多种子链接
2. 增加“泛爬虫”，采集种子链接
2. 数据库字段检验
3. redis中数据为空爬虫自动关闭（目前redis数据被消费完之后爬虫并不会自动关闭，如下图）
![](https://i.imgur.com/Sk4GDMA.png)