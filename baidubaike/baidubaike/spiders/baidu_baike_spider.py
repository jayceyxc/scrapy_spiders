#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Xuecheng Yu'
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2017-03-11 22:04:30

import sys

reload(sys)
sys.setdefaultencoding("utf-8")
import scrapy
import chardet
import re
import logging

from ..items import BaidubaikeItem
from disease_name import disease_names

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


def extract_chinese(s):
    line = s.strip().decode('utf-8', 'ignore')  # 处理前进行相关的处理，包括转换成Unicode等
    p2 = re.compile(ur'[^\u4e00-\u9fa5]')  # 中文的编码范围是：\u4e00到\u9fa5
    zh = " ".join(p2.split(line)).strip()
    zh = re.sub(' +', ' ', zh)
    out_str = zh  # 经过相关处理后得到中文的文本
    return out_str


class BaiduBaikeSpider(scrapy.Spider):
    name = "baiduBaikeSpider"
    url_pattern = "https://baike.baidu.com/item/%s"
    url_search_pattern = "https://www.baidu.com/s?wd=%s"
    mongo_uri = "127.0.0.1:19191"
    mongo_db = "baidu"
    collection_name = "baike"
    headersParameters = {  # 发送HTTP请求时的HEAD信息，用于伪装为浏览器
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }

    def start_requests(self):
        for disease_name in disease_names:
            url = self.url_search_pattern % disease_name
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headersParameters)

    def parse(self, response):
        self.log("search url: {0}".format(response.url), logging.INFO)
        result_list = response.xpath('//div[@id="content_left"]/div')
        for result in result_list:
            try:
                # print(result.xpath('//div[@class="f13"]/a'))
                title_xpath = result.xpath('./h3/a')
                title = title_xpath.xpath('string(.)').extract()[0]
                self.log('标题：' + title, logging.INFO)
                text = result.xpath('./div[@class="f13"]/a/text()').extract()[0]
                self.log('文本：' + text, logging.INFO)
                url = result.xpath('./div[@class="f13"]/a/@href').extract()[0]
                self.log('链接：' + url, logging.INFO)
                if text.find('baike.baidu.com') != -1:
                    self.log(url, logging.INFO)
                    yield scrapy.Request(url=url, callback=self.parse_baike, headers=self.headersParameters)
            except IndexError as ie:
                self.log(ie, logging.ERROR)

    def parse_baike(self, response):
        self.log('parse_baike' + response.url, logging.INFO)
        # main_info = response.xpath('//div[@class="main_tab main_tab-defaultTab curTab"]')
        main_str = ''
        try:
            main_info = response.xpath('//div[@class="main-content"]')
            main_str = main_info.xpath('string(.)').extract()[0]
            main_str = extract_chinese(main_str)
            self.log(main_str, logging.WARNING)
        except IndexError as ie:
            self.log(ie, logging.ERROR)

        desc_top_str = ''
        try:
            desc_top = response.xpath('//div[@class="poster-top"]')
            desc_top_str = desc_top.xpath('string(.)').extract()[0]
            desc_top_str = extract_chinese(desc_top_str)
            self.log(desc_top_str, logging.WARNING)
        except IndexError as ie:
            self.log(ie, logging.ERROR)

        desc_bottom_str = ''
        try:
            desc_bottom = response.xpath('//div[@class="poster-bottom"]')
            desc_bottom_str = desc_bottom.xpath('string(.)').extract()[0]
            desc_bottom_str = extract_chinese(desc_bottom_str)
            self.log(desc_bottom_str, logging.WARNING)
        except IndexError as ie:
            self.log(ie, logging.ERROR)

        try:
            title = response.xpath('//dd[@class="lemmaWgt-lemmaTitle-title"]/h1/text()').extract()[0]
            baike_item = BaidubaikeItem()
            baike_item['title'] = title
            baike_item['main_info'] = main_str
            baike_item['desc_info'] = desc_top_str + ' ' + desc_bottom_str
            yield baike_item
        except IndexError as ie:
            self.log(ie, logging.ERROR)
            self.log("url: {0} has no title.".format(response.url), logging.ERROR)


