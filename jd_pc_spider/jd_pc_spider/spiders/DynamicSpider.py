#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: DynamicSpider.py
@time: 08/11/2017 10:48
"""

import re
import scrapy
from scrapy_redis.spiders import RedisMixin
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import logging

from jd_pc_spider.items import JdPcItem


def process_value(value):
    if re.match(r'^https://item.jd.com/[\d]*.html$', value):
        return value


def process_list_value(value):
    if re.match(r'^https://list.jd.com/list.html?cat=9987,653,655', value):
        return value


class DynamicSpider(RedisMixin, CrawlSpider):
    name = "dynamicSpider"
    pattern = re.compile("\r\n|\n\r|\r|\n")
    # start_urls = ["https://item.jd.com/3652063.html"]
    start_urls = ['https://list.jd.com/list.html?cat=9987,653,655']

    rules = [
        Rule(LinkExtractor(allow_domains=["jd.com"], process_value=process_value), callback='parse_detail', follow=True),
        # Rule(LinkExtractor(allow_domains=["jd.com"], restrict_xpaths='//a[@class="pn-next"]'), callback='parse', follow=True)
        Rule(LinkExtractor(allow_domains=["jd.com"], process_value=process_list_value), callback='parse', follow=True)
    ]

    def start_requests(self):
        for url in self.start_urls:
            if url.startswith("http://") or url.startswith("https://"):
                # yield Request(url=line, callback=self.parse, dont_filter=False, meta=self.meta)
                yield self.make_request_from_data(url)
            else:
                url = "http://" + url
                # yield Request(url=line, callback=self.parse, dont_filter=False, meta=self.meta)
                yield self.make_request_from_data(url)

    def make_requests_from_url(self, url):
        """ This method is deprecated. """
        # self.log("calling host spider's make_requests_from_url function", level=logging.INFO)
        return scrapy.Request(url, dont_filter=False)


    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(DynamicSpider, self).from_crawler(crawler, *args, **kwargs)
        obj.setup_redis(crawler)
        return obj

    def parse_detail(self, response):
        self.log("enter DynamicSpider parse_detail", level=logging.INFO)
        title = response.xpath("/html/head/title/text()").extract()[0]
        keywords = response.xpath('//meta[@name="keywords"]/@content').extract()[0]
        description = response.xpath('//meta[@name="description"]/@content').extract()[0]
        ware_id = 0
        price = 0.0
        screen_resolution = ""
        back_camera = ""
        front_camera = ""
        core_num = ""
        frequency = ""
        try:
            price_str = response.xpath('//span[@class="p-price"]/span[2]/text()').extract()[0]
            price = float(price_str)
        except IndexError as ie:
            self.log("There is no price info", level=logging.ERROR)
            pass

        try:
            result = re.search(r"([\d]+)", response.url)
            ware_id_str = result.group(1) if result is not None else "0"
            ware_id = int(ware_id_str)
        except IndexError as ie:
            self.log("There is no ware_id info", level=logging.ERROR)
            pass

        li_list = response.xpath("//div[@class='p-parameter']/ul[@class='parameter1 p-parameter-list']/li")
        for li_item in li_list:
            try:
                if len(li_item.xpath("./i[@class='i-phone']")) != 0:
                    screen_resolution = li_item.xpath("./div/p/text()").extract()[0]
                elif len(li_item.xpath("./i[@class='i-camera']")) != 0:
                    back_camera = li_item.xpath("./div/p[1]/text()").extract()[0]
                    front_camera = li_item.xpath("./div/p[2]/text()").extract()[0]
                elif len(li_item.xpath("./i[@class='i-cpu']")) != 0:
                    core_num = li_item.xpath("./div/p[1]/text()").extract()[0]
                    frequency = li_item.xpath("./div/p[2]/text()").extract()[0]
            except IndexError as ie:
                pass

        brand = ""
        try:
            brand = response.xpath("//div[@class='p-parameter']/ul[@class='p-parameter-list']/li/@title").extract()[0]
        except IndexError as ie:
            self.log("brand IndexError")
            pass

        li_list = response.xpath("//div[@class='p-parameter']/ul[@class='parameter2 p-parameter-list']/li")
        content_dict = dict()
        for li_item in li_list:
            try:
                content = li_item.xpath("./text()").extract()[0]
                key, value = content.split(u"：")
                key = key.encode('utf-8')
                value = value.encode('utf-8')
                # print key, value
                # print type(key)
                # print type(value)
                content_dict[key] = value
            except IndexError as ie:
                self.log("content IndexError")
                pass

        item = JdPcItem()
        item["url"] = response.url
        item["ware_id"] = ware_id
        item["title"] = title
        item["keywords"] = keywords
        item["description"] = description
        item["price"] = price
        item["screen_resolution"] = screen_resolution
        item["back_camera"] = back_camera
        item["front_camera"] = front_camera
        item["core_num"] = core_num
        item["frequency"] = frequency
        item["brand"] = brand
        item["content"] = content_dict

        yield item
