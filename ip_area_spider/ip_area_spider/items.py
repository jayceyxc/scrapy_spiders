# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class IpAreaItem(scrapy.Item):
    # define the fields for your item here like:
    id = Field()
    kid = Field()
    prev_id = Field()
    start_ip = Field()
    end_ip = Field()
    ip = Field()
    area_name = Field()
    pass
