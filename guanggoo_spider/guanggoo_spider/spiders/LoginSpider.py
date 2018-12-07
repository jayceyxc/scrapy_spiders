#!/usr/bin/env python3
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm
@file: LoginSpider.py
@time: 2018/6/11 17:22
"""

import scrapy
from faker import Factory


class LoginSpider(scrapy.Spider):
    name = 'login_spider'
    start_urls = ['http://www.guanggoo.com/login']

    faker_factory = Factory.create()

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'www.guanggoo.com',
        'User-Agent': faker_factory.user_agent()
    }

    formdata = {
        'form_email': 'jayce123@163.com',
        'form_password': 'yuxc870704',
    }

    def start_requests(self):
        return [scrapy.Request(url='http://www.guanggoo.com/login', headers=self.headers, meta={'cookiejar':1}, callback=self.parse_login)]

    def parse_login(self, response):
        xsrf = response.xpath("//input[@name='_xsrf']/@value").extract()[0]
        return scrapy.FormRequest.from_response(
            response,
            formdata={'email':'jayce123@163.com', 'password':'beckham178', '_xsrf':xsrf},
            # formdata={'email': 'jayce123@163.com', 'password': 'beckham178'},
            meta={'cookiejar': response.meta['cookiejar']},
            callback=self.after_login
        )

    def after_login(self, response):
        print(self.start_urls)
        # print(response.text)
        print(response.url)
        print(response.text)
        print("response status: {0}".format(response.status))
        print("response headers: {0}".format(response.headers))
        print("request cookies: {0}".format(response.request.cookies))
        print("request headers: {0}".format(response.request.headers))
        return scrapy.Request(url='http://www.guanggoo.com/setting',
                              meta={'cookiejar': response.meta['cookiejar']},
                              headers=self.headers,
                              callback=self.parse_settings)

    def parse_settings(self, response):
        print(response.text)
        print(response.status)
        print(response.url)
