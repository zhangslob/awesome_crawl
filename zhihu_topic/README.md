# [知乎所有问题](./zhihu_topic/spiders)


从[话题广场](https://www.zhihu.com/topics)出发，先采集所有知乎的子话题，如


![](https://i.imgur.com/TC89LlB.png)

解析之后把所有的话题ID保存到redis中，再新建爬虫去采集该话题下所有的问题（这部分基本完工，但是还没测试过）。

