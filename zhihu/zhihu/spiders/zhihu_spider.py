#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: zhihu_spider.py
@time: 13/11/2017 14:27
"""
import logging
import time
import urllib2

import scrapy
from scrapy.http import Request
from scrapy_redis.spiders import RedisMixin
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from zhihu.items import ZhihuItem


class ZhihuSpider(RedisMixin, CrawlSpider):
    name = "zhihuSpider"
    allowed_domains = ["zhihu.com"]
    start_urls = [
        "https://www.zhihu.com"
    ]
    rules = (
        Rule(LinkExtractor(allow=('/question/\d+#.*?',)), callback='parse_page', follow=True),
        Rule(LinkExtractor(allow=('/question/\d+',)), callback='parse_page', follow=True),
    )
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Referer": "https://www.zhihu.com/"
    }

    def start_requests(self):
        self.log("start_requests", level=logging.INFO)
        yield scrapy.Request(
            # url='https://www.zhihu.com/#signin',
            url='https://www.zhihu.com',
            callback=self.post_login,
            meta={'cookiejar':1},
            dont_filter=True,
            headers=self.headers
        )

    def post_login(self, response):
        self.log('Preparing login', level=logging.INFO)
        self.log('cookiejar: %s' % response.meta['cookiejar'], level=logging.DEBUG)
        # 下面这句话用于抓取请求网页后返回网页中的_xsrf字段的文字, 用于成功提交表单
        xsrf = response.xpath('//input[@name="_xsrf"]/@value').extract()[0]
        self.log("xsrf: %s" % xsrf, level=logging.INFO)
        captcha_url = "https://www.zhihu.com/captcha.gif?r=%d&type=login" % (time.time() * 1000)
        captcha_res = urllib2.urlopen(url=captcha_url)
        captcha_data = captcha_res.read()
        with open("1.gif", mode="wb") as file:
            file.write(captcha_data)

        yanzhengma = raw_input("captcha: ")
        self.log("captcha: %s" % yanzhengma, level=logging.INFO)

        yield scrapy.FormRequest.from_response(
            response,
            meta={'cookiejar': response.meta['cookiejar']},  # 注意这里cookie的获取
            formdata={
                '_xsrf': xsrf,
                'email': 'jayce123@163.com',
                'password': 'yuxc870704',
                # 'captcha_type': 'cn'
                "captcha": yanzhengma
            },
            headers=self.headers,
            dont_filter=True,
            callback=self.after_login,
            url='login/email'
        )

    def after_login(self, response):
        self.log("after_logging, url: %s" % response.url, level=logging.INFO)
        self.log("text of response", level=logging.INFO)
        self.log(response.body, level=logging.INFO)
        for url in self.start_urls:
            # yield self.make_requests_from_url(url)
            yield scrapy.Request(url=url, dont_filter=True, headers=self.headers, meta={'cookiejar': response.meta['cookiejar']})

    def parse_page(self, response):
        name = ""
        title = ""
        description = ""
        answer = ""
        try:
            name = response.xpath('//span[@class="name"]/text()').extract()[0]
            title = response.xpath('//h2[@class="zm-item-title zm-editable-content"]/text()').extract()[0]
            description = response.xpath('//div[@class="zm-editable-content"]/text()').extract()[0]
            answer = response.xpath('//div[@class=" zm-editable-content clearfix"]/text()').extract()[0]
            self.log("name: %s" % name, level=logging.INFO)
        except IndexError as ie:
            pass

        item = ZhihuItem()
        item['url'] = response.url
        item['name'] = name
        item['title'] = title
        item['description'] = description
        item['answer'] = answer
        yield item

