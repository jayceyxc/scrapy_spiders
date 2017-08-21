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
import re

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


class JDBookSpider(scrapy.Spider):
    name = "bookspider"
    start_urls = [
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10001-1#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10001-2#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10001-3#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10001-4#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10001-5#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10002-1#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10002-2#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10002-3#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10002-4#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10002-5#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10003-1#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10003-2#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10003-3#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10003-4#comfort',
        'http://book.jd.com/booktop/0-1-0.html?category=3287-0-1-0-10003-5#comfort',
        'http://book.jd.com/booktop/0-0-1.html?category=1713-0-0-1-10001-1#comfort',
        'http://book.jd.com/booktop/0-0-1.html?category=1713-0-0-1-10001-2#comfort',
        'http://book.jd.com/booktop/0-0-1.html?category=1713-0-0-1-10001-3#comfort',
        'http://book.jd.com/booktop/0-0-1.html?category=1713-0-0-1-10001-4#comfort',
        'http://book.jd.com/booktop/0-0-1.html?category=1713-0-0-1-10001-5#comfort',
    ]

    """"
    custom_settings = {
        'LOG_FILE': 'book_spider.log',
        'LOG_LEVEL': 'DEBUG',
    }
    """

    """
    def parse(self, response):
        # 这里的type要用2或3，不能用1，1会被重定向
        price_url_pattern = "http://p.3.cn/prices/mgets?type=2&skuIds=J_%s"
        mobile_jd_url_pattern = "http://item.m.jd.com/product/%s.html"
        m_list = response.xpath("//div[@class='m m-list']/div[@class='mc']/ul[@class='clearfix']/li")
        logging.debug(response.encoding)
        for item in m_list:
            number = item.xpath("./div[@class='p-num']/text()").extract()[0]
            number = number.encode(response.encoding).decode("gbk", 'ignore')
            logging.debug(number)
            name = item.xpath("./div[@class='p-detail']/a/text()").extract()[0]
            name = name.encode(response.encoding).decode("gbk", 'ignore')
            # print type(name)
            logging.debug(name)
            detail_list = item.xpath("./div[@class='p-detail']/dl")
            detail_url = item.xpath("./div[@class='p-detail']/a/@href").extract()[0]
            detail_url = response.urljoin(detail_url)
            author_name = None
            publisher = None
            price = 0.0
            jd_price = 0.0
            for detail_li in detail_list:
                key = detail_li.xpath("./dt/text()").extract()[0]
                if key == u"作　者：":
                    author_name = detail_li.xpath("./dd/a/text()").extract()[0]
                    author_name = author_name.encode(response.encoding).decode("gbk", 'ignore')
                    logging.debug(author_name)
                elif key == u"出版社：":
                    publisher = detail_li.xpath("./dd/a/text()").extract()[0]
                    publisher = publisher.encode(response.encoding).decode("gbk", 'ignore')
                    logging.debug(publisher)
                elif key == u"定　价：":
                    product_id = detail_li.xpath("./dd/del/@data-price-id").extract()[0]
                    price_key = detail_li.xpath("./dd/del/@data-price-type").extract()[0]
                    logging.debug(product_id + " " + price_key)
                elif key == u"京东价：":
                    jd_product_id = detail_li.xpath("./dd/em/@data-price-id").extract()[0]
                    jd_price_key = detail_li.xpath("./dd/em/@data-price-type").extract()[0]
                    logging.debug(jd_product_id + " " + jd_price_key)

            if product_id != jd_product_id:
                logging.error("product id and jd product id is not same")
                yield None
            price_url = price_url_pattern % product_id
            logging.debug(price_url)
            price_resp = requests.get(price_url)
            content = price_resp.content
            detail = json.loads(content)
            logging.debug(detail)
            if detail is list and detail[0].has_key(price_key) and detail[0].has_key(jd_price_key):
                price = detail[0][price_key]
                jd_price = detail[0][jd_price_key]
            value = {
                "number": number,
                "name": name,
                "url": detail_url,
                "author": author_name,
                "publisher": publisher,
                "price": price,
                "jd_price": jd_price,
            }
            logging.debug(json.dumps(value, ensure_ascii=False))
            # print "value type is: " + str(type(value))
            yield value

        for item in m_list:
            detail_url = item.xpath("./div[@class='p-detail']/a/@href").extract()[0]
            if detail_url is not None:
                detail_url = response.urljoin(detail_url)
                yield scrapy.Request(detail_url, callback=self.detail_parse)
    """

    def get_jd_comment_count(self, ware_id):
        url = 'http://item.m.jd.com/ware/getDetailCommentList.json?wareId=' + str(ware_id)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}
        r2 = requests.get(url=url, headers=headers)
        data = json.loads(r2.text, encoding='utf-8')
        return data['wareDetailComment']['allCnt'], data['wareDetailComment']['goodCnt'], data['wareDetailComment'][
            'normalCnt'], data['wareDetailComment']['badCnt']

    def parse(self, response):
        mobile_jd_url_pattern = "http://item.m.jd.com/product/%s.html"
        jd_pat = re.compile("\d+.html")
        m_list = response.xpath("//div[@class='m m-list']/div[@class='mc']/ul[@class='clearfix']/li")
        logging.debug(response.encoding)
        for item in m_list:
            url = item.xpath("./div[@class='p-detail']/a/@href").extract()[0]
            url = response.urljoin(url)
            url = url.split('?', 1)[0]
            match_list = jd_pat.findall((url))
            if len(match_list) > 0:
                ware_id = match_list[0].rstrip(".html")
                detail_url = mobile_jd_url_pattern % ware_id
                yield scrapy.Request(detail_url, callback=self.detail_parse)

    def detail_parse(self, response):
        ware_id = response.xpath("//*[@id='currentWareId']/@value").extract()[0]
        good_name = response.xpath("//*[@id='goodName']/@value").extract()[0]
        jd_price = response.xpath("//*[@id='jdPrice']/@value").extract()[0]
        category_id = response.xpath("//*[@id='categoryId']/@value").extract()[0]
        all_color_set = response.xpath("//*[@id='allColorSet']/@value").extract()[0]
        total_comments = 0
        good_comments = 0
        normal_comments = 0
        bad_comments = 0
        self.log("ware id: %s" % ware_id, logging.INFO)
        if ware_id is not None:
            total_comments, good_comments, normal_comments, bad_comments = self.get_jd_comment_count(ware_id)
        yield {
            u"商品ID": ware_id,
            u"商品名称": good_name,
            u"京东价": float(jd_price),
            u"分类ID": category_id,
            u"分类标签": all_color_set,
            u"总评价数": int(total_comments),
            u"好评数": int(good_comments),
            u"普通评价数": int(normal_comments),
            u"差评数": int(bad_comments),
        }
