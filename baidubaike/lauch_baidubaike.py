#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-12-10 11:05
# @Author  : yuxuecheng
# @Contact : yuxuecheng@xinluomed.com
# @Site    : 
# @File    : lauch_baidubaike.py
# @Software: PyCharm
# @Description 启动百度百科爬虫

from scrapy import cmdline

cmdline.execute("scrapy crawl baiduBaikeSpider".split())
