#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: qunar_spider.py
@time: 09/09/2017 11:59
"""

import chardet
import scrapy
import logging
import json

from realestate_spider.items import RealestateItem
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


class QunarSpider(scrapy.Spider):
    name = "qunarSpider"
    mongo_uri = "127.0.0.1:19191"
    mongo_db = "tour"
    collection_name = "qunar_items"
    start_url_pattern = "http://piao.qunar.com/ticket/list.htm?keyword=%s"
    keywords_list = [u"武汉", u"上海"]

    def start_requests(self):
        for keyword in self.keywords_list:
            # self.log("parse url:{0}".format(response.url), level=logging.INFO)
            url = self.start_url_pattern % keyword
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.log("in parse_ershoufang: {0}".format(response.url), level=logging.INFO)
        house_list = response.xpath("//ul[@class='sellListContent']/li")
        for house_item in house_list:
            self.log(house_item, level=logging.INFO)
            try:
                total_price = house_item.xpath("./div[@class='info clear']/div[@class='priceInfo']/div[@class='totalPrice']/span/text()").extract()[0]
                unit_price = house_item.xpath("./div[@class='info clear']/div[@class='priceInfo']/div[@class='unitPrice']/span/text()").extract()[0]
                url = house_item.xpath("./a[@class='img ']/@href").extract()[0]
                if not url.startswith("https://cs.lianjia.com"):
                    url = "https://cs.lianjia.com" + url
                title = house_item.xpath("./div[@class='info clear']/div[@class='title']/a/text()").extract()[0]
                region = "未知"
                try:
                    region = house_item.xpath("./div[@class='info clear']/div[@class='address']/div[@class='houseInfo']/a/text()").extract()[0]
                except ValueError as ve:
                    self.log(ve.message, level=logging.WARN)
                    pass
                realestate_item = RealestateItem()
                realestate_item["refer"] = response.url
                realestate_item["url"] = url
                if total_price.isdigit():
                    realestate_item["price"] = float(total_price)
                else:
                    realestate_item["price"] = total_price
                realestate_item["region"] = region.strip(u"\xc2\xa0")
                realestate_item["bedrooms"] = 0
                realestate_item["title"] = title.strip(u"\xc2\xa0")
                realestate_item["area"] = 0
                realestate_item["unit_price"] = unit_price
                yield realestate_item
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
                pass

        # other page
        try:
            page_info_str = response.xpath("//div[@class='page-box house-lst-page-box']/@page-data").extract()[0]
            page_url_format = response.xpath("//div[@class='page-box house-lst-page-box']/@page-url").extract()[0]
            page_info_dict = json.loads(page_info_str)
            total_page_num = page_info_dict['totalPage']
            cur_page_num = page_info_dict['curPage']
            if cur_page_num == 1:
                for i in range(2, total_page_num + 1, 1):
                    next_page = "https://cs.lianjia.com" + page_url_format.replace("{page}", str(i))
                    self.log("next page: {0}".format(next_page), level=logging.INFO)
                    yield scrapy.Request(url=next_page, callback=self.parse_ershoufang)
        except IndexError as ie:
            self.log(ie.message, level=logging.WARN)
            self.log("this is last page, url is: %s" % response.url, level=logging.WARN)
            pass

