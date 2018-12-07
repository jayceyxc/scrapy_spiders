#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: leju_spider.py
@time: 12/09/2017 11:53
"""

import chardet
import scrapy
import logging
import json
import re

from realestate_spider.items import ResoldApartmentItem, LoufanItem, RentHouseItem

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


class LejuSpider(scrapy.Spider):
    name = "lejuSpider"
    mongo_uri = "127.0.0.1:19191"
    mongo_db = "realestate"
    collection_name = "leju_items"
    number_pattern = re.compile("([\d]+)")

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
        for url in start_url.leju_start_url:
            # self.log("parse url:{0}".format(response.url), level=logging.INFO)
            if url.find("zufang") != -1:
                yield scrapy.Request(url=url, callback=self.parse_rent)
            elif url.find("esf") != -1:
                yield scrapy.Request(url=url, callback=self.parse_ershoufang)
            else:
                yield scrapy.Request(url=url, callback=self.parse_loupan)
            # yield scrapy.Request(url=url, callback=self.parse)

    def parse_rent(self, response):
        self.log("parse_rent: %s" % response.url, level=logging.WARN)
        house_list = response.xpath("//div[@class='full-list-wrap full-list-wrapNew']/div")
        for house_item in house_list:
            try:
                rent_price = house_item.xpath("./div/div[@class='col-extra']/div[@class='sfy-right']/div[@class='one']/span[@class='georgia']/text()").extract()[0].strip()
                billing_type = "未知"
                try:
                    billing_type = house_item.xpath("./div/div[@class='col-extra']/div[@class='sfy-right']/div[@class='two mb5']/text()").extract()[0].strip()
                except IndexError as ie:
                    pass
                build_year = 0
                try:
                    temp_value = house_item.xpath("./div/div[@class='col-main']/div/div[@class='house-position']/span[@class='build-year']/text()").extract()[0]
                    build_result = self.number_pattern.search(temp_value)
                    if build_result is not None:
                        build_year = int(build_result.group(1))
                except IndexError as ie:
                    pass
                url = house_item.xpath("./@linkto").extract()[0]
                url = url.split("#")[0]
                if not url.startswith("http://cs.zufang.leju.com"):
                    url = "http://cs.zufang.leju.com" + url
                title = house_item.xpath("./div/div[@class='col-main']/div[@class='main-wrap']/h3[@class='house-title']/a/@title").extract()[0].strip()
                community = "未知"
                try:
                    community = house_item.xpath("./div/div[@class='col-main']/div/div[@class='house-info txt-cut']/a/text()").extract()[0].strip()
                except ValueError as ve:
                    self.log(ve.message, level=logging.WARN)
                    pass

                span_list = house_item.xpath("./div/div[@class='col-main']/div/div[@class='house-info txt-cut']/span")
                bedrooms = 0
                area = 0
                rent_type = "未知"
                decoration = "未知"
                for span_item in span_list:
                    content = span_item.xpath("./text()").extract()[0].strip()
                    if content.find(u"室") != -1:
                        bedrooms = int(content[:content.find(u"室")])
                    elif content.find(u"平米") != -1:
                        area_result = self.number_pattern.search(content)
                        if area_result is not None:
                            area = float(area_result.group(1))
                    elif content.find(u"租") != -1:
                        rent_type = content
                    else:
                        decoration = content
                region = "未知"
                try:
                    region = house_item.xpath("./div/div[@class='col-main']/div/div[@class='house-position']/span[@class='region']/a/text()").extract()[0]
                except IndexError as ie:
                    pass
                span_list2 = house_item.xpath("./div/div[@class='col-main']/div/div[@class='house-position']/span[not(@class)]")
                floor = "未知"
                orientation = "未知"
                for span_item in span_list2:
                    content = span_item.xpath("./text()").extract()[0].strip()
                    if content.find(u"层") != -1:
                        floor = content
                    else:
                        orientation = content
                renthouse_item = RentHouseItem()
                renthouse_item["refer"] = response.url
                renthouse_item["url"] = url
                if rent_price.isdigit():
                    renthouse_item["rent_price"] = float(rent_price)
                else:
                    renthouse_item["rent_price"] = rent_price
                renthouse_item["billing_type"] = billing_type
                renthouse_item["rent_type"] = rent_type
                renthouse_item["region"] = region
                renthouse_item["community"] = community
                renthouse_item["bedrooms"] = bedrooms
                renthouse_item["title"] = title
                renthouse_item["area"] = area
                renthouse_item["orientation"] = orientation
                renthouse_item["floor"] = floor
                renthouse_item["decoration"] = decoration
                renthouse_item["year"] = build_year

                yield renthouse_item
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
                pass

        # other page
        try:
            next_page = response.xpath("//div[@class='p']/div[@class='page']/a[@class='next']/@href").extract()[0]
            self.log("next page: {0}".format(next_page), level=logging.INFO)
            yield scrapy.Request(url=next_page, callback=self.parse_rent)
        except IndexError as ie:
            self.log(ie.message, level=logging.WARN)
            self.log("this is last page, url is: %s" % response.url, level=logging.WARN)
            pass

    def parse_loupan(self, response):
        self.log("parse_loupan: %s" % response.url, level=logging.WARN)
        div_list = response.xpath("//div[@id='ZT_searchBox']/div[@class='b_card']")
        for div_item in div_list:
            try:
                unit_price = "尚未公布"
                try:
                    div_item.xpath("./div[@class='b_infoBox']/h2[@class='nonow']")
                    unit_price = div_item.xpath("./div[@class='b_infoBox']/h3/strong/text()").extract()[0]
                except IndexError as ie:
                    try:
                        unit_price = div_item.xpath("./div[@class='b_infoBox']/h2/strong/text()").extract()[0]
                    except IndexError as ie:
                        pass

                url = div_item.xpath("./div[@class='b_imgBox']/a/@href").extract()[0]
                url = url.split("#")[0]
                if not url.startswith("http://house.leju.com"):
                    url = "http://house.leju.com" + url
                community = "未知"
                try:
                    community = div_item.xpath("./div[@class='b_titBox']/h2/a/text()").extract()[0].strip()
                except ValueError as ve:
                    self.log(ve.message, level=logging.WARN)
                    pass
                title = community
                region = "未知"
                try:
                    h3_list = div_item.xpath("./div[@class='b_titBox']/h3")
                    for h3_item in h3_list:
                        content = h3_item.xpath("./text()").extract()[0]
                        if content.startswith('['):
                            region = content.split(']')[0].lstrip('[').split('-')[0]
                except IndexError as ie:
                    self.log(ie.message, level=logging.WARN)
                    pass

                loufan_item = LoufanItem()
                loufan_item["refer"] = response.url
                loufan_item["url"] = url
                loufan_item["unit_price"] = unit_price
                loufan_item["region"] = region.strip()
                loufan_item["title"] = title.strip()
                loufan_item["community"] = community
                yield loufan_item
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
                pass

        # other page
        try:
            next_page = response.xpath("//div[@class='b_pages clearfix']/div[@class='b_pages clearfix']/a[@class='next']/@href").extract()[0]
            self.log("next page: {0}".format(next_page), level=logging.INFO)
            yield scrapy.Request(url=next_page, callback=self.parse_loupan)
        except IndexError as ie:
            self.log(ie.message, level=logging.WARN)
            self.log("this is last page, url is: %s" % response.url, level=logging.WARN)
            pass

    def parse_ershoufang(self, response):
        self.log("parse_ershoufang: %s" % response.url, level=logging.WARN)
        house_list = response.xpath("//div[@class='full-list-wrap full-list-wrapNew']/div")
        for house_item in house_list:
            # self.log(house_item, level=logging.INFO)
            try:
                total_price = house_item.xpath("./div/div[@class='col-extra']/div[@class='sfy-right']/div[@class='one']/span[@class='georgia']/text()").extract()[0].strip()
                unit_price = house_item.xpath("./div/div[@class='col-extra']/div[@class='sfy-right']/div[@class='two mb5']/text()").extract()[0].strip()
                url = house_item.xpath("./@linkto").extract()[0]
                url = url.split("#")[0]
                if not url.startswith("http://cs.esf.leju.com"):
                    url = "http://cs.esf.leju.com" + url
                title = house_item.xpath("./div/div[@class='col-main']/div[@class='main-wrap']/h3[@class='house-title']/a/@title").extract()[0].strip()
                community = "未知"
                try:
                    community = house_item.xpath("./div/div[@class='col-main']/div/div[@class='house-info txt-cut']/a/text()").extract()[0].strip()
                except ValueError as ve:
                    self.log(ve.message, level=logging.WARN)
                    pass

                span_list = house_item.xpath("./div/div[@class='col-main']/div/div[@class='house-info txt-cut']/span")
                bedrooms = 0
                area = 0
                orientation = "未知"
                for span_item in span_list:
                    content = span_item.xpath("./text()").extract()[0].strip()
                    if content.find(u"室") != -1:
                        bedrooms = int(content[:content.find(u"室")])
                    elif content.find(u"平米") != -1:
                        area_result = self.number_pattern.search(content)
                        if area_result is not None:
                            area = float(area_result.group(1))
                    else:
                        orientation = content
                region = "未知"
                try:
                    region = house_item.xpath("./div/div[@class='col-main']/div/div[@class='house-position']/span[@class='region']/a/text()").extract()[0]
                except IndexError as ie:
                    pass
                span_list2 = house_item.xpath("./div/div[@class='col-main']/div/div[@class='house-position']/span[not(@class)]")
                floor = "未知"
                decoration = "未知"
                for span_item in span_list2:
                    content = span_item.xpath("./text()").extract()[0].strip()
                    if content.find(u"层") != -1:
                        floor = content
                    else:
                        decoration = content

                build_year = 0
                try:
                    temp_value = house_item.xpath("./div/div[@class='col-main']/div/div[@class='house-position']/span[@class='build-year']/text()").extract()[0]
                    build_result = self.number_pattern.search(temp_value)
                    if build_result is not None:
                        build_year = int(build_result.group(1))
                except IndexError as ie:
                    pass

                resold_apartment_item = ResoldApartmentItem()
                resold_apartment_item["refer"] = response.url
                resold_apartment_item["url"] = url
                if total_price.isdigit():
                    resold_apartment_item["total_price"] = float(total_price)
                else:
                    resold_apartment_item["total_price"] = total_price
                resold_apartment_item["region"] = region
                resold_apartment_item["community"] = community
                resold_apartment_item["bedrooms"] = bedrooms
                resold_apartment_item["title"] = title
                resold_apartment_item["area"] = area
                search_result = self.number_pattern.search(unit_price)
                if search_result is None:
                    resold_apartment_item["unit_price"] = 0
                else:
                    resold_apartment_item["unit_price"] = int(search_result.group(1))
                resold_apartment_item["orientation"] = orientation
                resold_apartment_item["floor"] = floor
                resold_apartment_item["decoration"] = decoration
                resold_apartment_item["year"] = build_year
                yield resold_apartment_item
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
            except UnicodeDecodeError as ude:
                self.log(ude.message, level=logging.WARN)
                pass

        # other page
        try:
            next_page = response.xpath("//div[@class='p']/div[@class='page']/a[@class='next']/@href").extract()[0]
            self.log("next page: {0}".format(next_page), level=logging.INFO)
            yield scrapy.Request(url=next_page, callback=self.parse_ershoufang)
        except IndexError as ie:
            self.log(ie.message, level=logging.WARN)
            self.log("this is last page, url is: %s" % response.url, level=logging.WARN)
            pass

    def parse(self, response):
        # self.log("parse url:{0}".format(response.url), level=logging.INFO)
        if response.url.find("zufang") != -1:
            self.log("parse_rent url:{0}".format(response.url), level=logging.INFO)
            self.parse_rent(response)
        elif response.url.find("loupan") != -1:
            self.log("parse_loupan url:{0}".format(response.url), level=logging.INFO)
            self.parse_loupan(response)
        elif response.url.find("ershoufang") != -1:
            self.log("parse_ershoufang url:{0}".format(response.url), level=logging.INFO)
            self.parse_ershoufang(response)