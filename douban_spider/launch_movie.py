#!/usr/bin/env python3
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: launch_movie.py
@time: 14/11/2017 15:46
"""

from scrapy import cmdline

cmdline.execute("scrapy crawl moviespider".split())