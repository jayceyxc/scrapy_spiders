# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    rating = scrapy.Field()
    rating_sum = scrapy.Field()
    director = scrapy.Field()
    # scriptwriter = scrapy.Field()
    actor = scrapy.Field()
    movie_type = scrapy.Field()
    # country = scrapy.Field()
    # language = scrapy.Field()
    show_time = scrapy.Field()
    duration = scrapy.Field()
    pass
