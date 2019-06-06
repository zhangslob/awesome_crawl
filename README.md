

# awesome_crawl [![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome) 

---

| 爬虫                        | 说明             | 技术栈 |
| ------------------------- | -------------- | -------------- |
| [腾讯新闻](https://github.com/zhangslob/awesome_crawl#1%E8%85%BE%E8%AE%AF%E6%96%B0%E9%97%BB%E7%9A%84%E5%85%A8%E7%AB%99%E7%88%AC%E8%99%AB) | 采集所有腾讯新闻的链接和新闻详情        | scrapy,mongo,redis |
| [知乎话题](https://github.com/zhangslob/awesome_crawl#2%E7%9F%A5%E4%B9%8E%E6%89%80%E6%9C%89%E9%97%AE%E9%A2%98)                       | 从话题广场出发，先采集子话题ID，再采集ID下所有问题          | scrapy,mongo,redis |
| [微博粉丝](https://github.com/zhangslob/awesome_crawl#3%E8%83%A1%E6%AD%8C%E6%89%80%E6%9C%89%E5%BE%AE%E5%8D%9A%E7%B2%89%E4%B8%9D)                | 采集大V的所有粉丝          | scrapy,mongo,redis |
| [Tumblr爬虫](https://github.com/zhangslob/awesome_crawl#4tumblr%E7%88%AC%E8%99%AB) | 下载指定Tumblr博主的资源 | requests,concurrent |
| [妹子图爬虫](https://github.com/zhangslob/awesome_crawl#5%E5%A6%B9%E5%AD%90%E5%9B%BE%E7%88%AC%E8%99%AB) | go语言下载妹子图 | goroutine,goquery |



如果能帮助你，那就最好了。欢迎关注公众号：

![](https://ws4.sinaimg.cn/large/006tKfTcly1g0zrwffcfbj309k09kjrc.jpg)




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

你可以自行添加更多爬虫去采集种子链接，如从[首页](http://www.qq.com/)进入匹配，从推荐入口：

```python
import requests

url = "https://pacaio.match.qq.com/xw/recommend"

querystring = {"num":"10^","callback":"__jp0"}

headers = {
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8",
    'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
    'accept': "*/*",
    'referer': "https://xw.qq.com/m/recommend/",
    'authority': "pacaio.match.qq.com",
    'cache-control': "no-cache",
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)
```
等等，你所需要做的仅仅是把这些抓到的种子链接塞到redis里面，也就是启用`qq_news.pipelines.RedisStartUrlsPipeline`这个中间件。

## TODO

1. 增加更多新闻链接的匹配，从推荐接口处获得更多种子链接
2. 增加“泛爬虫”，采集种子链接
2. 数据库字段检验
3. redis中数据为空爬虫自动关闭（目前redis数据被消费完之后爬虫并不会自动关闭，如下图）
![](https://i.imgur.com/Sk4GDMA.png)

### [2、知乎所有问题](https://github.com/zhangslob/awesome_crawl/tree/master/zhihu_topic/zhihu_topic)


从[话题广场](https://www.zhihu.com/topics)出发，先采集所有知乎的子话题，如


![](https://i.imgur.com/TC89LlB.png)

解析之后把所有的话题ID保存到redis中，再新建爬虫去采集该话题下所有的问题（这部分基本完工，但是还没测试过）。


### [3、胡歌所有微博粉丝](https://github.com/zhangslob/awesome_crawl/tree/master/weibo_fans)

详见 [为了知道胡歌粉丝的男女比率，爬了三百万微博数据](https://zhangslob.github.io/2018/06/07/%E8%83%A1%E6%AD%8C%E7%94%B7%E7%B2%89%E5%A4%9A%E8%BF%98%E6%98%AF%E5%A5%B3%E7%B2%89%E5%A4%9A-%E7%88%AC%E7%88%AC%E5%BE%AE%E5%8D%9A/)



### [4、Tumblr爬虫](https://github.com/zhangslob/awesome_crawl/tree/master/tumblr_spider)

filepath: `tumblr_spider/tumblr_spider.py`

useage: `python tumblr_spider.py username`
example: `python tumblr_spider.py user1,use2,use3`

Attention: 你需要可以访问国外的代理，并在`get_proxy()`函数中设置

### [5、妹子图爬虫](https://github.com/zhangslob/awesome_crawl/tree/master/mzitu)

使用`go`开发的爬虫，可以下载妹子图至本地，效果如下：

![](https://i.loli.net/2019/06/06/5cf8e13ebce7b80963.png)
