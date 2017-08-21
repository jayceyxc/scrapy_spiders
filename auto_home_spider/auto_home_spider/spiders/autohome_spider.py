#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: autohome_spider.py
@time: 19/08/2017 13:03
"""


import chardet
import scrapy
import logging

from auto_home_spider.items import CarItem
import start_url

enable_coding = ['UTF-8', 'GBK', 'GB2312']


# return a  fixed unicode code
# beause the response_encoding may be wrong
def encode_content(response_encoding, content, response_body):
    if response_encoding.upper() in enable_coding:
        return content
    if response_body:
        ty = chardet.detect(response_body)['encoding']
        try:
            fix_content = content.encode(response_encoding).decode("GBK", 'xmlcharrefreplace')
        except Exception:
            fix_content = content.encode(response_encoding).decode("GBK", 'ignore')
        return fix_content


class AutohomeSpider(scrapy.Spider):
    name = "autohomeSpider"
    mongo_uri = "127.0.0.1:19191"
    mongo_db = "autohome"
    collection_name = "car_items"

    price_url_pattern = "http://car.autohome.com.cn/price/list-%d_%d-0-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html"
    price_pair = [(0, 5),(5, 8),(8, 10),(10, 15), (15, 20), (20, 25), (25, 35),(35, 50), (50, 100), (100, 0)]

    pailiang_url_list = [
        "http://car.autohome.com.cn/price/list-0-0-0_1.0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        "http://car.autohome.com.cn/price/list-0-0-1.1_1.6-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        "http://car.autohome.com.cn/price/list-0-0-1.7_2.0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        "http://car.autohome.com.cn/price/list-0-0-2.1_2.5-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        "http://car.autohome.com.cn/price/list-0-0-2.6_3.0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        "http://car.autohome.com.cn/price/list-0-0-3.1_4.0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        "http://car.autohome.com.cn/price/list-0-0-4.0_0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
    ]

    biansuxiang_url_list = [
        "http://car.autohome.com.cn/price/list-0-0-0-0-1-0-0-0-0-0-0-0-0-0-0-1.html",
        "http://car.autohome.com.cn/price/list-0-0-0-0-101-0-0-0-0-0-0-0-0-0-0-1.html",
        "http://car.autohome.com.cn/price/list-0-0-0-0-9-0-0-0-0-0-0-0-0-0-0-1.html",
    ]

    chexing_url_dict = {
        u"微型车": "http://car.autohome.com.cn/price/list-0-1-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"小型车": "http://car.autohome.com.cn/price/list-0-2-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"紧凑型车": "http://car.autohome.com.cn/price/list-0-3-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"中型车": "http://car.autohome.com.cn/price/list-0-4-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"中大型车": "http://car.autohome.com.cn/price/list-0-5-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"大型车": "http://car.autohome.com.cn/price/list-0-6-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"跑车": "http://car.autohome.com.cn/price/list-0-7-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"MPV": "http://car.autohome.com.cn/price/list-0-8-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"SUV":"http://car.autohome.com.cn/price/list-0-9-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"微面": "http://car.autohome.com.cn/price/list-0-11-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"微卡": "http://car.autohome.com.cn/price/list-0-12-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"轻客": "http://car.autohome.com.cn/price/list-0-13-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"皮卡": "http://car.autohome.com.cn/price/list-0-14-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
    }

    def start_requests(self):
        """
        for price_range in self.price_pair:
            url = self.price_url_pattern % (price_range[0], price_range[1])
            yield scrapy.Request(url=url, callback=self.parse)
        for pailiang_url in self.pailiang_url_list:
            yield scrapy.Request(url=pailiang_url, callback=self.parse)

        for biansuxiang_url in self.biansuxiang_url_list:
            yield scrapy.Request(url=biansuxiang_url, callback=self.parse)

        for chexing_url in self.chexing_url_dict.values():
            yield scrapy.Request(url=chexing_url, callback=self.parse)
        """
        for url in start_url.auto_home_start_urls:
            yield  scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # series
        series_div_list = response.xpath("//div[@class='tab-content-item current']/div[@class='list-cont']")
        for div_item in series_div_list:
            try:
                url = div_item.xpath("./div[@class='list-cont-bg']/div[@class='list-cont-main']/div[@class='main-title']/a/@href").extract()[0]
                url = "car.autohome.com.cn" + url
                url = url.split("#")[0]
                title = div_item.xpath("./div[@class='list-cont-bg']/div[@class='list-cont-main']/div[@class='main-title']/a/text()").extract()[0]
                car_item = CarItem()
                car_item["refer"] = response.url
                car_item["url"] = url
                car_item["title"] = title
                yield car_item
            except IndexError as ie:
                pass

        # spec
        spec_div_list = response.xpath("//div[@class='tab-content-item current']/div[@class='intervalcont fn-hide']")
        for spec_div in spec_div_list:
            interval_div_list = spec_div.xpath("./div[@class='interval01']")
            for interval_div in interval_div_list:
                spec_car_list = interval_div.xpath("./ul[@class='interval01-list']/li")
                for spec_car in spec_car_list:
                    try:
                        url = spec_car.xpath("./div[@class='interval01-list-cars']/div[@class='interval01-list-cars-infor']/p[1]/a/@href").extract()[0]
                        url = url.lstrip("/").split("#")[0].rstrip("/")
                        title = spec_car.xpath("./div[@class='interval01-list-cars']/div[@class='interval01-list-cars-infor']/p[1]/a/text()").extract()[0]
                        car_item = CarItem()
                        car_item["refer"] = response.url
                        car_item["url"] = url
                        car_item["title"] = title
                        yield car_item
                    except IndexError as ie:
                        pass

        # next page
        try:
            next_page = response.xpath("//div[@class='price-page']/div[@class='page']/a[@class='page-item-next']/@href").extract()[0]
            next_page = "http://car.autohome.com.cn" + next_page
            yield scrapy.Request(url=next_page, callback=self.parse)
        except IndexError as ie:
            self.log("this is last page, url is: %s" % response.url, level=logging.WARN)
            pass
