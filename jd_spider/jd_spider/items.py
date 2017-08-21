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
