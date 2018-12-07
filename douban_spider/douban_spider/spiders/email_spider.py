#!/usr/bin/env python3
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm
@file: email_spider.py
@time: 2018/6/14 13:17
"""

import scrapy
from urllib import parse
from faker import Factory

from ..items import EmailItem


class EmailSpider(scrapy.Spider):
    name = 'email_spider'
    allowed_domains = ['accounts.douban.com', 'douban.com']
    start_urls = [
        'https://www.douban.com/'
    ]
    faker_factory = Factory.create()

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Host': 'accounts.douban.com',
        'User-Agent': faker_factory.user_agent()
    }

    formdata = {
        'form_email': 'jayce123@163.com',
        'form_password': 'yuxc870704',
        # 'captcha-solution': '',
        # 'captcha-id': '',
        'login': '登录',
        'redir': 'https://www.douban.com/',
        'source': 'None'
    }

    def start_requests(self):
        return [scrapy.Request(url='https://www.douban.com/accounts/login', headers=self.headers, meta={'cookiejar':1}, callback=self.parse_login)]

    def parse_login(self, response):
        # 如果有验证码要人为处理
        print(response.body)
        print(response.text)
        if 'captcha_image' in response.text:
            print('Copy the link:')
            link = response.xpath('//img[@class="captcha_image"]/@src').extract()[0]
            print(link)
            captcha_solution = input('captcha-solution:')
            captcha_id = parse.parse_qs(parse.urlparse(link).query, True)['id']
            self.formdata['captcha-solution'] = captcha_solution
            self.formdata['captcha-id'] = captcha_id
        return [scrapy.FormRequest.from_response(response,
                                                 formdata=self.formdata,
                                                 headers=self.headers,
                                                 meta={'cookiejar': response.meta['cookiejar']},
                                                 callback=self.after_login
                                                 )]

    def after_login(self, response):
        print(response.status)
        print(response.text)
        print(response.meta['cookiejar'])
        print(response.request.cookies)
        self.headers['Host'] = 'www.douban.com'
        return scrapy.Request(url='https://www.douban.com/doumail/',
                              meta={'cookiejar': response.meta['cookiejar']},
                              headers=self.headers,
                              callback=self.parse_email)

    def parse_email(self, response):
        print(response.status)
        print(response.meta['cookiejar'])
        print(response.request.cookies)
        for item in response.xpath('//div[@class="doumail-list"]/ul/li'):
            mail = EmailItem()
            mail['sender_time'] = item.xpath('div[2]/div/span[1]/text()').extract()[0]
            mail['sender_from'] = item.xpath('div[2]/div/span[2]/text()').extract()[0]
            mail['url'] = item.xpath('div[2]/p/a/@href').extract()[0]
            mail['title'] = item.xpath('div[2]/p/a/text()').extract()[0]
            print(mail)
            yield mail