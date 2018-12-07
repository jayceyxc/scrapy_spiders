# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdPcItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    ware_id = scrapy.Field()
    title = scrapy.Field()
    keywords = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()
    screen_resolution = scrapy.Field()
    back_camera = scrapy.Field()
    front_camera = scrapy.Field()
    core_num = scrapy.Field()
    frequency = scrapy.Field()
    brand = scrapy.Field()
    content = scrapy.Field()



