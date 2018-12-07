#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: launch_mobilespider.py
@time: 08/09/2017 18:04
"""

from scrapy import cmdline

cmdline.execute("scrapy crawl mobilespider -s LOG_FILE=scrapy.log".split())