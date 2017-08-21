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
        for page_index in range(1, 146, 1):
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

    def parse(self, response):
        mobile_jd_url_pattern = "https://item.m.jd.com/product/%s.html"
        item_list = response.xpath("//ul[@class='gl-warp clearfix ']/li")
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
            total_comments = 0
            good_comments = 0
            normal_comments = 0
            bad_comments = 0
            if ware_id is not None:
                total_comments, good_comments, normal_comments, bad_comments = self.get_comment_info(ware_id)
            yield {
                u"商品ID": ware_id,
                u"商品名称": good_name,
                u"京东价": float(jd_price),
                u"分类ID": category_id,
                u"店铺ID": int(shop_id),
                u"颜色分类": u",".join(json.loads(all_color_set)),
                u"存储分类": u",".join(json.loads(all_size_set)),
                u"商品规格": all_sku_color_size_spec,
                u"商品链接": response.url,
                u"总评价数": int(total_comments),
                u"好评数": int(good_comments),
                u"普通评价数": int(normal_comments),
                u"差评数": int(bad_comments),
            }
        except IndexError:
            self.log("no ware_id or good_name or price for url: %s" % response.url, logging.ERROR)

