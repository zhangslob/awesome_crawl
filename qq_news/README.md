

# [腾讯新闻的全站爬虫](./qq_news/spiders)

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