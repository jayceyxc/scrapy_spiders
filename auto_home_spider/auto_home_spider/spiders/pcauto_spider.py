#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: pcauto_spider.py
@time: 21/08/2017 16:27
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


class PcautoSpider(scrapy.Spider):
    name = "pcautoSpider"
    mongo_uri = "127.0.0.1:19191"
    mongo_db = "autohome"
    collection_name = "car_items"

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
        for url in start_url.pcauto_start_url:
            yield  scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # series
        series_list = response.xpath("//div[@class='lieBiao']")
        for series in series_list:
            if response.url.find("rank") > 0:
                series_name = series.xpath("./div[@class='thlieBiao']/div[@class='con']/i[@class='tit blue']/strong/a/text()").extract()[0]
                series_url = series.xpath("./div[@class='thlieBiao']/div[@class='con']/i[@class='tit blue']/strong/a/@href").extract()[0]
            else:
                series_name = series.xpath("./div[@class='thlieBiao']/div[@class='con']/div[@class='tit blue']/strong/a/text()").extract()[0]
                series_url = series.xpath("./div[@class='thlieBiao']/div[@class='con']/div[@class='tit blue']/strong/a/@href").extract()[0]
            series_url = "http://price.pcauto.com.cn" + series_url
            series_item = CarItem()
            series_item["refer"] = response.url
            series_item["url"] = series_url
            series_item["title"] = series_name
            yield series_item

            car_table = series.xpath("./div[@class='tblieBiao']/div[@class='thTab_b']/div[@class='contentdiv']/ul")
            for element in car_table:
                for row in element.xpath("./li"):
                    url = row.xpath("./i[@class='iCol1']/em/a/@href").extract()[0]
                    url = "http://price.pcauto.com.cn" + url
                    title = row.xpath("./i[@class='iCol1']/em/a/text()").extract()[0]
                    title = u" ".join([series_name, title])
                    car_item = CarItem()
                    car_item["refer"] = response.url
                    car_item["url"] = url
                    car_item["title"] = title
                    yield car_item

        # next page
        try:
            next_page = response.xpath("//div[@class='pcauto_page']/a[@class='next']/@href").extract()[0]
            next_page = "http://price.pcauto.com.cn" + next_page
            yield scrapy.Request(url=next_page, callback=self.parse)
        except IndexError as ie:
            self.log("this is last page, url is: %s" % response.url, level=logging.WARN)
            pass