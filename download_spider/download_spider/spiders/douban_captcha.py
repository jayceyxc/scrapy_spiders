#!/usr/bin/env python3
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: douban_captcha.py
@time: 14/11/2017 15:23
"""

import sys
import os
import logging
import re
import scrapy

from download_spider.download_spider.items import DownloadItem


class DoubanCaptcha(scrapy.Spider):
    name = "douban_captcha"
    url = "https://www.douban.com"

    headers = {
        "Accept-Language": "zh-CN",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
        "Referer": "www.douban.com",
        "DNT": "1",
        "Connection": "Keep-Alive"
    }

    def __init__(self, **kwargs):
        super(DoubanCaptcha, self).__init__(**kwargs)
        self.download_path = os.path.join(os.getcwd(), "douban_captcha")
        self.log("download_path: %s" % self.download_path, level=logging.INFO)

    def start_requests(self):
        for page_index in range(1, 10000, 1):
            yield scrapy.Request(url=DoubanCaptcha.url, callback=self.parse, dont_filter=True, headers=DoubanCaptcha.headers)

    def parse(self, response):
        self.log("status code: %d" % response.status, level=logging.DEBUG)
        if response.status == 200:
            try:
                captcha_image_url = response.xpath('//img[@id="captcha_image"]/@src').extract()[0]
                self.log("captcha_image_url: %s" % captcha_image_url, level=logging.DEBUG)
                result = re.search(r'id=(.*):', captcha_image_url)
                if result is not None:
                    id = result.group(1)

                    item = DownloadItem()
                    item['url'] = captcha_image_url
                    item['filename'] = os.path.join(self.download_path, id)

                    self.log("item info: %s" % (dict(item)), level=logging.INFO)
                    yield item
                else:
                    self.log("result is None", level=logging.ERROR)
            except IndexError as ie:
                self.log("Index error", level=logging.ERROR)
                pass
        else:
            self.log("status code is not 200", level=logging.ERROR)
