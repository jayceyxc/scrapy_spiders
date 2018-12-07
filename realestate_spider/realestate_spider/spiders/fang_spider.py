#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: fang_spider.py
@time: 17/10/2017 11:44
"""


import chardet
import scrapy
import logging
import json

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


class FangSpider(scrapy.Spider):
    name = "fangSpider"
    mongo_uri = "127.0.0.1:19191"
    mongo_db = "realestate"
    collection_name = "fang_items"

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
        for url in start_url.fang_start_url:
            # self.log("parse url:{0}".format(response.url), level=logging.INFO)
            if url.find("zufang") != -1:
                yield scrapy.Request(url=url, callback=self.parse_rent)
            elif url.find("loupan") != -1:
                yield scrapy.Request(url=url, callback=self.parse_loupan)
            elif url.find("ershoufang") != -1:
                yield scrapy.Request(url=url, callback=self.parse_ershoufang)
            # yield scrapy.Request(url=url, callback=self.parse)

    def parse_rent_detail(self, response):
        try:
            rent_price = response.xpath("//div[@class='overview']/div[@class='content zf-content']/div[@class='price ']/span[@class='total']/text()").extract()[0]
            title = response.xpath("//div[@class='wid1000']/div[@class='h1-tit rel']/h1/text()").extract()[0]
            house_info_list = response.xpath("//div[@class='floatr house-info-wrap']/ul[@class='house-info']/li")
            area = 0
            bedrooms = 0
            floor = "未知"
            orientation = "未知"
            community = "未知"
            region = "未知"
            for house in house_info_list:
                try:
                    i_value = house.xpath("./i/text()").extract()[0]

                    if i_value == u"面积：":
                        area_temp = house.xpath("./text()").extract()[0]
                        area = float(area_temp[:area_temp.find(u"平")])
                    elif i_value == u"房屋户型：":
                        bedroom_temp = house.xpath("./text()").extract()[0]
                        bedrooms = int(bedroom_temp[:bedroom_temp.find(u"室")])
                    elif i_value == u"楼层：":
                        floor = house.xpath("./text()").extract()[0]
                    elif i_value == u"房屋朝向：":
                        orientation = house.xpath("./text()").extract()[0]
                    elif i_value == u"小区：":
                        community = house.xpath("./a/text()").extract()[0]
                    elif i_value == u"位置：":
                        region = house.xpath("./a/text()").extract()[0]
                except IndexError as ie:
                    self.log(ie.message, level=logging.WARN)
                    pass
                except ValueError as ve:
                    self.log(ve.message, level=logging.WARN)
                    pass

            billing_type = "未知"
            rent_type = "未知"
            decoration = "未知"
            build_year = "未知"

            renthouse_item = RentHouseItem()
            renthouse_item["refer"] = response.meta['refer']
            renthouse_item["url"] = response.url
            if rent_price.isdigit():
                renthouse_item["rent_price"] = float(rent_price)
            else:
                renthouse_item["rent_price"] = rent_price
            renthouse_item["billing_type"] = billing_type
            renthouse_item["rent_type"] = rent_type
            renthouse_item["region"] = region.strip()
            renthouse_item["community"] = community.strip()
            renthouse_item["bedrooms"] = bedrooms
            renthouse_item["title"] = title.strip()
            renthouse_item["area"] = area
            renthouse_item["orientation"] = orientation
            renthouse_item["floor"] = floor
            renthouse_item["decoration"] = decoration
            renthouse_item["year"] = build_year

            yield renthouse_item
        except IndexError as ie:
            self.log(ie.message, level=logging.WARN)
            pass

    def parse_rent(self, response):
        house_list = response.xpath("//div[@class='houseList']/dl")
        for house_item in house_list:
            try:
                detail_url = house_item.xpath("./dd[@class='info rel']/p[@class='title']/a/@href").extract()[0]
                detail_url = detail_url.split("?")[0]
                if not detail_url.startswith("http://zu.cs.fang.com"):
                    detail_url = "http://zu.cs.fang.com" + detail_url
                self.log("detail page: {0}".format(detail_url), level=logging.INFO)
                yield scrapy.Request(url=detail_url, callback=self.parse_rent_detail, meta={'refer': response.url})
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
                pass
            except UnicodeDecodeError as ude:
                self.log(ude.message, level=logging.WARN)
                pass

        # other page
        try:
            a_list = response.xpath("//div[@class='fanye']/a")
            for a_item in a_list:
                text = a_item.xpath("./text()").extract()[0]
                if text == u"下一页":
                    next_page = a_item.xpath("./@href").extract()[0]
                    if not next_page.startswith("http://zu.cs.fang.com"):
                        next_page = "http://zu.cs.fang.com" + next_page
                    yield scrapy.Request(url=next_page, callback=self.parse_rent)
        except IndexError as ie:
            self.log(ie.message, level=logging.WARN)
            self.log("this is last page, url is: %s" % response.url, level=logging.WARN)
            pass

    def parse_loupan(self, response):
        house_list = response.xpath("//ul[@id='house-lst']/li")
        for house_item in house_list:
            try:
                url = house_item.xpath("./div[@class='pic-panel']/a/@href").extract()[0]
                if not url.startswith("https://cs.lianjia.com"):
                    url = "https://cs.lianjia.com" + url

                unit_price = '价格待定'
                try:
                    unit_price = house_item.xpath("./div[@class='info-panel']/div[@class='col-2']/div[@class='price']/div[@class='average']/span[@class='num']/text()").extract()[0]
                except IndexError as ie:
                    self.log(ie.message, level=logging.WARN)
                    pass

                region = "未知"
                address = "未知"
                try:
                    address = house_item.xpath("./div[@class='info-panel']/div[@class='col-1']/div[@class='where']/span[@class='region']/text()").extract()[0]
                    region = address.split("-")[0]
                    address = address.split("-")[1]
                except IndexError as ie:
                    self.log(ie.message, level=logging.WARN)
                    pass

                community = "未知"
                try:
                    community = house_item.xpath("./div[@class='info-panel']/div[@class='col-1']/h2/a/text()").extract()[0]
                except IndexError as ie:
                    self.log(ie.message, level=logging.WARN)
                    pass

                title = community.strip()

                house_type = "未知"
                try:
                    house_type = house_item.xpath("./div[@class='info-panel']/div[@class='col-1']/div[@class='type']/span[@class='live']/text()").extract()[0]
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
                loufan_item['house_type'] = house_type
                loufan_item['address'] = address
                yield loufan_item
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
                pass
            except UnicodeDecodeError as ude:
                self.log(ude.message, level=logging.WARN)
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
                    yield scrapy.Request(url=next_page, callback=self.parse_loupan)
        except IndexError as ie:
            self.log(ie.message, level=logging.WARN)
            self.log("this is last page, url is: %s" % response.url, level=logging.WARN)
            pass

    def parse_ershoufang_detail(self, response):
        self.log("in parse_ershoufang_detail: {0}".format(response.url), level=logging.INFO)
        try:
            total_price = response.xpath("//div[@class='overview']/div[@class='content']/div[@class='price ']/span[@class='total']/text()").extract()[0]
            unit_price = response.xpath("//div[@class='overview']/div[@class='content']/div[@class='price ']/div[@class='text']/div[@class='unitPrice']/span[@class='unitPriceValue']/text()").extract()[0]
            url = response.url
            if not url.startswith("https://cs.lianjia.com"):
                url = "https://cs.lianjia.com" + url

            title = response.xpath("//div[@class='sellDetailHeader']/div[@class='title-wrapper']/div[@class='content']/div[@class='title']/h1[@class='main']/@title").extract()[0]

            house_info_div = response.xpath("//div[@class='overview']/div[@class='content']/div[@class='houseInfo']")
            bedrooms = 0
            floor = "未知"
            orientation = "未知"
            decoration = "未知"
            area = 0
            build_year = "未知"
            try:
                bedroom_temp = house_info_div.xpath("./div[@class='room']/div[@class='mainInfo']/text()").extract()[0]
                bedrooms = int(bedroom_temp[:bedroom_temp.find(u"室")])
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
                pass
            except ValueError as ve:
                self.log(ve.message, level=logging.WARN)
                pass

            try:
                floor = house_info_div.xpath("./div[@class='room']/div[@class='subInfo']/text()").extract()[0]
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
                pass
            except ValueError as ve:
                self.log(ve.message, level=logging.WARN)
                pass

            try:
                orientation = house_info_div.xpath("./div[@class='type']/div[@class='mainInfo']/text()").extract()[0]
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
                pass
            except ValueError as ve:
                self.log(ve.message, level=logging.WARN)
                pass

            try:
                decoration = house_info_div.xpath("./div[@class='type']/div[@class='subInfo']/text()").extract()[0]
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
                pass
            except ValueError as ve:
                self.log(ve.message, level=logging.WARN)
                pass

            try:
                area_temp = house_info_div.xpath("./div[@class='area']/div[@class='mainInfo']/text()").extract()[0]
                area = float(area_temp[:area_temp.find(u"平")])
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
                pass
            except ValueError as ve:
                self.log(ve.message, level=logging.WARN)
                pass

            try:
                build_year_temp = house_info_div.xpath("./div[@class='area']/div[@class='subInfo']/text()").extract()[0]
                build_year = build_year_temp[:build_year_temp.find(u"年")]
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
                pass
            except ValueError as ve:
                self.log(ve.message, level=logging.WARN)
                pass

            around_info_div = response.xpath("//div[@class='overview']/div[@class='content']/div[@class='aroundInfo']")
            community = "未知"
            region = "未知"
            house_type = "未知"
            try:
                community = around_info_div.xpath("./div[@class='communityName']/a[@class='info ']/text()").extract()[0]
            except ValueError as ve:
                self.log(ve.message, level=logging.WARN)
                pass

            try:
                region = around_info_div.xpath("./div[@class='areaName']/span[@class='info']/a/text()").extract()[0]
            except ValueError as ve:
                self.log(ve.message, level=logging.WARN)
                pass

            resold_apartment_item = ResoldApartmentItem()
            resold_apartment_item["refer"] = response.meta['refer']
            resold_apartment_item["url"] = url
            if total_price.isdigit():
                resold_apartment_item["total_price"] = float(total_price)
            else:
                resold_apartment_item["total_price"] = total_price
            if unit_price.isdigit():
                resold_apartment_item["unit_price"] = float(unit_price)
            else:
                resold_apartment_item["unit_price"] = unit_price
            resold_apartment_item["region"] = region
            resold_apartment_item["house_type"] = house_type
            resold_apartment_item["community"] = community
            resold_apartment_item["bedrooms"] = bedrooms
            resold_apartment_item["title"] = title
            resold_apartment_item["area"] = area
            resold_apartment_item["orientation"] = orientation
            resold_apartment_item["floor"] = floor
            resold_apartment_item["decoration"] = decoration
            resold_apartment_item["year"] = build_year
            yield resold_apartment_item
        except IndexError as ie:
            self.log(ie.message, level=logging.WARN)
            pass

    def parse_ershoufang(self, response):
        self.log("in parse_ershoufang: {0}".format(response.url), level=logging.INFO)
        house_list = response.xpath("//ul[@class='sellListContent']/li")
        for house_item in house_list:
            try:
                detail_url = house_item.xpath("./a[@class='img ']/@href").extract()[0]
                detail_url = detail_url.split("?")[0]
                if not detail_url.startswith("https://cs.lianjia.com"):
                    detail_url = "https://cs.lianjia.com" + detail_url
                self.log("detail page: {0}".format(detail_url), level=logging.INFO)
                yield scrapy.Request(url=detail_url, callback=self.parse_ershoufang_detail, meta={'refer': response.url})
            except IndexError as ie:
                self.log(ie.message, level=logging.WARN)
                pass
            except UnicodeDecodeError as ude:
                self.log(ude.message, level=logging.WARN)
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