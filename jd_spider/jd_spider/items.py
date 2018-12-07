# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    number = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    publisher = scrapy.Field()
    price = scrapy.Field()
    jd_price = scrapy.Field()
    pass


class MobileItem(scrapy.Item):
    # define the fields for your item here like, 有些手机可能没有所有参数
    ware_id = scrapy.Field()
    good_name = scrapy.Field()
    jd_price = scrapy.Field()
    category_id = scrapy.Field()
    shop_id = scrapy.Field()
    color_set = scrapy.Field()
    capacity_set = scrapy.Field()
    good_url = scrapy.Field()
    total_comments = scrapy.Field()
    good_comments = scrapy.Field()
    normal_comments = scrapy.Field()
    bad_comments = scrapy.Field()
    RAM = scrapy.Field()
    ROM = scrapy.Field()
    # 操作系统类型
    OS = scrapy.Field()
    # CPU型号
    CPU = scrapy.Field()
    # 分辨率
    resolution = scrapy.Field()
    # 屏幕尺寸
    display = scrapy.Field()
    # 上市时间
    year_to_market = scrapy.Field()
    month_to_market = scrapy.Field()
    # 机身的长度、宽度和厚度
    length = scrapy.Field()
    width = scrapy.Field()
    thickness = scrapy.Field()
    # 机身重量
    weight = scrapy.Field()
    # 入网型号
    net_in_model = scrapy.Field()
    # 前置摄像头
    front_camera = scrapy.Field()
    # 后置摄像头
    rear_camera = scrapy.Field()
    # 品牌
    brand = scrapy.Field()
    # 型号
    model = scrapy.Field()
    # 颜色
    color = scrapy.Field()



