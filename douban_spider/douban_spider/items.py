#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    # define the fields for your item here like:
    movie_id = scrapy.Field()
    movie_name = scrapy.Field()
    movie_year = scrapy.Field()
    rating_average = scrapy.Field()
    rating_sum = scrapy.Field()
    directors = scrapy.Field()
    actors = scrapy.Field()
    categories = scrapy.Field()
    show_time = scrapy.Field()
    duration = scrapy.Field()
    keywords = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    pass


class EmailItem(scrapy.Item):
    sender_time = scrapy.Field()
    sender_from = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()