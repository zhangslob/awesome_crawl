# [胡歌所有微博粉丝](./weibo/spiders/weibo_fans.py)


最近偶然间看到一条新闻，标题是：“胡歌作为一个男性明星，男粉丝比女粉丝还多，这不科学！”

![](https://i.imgur.com/959B59J.png)

文中这样说道“胡歌在微博上的粉丝就已经达到了5748.9398万人，并且通过查看粉丝可以发现许多都是男性粉丝，这不得不说这是独一无二了”

当时我就震惊了，“通过查看粉丝”？？？这是什么操作，现在的UC小编越来越多了吗？

我作为一名老胡的粉丝，简直是不能忍，这完全是在瞎写啊。

所以我有个想法，把胡歌微博上六千万粉丝数据爬取下来，看看到底男粉丝多还是女粉丝多。

>大家可以在自己心中猜测一个答案，到底男粉多还是女粉多呢～～。我的答案是男性比较多。

# 分析问题



![](https://i.imgur.com/h1TyXZ7.png)

这里可以看到胡歌微博粉丝总数约6千万，本次我的目标就是尽力去找到胡歌**活跃粉丝**的男女比例。



但是我们知道微博是有限制的，微博不会把所有数据都展示出来，如图

![](https://i.imgur.com/UxASfy6.png)

那么问题来了，我要怎样才能尽可能多的抓到粉丝数据？


这里我就想要尽可能多的抓取到老胡的活跃粉丝， 所谓活跃粉丝，指的是除去“不转发、不评论、不点赞”这些“三不”用户，是活跃的、有参与的用户。这些用户才是真正有价值的，正好去除了僵尸粉。


# 两种思路

采集微博粉丝，目前我有两种方法来解决这个问题，：

1. 全量采集。采集微博所有用户数据，包括关注、粉丝等。通过粉丝的粉丝、关注的关注、用户分类、推荐等等各种方法拿到微博全量用户数据。
2. 采样。采集胡歌的所有微博下有评论、点赞、转发的用户，凡是有参与过的亲密值加一，当这个值超过一定限度时（比如说5或者10），我们就认为该用户是胡歌的粉丝。

想了想，第一种方法短时间内是不现实的，方法2倒是可以尝试一波。

# 爬虫逻辑

爬虫分为三步：
1. 采集胡歌所有微博
2. 采集每条微博的三类数据（转发、评论、点赞）
3. 数据清洗

好了，现在已经非常清晰了，下面就开始去寻找爬取方法。

# 微博接口

根据以往的经验，weibo.cn 和 m.weibo.cn 是最简单爬取的，weibo.com 是最难的。这次我们从 m.weibo.cn 入手，分析可以得到胡歌微博的接口，而且是无需登录的！！！很重要。其他入口都需要解决登录难题！

`https://m.weibo.cn/api/container/getIndex?containerid=1076031223178222&page={}`

返回数据：

```cmd
cardlistInfo: {
containerid: "1076031223178222",
v_p: 42,
show_style: 1,
total: 3643,
page: 2
},
```

这里告诉我们总共有3643条数据，每页10条，那么翻页就很清晰了。

## 其他接口

```cmd
转发：https://m.weibo.cn/api/statuses/repostTimeline?id=4238119278366780&page={}

评论：https://m.weibo.cn/api/comments/show?id=4238119278366780&page={}

点赞：https://m.weibo.cn/api/attitudes/show?id=4238119278366780&page={}

```

（想要爬其他人，替换这里的id即可）

暂时不清楚总共有多少页，虽然返回的数据中有 `total_number` ，但是此数字并不准确，还需要更多测试。

```cmd
total_number: 19526897,
hot_total_number: 0,
max: 1952690
```

（简单测后发现总页数为`total_number//55`）

## 采集用户信息接口

`https://m.weibo.cn/api/container/getIndex?type=uid&value=6114792181`

其实不需要这一次请求，因为在转发接口中已经有我们想要的数据了，如下：

```cmd
user: {
id: 6431898981,
screen_name: "豪气superiority",
profile_image_url: "https://tvax2.sinaimg.cn/crop.9.0.220.220.180/0071hAK9ly8fmdxpea2vxj306n064glj.jpg",
profile_url: "https://m.weibo.cn/u/6431898981?uid=6431898981&featurecode=20000320",
statuses_count: 7255,
verified: false,
verified_type: -1,
close_blue_v: false,
description: "",
gender: "m",
mbtype: 0,
urank: 4,
mbrank: 0,
follow_me: false,
following: false,
followers_count: 2,
follow_count: 62,
cover_image_phone: "https://tva1.sinaimg.cn/crop.0.0.640.640.640/549d0121tw1egm1kjly3jj20hs0hsq4f.jpg",
avatar_hd: "https://wx2.sinaimg.cn/orj480/0071hAK9ly8fmdxpea2vxj306n064glj.jpg",
like: false,
like_me: false,
badge: {
user_name_certificate: 1,
wenchuan_10th: 1
}
```

很蛋疼的是，点赞和评论接口中并没有相关数据，所以点赞和评论部分要重新爬取，如下：

```cmd
{
id: 4247512245791226,
created_at: "5分钟前",
source: "微博 weibo.com",
user: {
id: 6114792181,
screen_name: "Ming_54456",
profile_image_url: "https://tvax1.sinaimg.cn/crop.367.164.918.918.180/006FP2Mlly8fjs2mf3x6pj319x0yoqbo.jpg",
verified: false,
verified_type: -1,
mbtype: 12,
profile_url: "https://m.weibo.cn/u/6114792181?uid=6114792181&featurecode=20000320",
remark: "",
following: false,
follow_me: false
}
},
```



微博官方API同样提供相应数据 ，建议使用前仔细阅读 [接口访问频次权限](http://open.weibo.com/wiki/Rate-limiting)

# 爬虫代码

爬虫完整代码可以去我的公众号（Python爬虫与算法进阶），回复“微博”获得。


爬虫语言是Python3，使用Scrapy框架，数据保存在mongo，没有使用分布式，单机3天跑完。

因为微博的反爬，需要大量代理支撑。

```python
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛
```



爬取的数据实例：

```cmd
{
    "_id" : ObjectId("5b162d10e0eafb1d6e63b460"),
    "id" : NumberLong(5372682651),
    "statuses_count" : 10599,
    "screen_name" : "用户5372682651",
    "profile_url" : "https://m.weibo.cn/u/5372682651?uid=5372682651",
    "description" : "暂无数据",
    "gender" : "f",
    "followers_count" : 80,
    "follow_count" : 1060
}
```




# 简单数据清洗

最终跑完一次爬到的数据有`3889285`，因为有大量页面会跳转到登录页面，对这些请求做一个重试效果会好些。



数据清洗对我来说真的是个头疼的问题，找了很多相关资料，最后使用了mongo的`aggregate`方法，该方法也是我第一次使用，下面是代码：

```cmd
db.getCollection('Weibo').aggregate(
    [
        {"$group" : {_id:{id:"$id",gender:"$gender"}, count:{$sum:1}}},
        {$sort:{"count":-1}},
        { $out:"result"},
    ],
    {
      allowDiskUse:true,
      cursor:{}
    }  
)
```

结果产生了一张新的表，对每个ID进行统计，并排序，如下：

```cmd
{
    "_id" : {
        "id" : NumberLong(5737668415),
        "gender" : "f"
    },
    "count" : 106701.0
}
{
    "_id" : {
        "id" : NumberLong(5909154992),
        "gender" : "m"
    },
    "count" : 72298.0
}
```



参与次数达到十万次，天呐，超级真爱粉，[缘来是她](https://m.weibo.cn/u/5737668415?uid=5737668415)，疯狂刷屏有没有

![](http://p8eyj0cpn.bkt.clouddn.com/%E6%B7%B1%E5%BA%A6%E6%88%AA%E5%9B%BE_%E9%80%89%E6%8B%A9%E5%8C%BA%E5%9F%9F_20180607110639.png)

好了，现在开始看看真正的数据吧。



本次共采集用户数据`3889285`条，，原始数据中男性占比`%33.68`，女性占比`%66.32`，好吧，看来女性粉丝更多；去重之后数据共有`1129035`，男性占比`%29.58`，女性占比`%70.42`，怎么看着女性粉丝还是更多呢。。



我们再来计算一个数据，亲密度大于10的粉丝共有`16486`位，其中男性占比`%24.05`，女性占比`%75.95`，于是有下面这张表格。



| 亲密度     | 男性占比   | 女性占比   | 粉丝总数    |
| :------ | ------ | ------ | ------- |
| 大于0     | 29.58% | 70.42% | 1129035 |
| 大于10    | 24.05% | 75.95% | 16486   |
| 大于50    | 32.77% | 67.23% | 4285    |
| 大于100   | 36.77% | 63.23% | 2578    |
| 大于1000  | 40.18% | 59.82% | 331     |
| 大于10000 | 37.5%  | 62.5%  | 24      |
| Top10   | 30.00% | 70.00% | 10      |

这个数据挺有意思的，画张表瞧瞧

![](https://i.loli.net/2018/06/10/5b1cd33ba3031.png)



粉丝昵称词云

![](https://i.loli.net/2018/06/10/5b1cd793e1520.png)

（感谢BDP）


# 结论

看了这些数据，相信大家自己心中已经有了答案。

胡歌作为一个玉树临风、 英俊潇洒、 风流倜傥、 一表人才、 高大威猛、 气宇不凡、 温文尔雅、 品貌非凡、 仪表不凡的男人，女粉丝比较多是很正常的。但是为啥大家都会有一种男粉丝比女粉丝多的错觉呢，我觉得是对比产生的感觉。我拿胡歌与其他小鲜肉作对比，肯定会跟欣赏胡歌。你说呢？

本文并不是为了证明什么，只是作为一名普通粉丝想去看看更多东西。其实本次数据爬取有很多地方需要优化，大家不用太过当真。如果你有更好的分析数据的想法，可以联系我。

>老大镇楼

![](http://wx1.sinaimg.cn/large/48e837eegy1fe2dmkfsquj21tq1tqu0x.jpg)

















