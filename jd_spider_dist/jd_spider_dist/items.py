# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class JdItem(scrapy.Item):
    # 京东商品信息
    id = Field() # 商品ID
    name = Field() # 商品名称
    price = Field() # 商品价格
    category = Field()  # 商品分类
    total_comments = Field() # 总评价数
    good_comments = Field() # 好评数
    normal_comments = Field() # 普通评价数
    bad_comments = Field() # 差评数

    def __repr__(self):
        return "id: %s, name: %s" % (self["id"], self["name"])


class MobileItem(JdItem):
    shop_id = Field() # 手机的店铺ID
