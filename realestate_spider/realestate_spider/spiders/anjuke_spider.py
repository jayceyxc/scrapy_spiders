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


class AnjukeSpider(scrapy.Spider):
    name = "anjukeSpider"
    mongo_uri = "127.0.0.1:19191"
    mongo_db = "realestate"
    collection_name = "anjuke_items"
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
        for url in start_url.anjuke_start_url:
            # self.log("parse url:{0}".format(response.url), level=logging.INFO)
            if url.find("cs.zu.anjuke.com") != -1:
                yield scrapy.Request(url=url, callback=self.parse_rent)
            elif url.find("cs.anjuke.com/sale/") != -1:
                yield scrapy.Request(url=url, callback=self.parse_ershoufang)
            else:
                yield scrapy.Request(url=url, callback=self.parse_loupan)
            # yield scrapy.Request(url=url, callback=self.parse)

    def parse_rent(self, response):
        self.log("parse_rent: %s" % response.url, level=logging.WARN)
        house_list = response.xpath("//div[@class='maincontent']/div[@class='list-content']/div[@class='zu-itemmod  ']")
        for house_item in house_list:
            try:
                rent_price = house_item.xpath("./div[@class='zu-side']/p/strong/text()").extract()[0]
                data = house_item.xpath("./div[@class='zu-info']/p[@class='details-item tag']")
                info = data.xpath('string(.)').extract()[0]
                # 3室2厅|整租|精装修|10/18层
                segs = info.split('|')
                bedrooms = 0
                floor = "未知"
                rent_type = "未知"
                decoration = "未知"
                for content in segs:
                    if content.find(u"室") != -1:
                        bedrooms = int(content[:content.find(u"室")])
                    elif content.find(u"层") != -1:
                        floor = content
                    elif content.find(u"租") != -1:
                        rent_type = content
                    else:
                        decoration = content

                community = "未知"
                try:
                    community = house_item.xpath("./div[@class='zu-info']/address[@class='details-item']/a/text()").extract()[0]
                except IndexError as ie:
                    pass

                region = "未知"
                try:
                    data2 = house_item.xpath("./div[@class='zu-info']/address[@class='details-item']/text()").extract()[1]
                    data2 = data2 = data2.encode('utf8').strip().lstrip("［").rstrip("］")
                    region = data2.split("-")[0]
                except IndexError as ie:
                    pass

                url = house_item.xpath("./a/@href").extract()[0]
                if not url.startswith("https://cs.zu.anjuke.com"):
                    url = "https://cs.zu.anjuke.com" + url
                title = house_item.xpath("./a/@title").extract()[0].strip()

                # 以下四项在安居客的简单介绍中没有，在详细页面才有，因为不影响标签判断，不再深入。
                billing_type = "未知"
                build_year = -1
                orientation = "未知"
                area = -1

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
            next_page = response.xpath("//div[@class='maincontent']/div[@class='page-content']/div[@class='multi-page']/a[@class='aNxt']/@href").extract()[0]
            self.log("next page: {0}".format(next_page), level=logging.INFO)
            yield scrapy.Request(url=next_page, callback=self.parse_rent)
        except IndexError as ie:
            self.log(ie.message, level=logging.WARN)
            self.log("this is last page, url is: %s" % response.url, level=logging.WARN)
            pass

    def parse_loupan(self, response):
        self.log("parse_loupan: %s" % response.url, level=logging.WARN)
        div_list = response.xpath("//div[@class='list-contents']/div[@class='list-results']/div[@class='key-list']/div")
        for div_item in div_list:
            try:
                unit_price = "尚未公布"
                try:
                    unit_price = div_item.xpath("./a[@class='favor-pos']/p[@class='price']/span/text()").extract()[0]
                except IndexError as ie:
                    try:
                        unit_price = div_item.xpath("./a[@class='favor-pos']/p[@class='favor-tag around-price']/span/text()").extract()[0]
                    except IndexError as ie:
                        unit_price = div_item.xpath("./a[@class='favor-pos']/p[@class='price-txt']/text()").extract()[0]
                        pass

                url = div_item.xpath("./@data-link").extract()[0]
                if not url.startswith("https://cs.fang.anjuke.com"):
                    url = "https://cs.fang.anjuke.com" + url
                community = "未知"
                try:
                    community = div_item.xpath("./div[@class='infos']/a[@class='lp-name']/h3/span[@class='items-name']/text()").extract()[0].strip()
                except ValueError as ve:
                    self.log(ve.message, level=logging.WARN)
                    pass
                title = community

                region = "未知"
                try:
                    span_list = div_item.xpath("./div[@class='infos']/a[@class='address']/span")
                    region = span_list.xpath('string(.)').extract()[0].split()[1]
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
            next_page = response.xpath("//div[@class='list-page']/div[@class='pagination']/a[@class='next-page next-link']/@href").extract()[0]
            self.log("next page: {0}".format(next_page), level=logging.INFO)
            yield scrapy.Request(url=next_page, callback=self.parse_loupan)
        except IndexError as ie:
            self.log(ie.message, level=logging.WARN)
            self.log("this is last page, url is: %s" % response.url, level=logging.WARN)
            pass

    def parse_ershoufang_detail( self, response ):
        self.log("parse_ershoufang: %s" % response.url, level=logging.WARN)
        try:
            total_price = response.xpath("//div[@class='basic-info clearfix']/span[@class='light info-tag']/em/text()").extract()[0].strip()
            community = "未知"
            region = "未知"
            build_year = 0
            house_type = "未知"
            first_dl_list = response.xpath("//div[@class='houseInfoV2-detail clearfix']/div[@class='first-col detail-col']/dl")
            for dl in first_dl_list:
                dt = dl.xpath("./dt/text()").extract()[0]
                dd = "未知"
                try:
                    if dt == u"小区：":
                        community = dl.xpath("./dd/a/text()").extract()[0]
                    elif dt == u"位置：":
                        region = dl.xpath("./dd/p/a/text()").extract()[0]
                    elif dt == u"年代：":
                        temp_value = dl.xpath("./dd/text()").extract()[0]
                        build_result = self.number_pattern.search(temp_value)
                        if build_result is not None:
                            build_year = int(build_result.group(1))
                    elif dt == u"类型：":
                        house_type = dl.xpath("./dd/text()").extract()[0]
                except IndexError as ie:
                    self.log(ie.message, level=logging.WARN)
                    pass
                except ValueError as ve:
                    self.log(ve.message, level=logging.WARN)
                    pass

            bedrooms = 0
            area = 0
            orientation = "未知"
            floor = "未知"
            second_dl_list = response.xpath("//div[@class='houseInfoV2-detail clearfix']/div[@class='second-col detail-col']/dl")
            for dl in second_dl_list:
                dt = dl.xpath("./dt/text()").extract()[0]
                dd = "未知"
                try:
                    if dt == u"房型：":
                        dd = dl.xpath("./dd/text()").extract()[0].split()[0].strip()
                        bedrooms = int(dd[:dd.find(u"室")])
                    elif dt == u"面积：":
                        dd = dl.xpath("./dd/text()").extract()[0].strip()
                        area_result = self.number_pattern.search(dd)
                        if area_result is not None:
                            area = float(area_result.group(1))
                    elif dt == u"朝向：":
                        orientation = dl.xpath("./dd/text()").extract()[0].strip()
                    elif dt == u"楼层：":
                        floor = dl.xpath("./dd/text()").extract()[0].strip()
                except IndexError as ie:
                    self.log(ie.message, level=logging.WARN)
                    pass
                except ValueError as ve:
                    self.log(ve.message, level=logging.WARN)
                    pass

            decoration = "未知"
            unit_price = 0
            third_dl_list = response.xpath("//div[@class='houseInfoV2-detail clearfix']/div[@class='third-col detail-col']/dl")
            for dl in third_dl_list:
                dt = dl.xpath("./dt/text()").extract()[0]
                dd = "未知"
                try:
                    if dt == u"装修程度：":
                        decoration = dl.xpath("./dd/text()").extract()[0].split()[0].strip()
                    elif dt == u"房屋单价：":
                        dd = dl.xpath("./dd/text()").extract()[0].strip()
                        search_result = self.number_pattern.search(dd)
                        if search_result is not None:
                            unit_price = int(search_result.group(1))
                except IndexError as ie:
                    self.log(ie.message, level=logging.WARN)
                    pass
                except ValueError as ve:
                    self.log(ve.message, level=logging.WARN)
                    pass

            url = response.url
            if not url.startswith("https://cs.anjuke.com"):
                url = "https://cs.anjuke.com" + url
            title = response.xpath("//div[@class='clearfix title-guarantee']/h3[@class='long-title']/text()").extract()[0].strip()

            resold_apartment_item = ResoldApartmentItem()
            resold_apartment_item["refer"] = response.meta['refer']
            resold_apartment_item["url"] = url
            if total_price.isdigit():
                resold_apartment_item["total_price"] = float(total_price)
            else:
                resold_apartment_item["total_price"] = total_price
            resold_apartment_item["region"] = region
            resold_apartment_item["house_type"] = house_type
            resold_apartment_item["community"] = community
            resold_apartment_item["bedrooms"] = bedrooms
            resold_apartment_item["title"] = title
            resold_apartment_item["area"] = area
            resold_apartment_item["unit_price"] = unit_price
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

    def parse_ershoufang(self, response):
        self.log("parse_ershoufang: %s" % response.url, level=logging.WARN)
        house_list = response.xpath("//div[@class='sale-left']/ul[@id='houselist-mod-new']/li")
        for house_item in house_list:
            # self.log(house_item, level=logging.INFO)
            try:
                detail_url = house_item.xpath("./div[@class='house-details']/div[@class='house-title']/a/@href").extract()[0]
                detail_url = detail_url.split("?")[0]
                if not detail_url.startswith("https://cs.anjuke.com"):
                    detail_url = "https://cs.anjuke.com" + detail_url
                self.log("detail page: {0}".format(detail_url), level=logging.INFO)
                yield scrapy.Request(url=detail_url, callback=self.parse_ershoufang_detail, meta={'refer': response.url})
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
            except UnicodeDecodeError as ude:
                self.log(ude.message, level=logging.WARN)
                pass

        # other page
        try:
            next_page = response.xpath("//div[@class='multi-page']/a[@class='aNxt']/@href").extract()[0].split("#")[0]
            self.log("next page: {0}".format(next_page), level=logging.INFO)
            yield scrapy.Request(url=next_page, callback=self.parse_ershoufang)
        except IndexError as ie:
            self.log(ie.message, level=logging.WARN)
            self.log("this is last page, url is: %s" % response.url, level=logging.WARN)
            pass

    def parse(self, response):
        # self.log("parse url:{0}".format(response.url), level=logging.INFO)
        if response.url.find("cs.zu.anjuke.com") != -1:
            self.log("parse_rent url:{0}".format(response.url), level=logging.INFO)
            self.parse_rent(response)
        elif response.url.find("cs.fang.anjuke.com") != -1:
            self.log("parse_loupan url:{0}".format(response.url), level=logging.INFO)
            self.parse_loupan(response)
        elif response.url.find("cs.anjuke.com/sale") != -1:
            self.log("parse_ershoufang url:{0}".format(response.url), level=logging.INFO)
            self.parse_ershoufang(response)
