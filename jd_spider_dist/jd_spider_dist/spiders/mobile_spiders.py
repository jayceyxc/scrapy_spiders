#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: mobile_spiders.py
@time: 2017/7/28 15:58
"""

import json
import requests
import logging
from scrapy_redis.spiders import RedisSpider
from scrapy import Request

from jd_spider_dist.items import MobileItem


class MobileSpider(RedisSpider):
    name = "mobileSpider"
    redis_key = "%(name)s:start_urls"
    redis_batch_size = 5
    url_pattern = "https://list.jd.com/list.html?cat=9987,653,655&page=%d&sort=sort_rank_asc&trans=1&JL=6_0_0&ms=6#J_main"

    def start_requests(self):
        self.log("start_requests", level=logging.INFO)
        for page_index in range(1, 10, 1):
            url = self.url_pattern % page_index
            yield Request(url=url, callback=self.parse)
            # self.crawler.engine.crawl(Request(url=url, callback=self.parse), self)

    @staticmethod
    def get_comment_info(ware_id):
        url = 'http://item.m.jd.com/ware/getDetailCommentList.json?wareId=' + str(ware_id)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}
        r2 = requests.get(url=url, headers=headers)
        data = json.loads(r2.text, encoding='utf-8')
        return data['wareDetailComment']['allCnt'], data['wareDetailComment']['goodCnt'], data['wareDetailComment'][
            'normalCnt'], data['wareDetailComment']['badCnt']

    def parse(self, response):
        self.log("parse %s" % response.url, level=logging.INFO)
        mobile_jd_url_pattern = "https://item.m.jd.com/product/%s.html"
        item_list = response.xpath("//ul[@class='gl-warp clearfix']/li")
        self.log(response.encoding, level=logging.INFO)
        # self.log(response.body.decode(response.encoding, 'ignore'), level=logging.INFO)
        for item in item_list:
            ware_id = item.xpath("./div[@class='gl-i-wrap j-sku-item']/div[@class='p-focus']/a[@class='J_focus']/@data-sku").extract()[0]
            self.log("ware id: %s" % ware_id, logging.INFO)
            detail_url = mobile_jd_url_pattern % ware_id
            yield Request(detail_url, callback=self.detail_parse)
            # self.crawler.engine.crawl(Request(url=detail_url, callback=self.detail_parse), self)

    def detail_parse(self, response):
        self.log("detail_parse %s" % response.url, logging.INFO)
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

            mobileItem = MobileItem()
            mobileItem["id"] = ware_id
            mobileItem["name"] = good_name
            mobileItem["price"] = float(jd_price)
            mobileItem["category"] = category_id
            mobileItem["total_comments"] = int(total_comments)
            mobileItem["good_comments"] = int(good_comments)
            mobileItem["normal_comments"] = int(normal_comments)
            mobileItem["bad_comments"] = int(bad_comments)
            mobileItem["shop_id"] = int(shop_id)

            yield mobileItem
        except IndexError:
            self.log("no ware_id or good_name or price for url: %s" % response.url, logging.ERROR)
