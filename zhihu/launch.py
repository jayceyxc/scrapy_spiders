#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: launch_movie.py
@time: 13/11/2017 14:25
"""

from scrapy import cmdline

cmdline.execute("scrapy crawl zhihuSpider".split())