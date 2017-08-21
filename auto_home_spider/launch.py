#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: launch.py.py
@time: 19/08/2017 13:03
"""

from scrapy import cmdline

cmdline.execute("scrapy crawl autohomeSpider".split())
