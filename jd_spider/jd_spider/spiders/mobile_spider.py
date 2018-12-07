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
import json
import chardet
import requests
import logging
import traceback

from jd_spider.items import MobileItem

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


class JDMobileSpider(scrapy.Spider):
    name = "mobilespider"
    url_pattern = "https://list.jd.com/list.html?cat=9987,653,655&page=%d&sort=sort_rank_asc&trans=1&JL=6_0_0&ms=6#J_main"
    mongo_uri = "127.0.0.1:19191"
    mongo_db = "jd"
    collection_name = "mobile_items"

    def start_requests(self):
        for page_index in range(1, 154, 1):
            url = self.url_pattern % page_index
            # print url
            yield scrapy.Request(url=url, callback=self.parse)

    @staticmethod
    def get_comment_info(ware_id):
        url = 'http://item.m.jd.com/ware/getDetailCommentList.json?wareId=' + str(ware_id)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}
        r2 = requests.get(url=url, headers=headers)
        data = json.loads(r2.text, encoding='utf-8')
        return data['wareDetailComment']['allCnt'], data['wareDetailComment']['goodCnt'], data['wareDetailComment'][
            'normalCnt'], data['wareDetailComment']['badCnt']

    @staticmethod
    def get_detail_info(ware_id):
        result = dict()
        url = 'https://item.m.jd.com/ware/detail.json?wareId=' + str(ware_id)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}
        r2 = requests.get(url=url, headers=headers)
        try:
            data = json.loads(r2.text, encoding='utf-8')
            detail = json.loads(data['ware']['wi']['code'])
            for info in detail:
                for key in info.keys():
                    inner_data = info[key]
                    for inner_info in inner_data:
                        for inner_key in inner_info:
                            result[inner_key] = inner_info[inner_key]
        except ValueError:
            # traceback.print_exc()
            pass

        return result

    def parse(self, response):
        mobile_jd_url_pattern = "https://item.m.jd.com/product/%s.html"
        item_list = response.xpath("//ul[@class='gl-warp clearfix']/li")
        logging.debug(response.encoding)
        for item in item_list:
            ware_id = item.xpath("./div[@class='gl-i-wrap j-sku-item']/div[@class='p-focus']/a[@class='J_focus']/@data-sku").extract()[0]
            # self.log("ware id: %s" % ware_id, logging.INFO)
            detail_url = mobile_jd_url_pattern % ware_id
            yield scrapy.Request(detail_url, callback=self.detail_parse)

    def detail_parse(self, response):
        try:
            ware_id = response.xpath("//*[@id='currentWareId']/@value").extract()[0]
            good_name = response.xpath("//*[@id='goodName']/@value").extract()[0]
            jd_price = response.xpath("//*[@id='jdPrice']/@value").extract()[0]
            category_id = "-1"
            shop_id = "-1"
            all_color_set = "{}"
            all_size_set = "{}"
            all_sku_color_size_spec = "{}"
            try:
                category_id = response.xpath("//*[@id='categoryId']/@value").extract()[0]
                if len(category_id) == 0:
                    category_id = "-1"
            except IndexError:
                self.log("no category id for url: %s" % response.url, logging.WARN)
                pass
            try:
                shop_id = response.xpath("//*[@id='shopId']/@value").extract()[0]
                if len(shop_id) == 0:
                    shop_id = "-1"
            except IndexError:
                self.log("no shop id for url: %s" % response.url, logging.WARN)
                pass
            try:
                all_color_set = response.xpath("//*[@id='allColorSet']/@value").extract()[0]
                if len(all_color_set) == 0:
                    all_color_set = "{}"
            except IndexError:
                self.log("no color set for url: %s" % response.url, logging.WARN)
                pass
            try:
                all_size_set = response.xpath("//*[@id='allSizeSet']/@value").extract()[0]
                if len(all_size_set) == 0:
                    all_size_set = "{}"
            except IndexError:
                self.log("no size set for url: %s" % response.url, logging.WARN)
                pass
            try:
                all_sku_color_size_spec = response.xpath("//*[@id='skuColorSizeSpec']/@value").extract()[0]
                if len(all_sku_color_size_spec) == 0:
                    all_sku_color_size_spec = "{}"
                data = json.loads(all_sku_color_size_spec)
                s = ""
                for d in data['colorSize']:
                    for key, value in d.iteritems():
                        s += "%s:%s," % (key, value)
                    s = s.rstrip(',')
                    s += ";"
                all_sku_color_size_spec = s
            except IndexError:
                self.log("no color size spec for url: %s" % response.url, logging.WARN)
                pass
            except KeyError:
                self.log("no color size spec for url: %s" % response.url, logging.WARN)
                pass
            total_comments = 0
            good_comments = 0
            normal_comments = 0
            bad_comments = 0
            detail_info = dict()
            if ware_id is not None:
                total_comments, good_comments, normal_comments, bad_comments = self.get_comment_info(ware_id)
                detail_info = self.get_detail_info(ware_id)

            mobile_item = MobileItem()
            mobile_item['ware_id'] = ware_id
            mobile_item['good_name'] = good_name
            mobile_item['jd_price'] = float(jd_price)
            mobile_item['category_id'] = category_id
            mobile_item['shop_id'] = int(shop_id)
            mobile_item['color_set'] = u",".join(json.loads(all_color_set))
            mobile_item['capacity_set'] = u",".join(json.loads(all_size_set))
            mobile_item['good_url'] = response.url
            mobile_item['total_comments'] = int(total_comments)
            mobile_item['good_comments'] = int(good_comments)
            mobile_item['normal_comments'] = int(normal_comments)
            mobile_item['bad_comments'] = int(bad_comments)
            mobile_item['RAM'] = detail_info[u"RAM"] if u"RAM" in detail_info else u"0GB"
            mobile_item['ROM'] = detail_info[u"ROM"] if u"ROM" in detail_info else u"0GB"
            mobile_item['OS'] = detail_info[u"操作系统"] if u"操作系统" in detail_info else u"Unknown"
            if u"CPU型号" in detail_info:
                mobile_item['CPU'] = detail_info[u"CPU型号"]
            elif u"CPU品牌" in detail_info:
                mobile_item['CPU'] = detail_info[u"CPU品牌"]
            else:
                mobile_item['CPU'] = u"Unknown"
            # mobile_item['CPU'] = detail_info[u"CPU型号"] if u"CPU型号" in detail_info else u"Unknown"
            mobile_item['resolution'] = detail_info[u"分辨率"] if u"分辨率" in detail_info else u"Unknown"
            mobile_item['display'] = detail_info[u"主屏幕尺寸（英寸）"] if u"主屏幕尺寸（英寸）" in detail_info else u"Unknown"
            mobile_item['year_to_market'] = detail_info[u"上市年份"] if u"上市年份" in detail_info else u"Unknown"
            mobile_item['month_to_market'] = detail_info[u"上市月份"] if u"上市月份" in detail_info else u"Unknown"
            mobile_item['length'] = detail_info[u"机身长度（mm）"] if u"机身长度（mm）" in detail_info else u"Unknown"
            mobile_item['width'] = detail_info[u"机身宽度（mm）"] if u"机身宽度（mm）" in detail_info else u"Unknown"
            mobile_item['thickness'] = detail_info[u"机身厚度（mm）"] if u"机身厚度（mm）" in detail_info else u"Unknown"
            mobile_item['weight'] = detail_info[u"机身重量（g）"] if u"机身重量（g）" in detail_info else u"Unknown"
            mobile_item['net_in_model'] = detail_info[u"入网型号"] if u"入网型号" in detail_info else u"Unknown"
            mobile_item['front_camera'] = detail_info[u"前置摄像头"] if u"前置摄像头" in detail_info else u"Unknown"
            mobile_item['rear_camera'] = detail_info[u"后置摄像头"] if u"后置摄像头" in detail_info else u"Unknown"
            mobile_item['brand'] = detail_info[u"品牌"] if u"品牌" in detail_info else u"Unknown"
            mobile_item['model'] = detail_info[u"型号"] if u"型号" in detail_info else u"Unknown"
            mobile_item['color'] = detail_info[u"机身颜色"] if u"机身颜色" in detail_info else u"Unknown"

            yield mobile_item
        except IndexError:
            self.log("no ware_id or good_name or price for url: %s" % response.url, logging.ERROR)

