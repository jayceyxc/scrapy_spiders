#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: ip_spider.py
@time: 28/08/2017 17:03
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import chardet
import scrapy
import logging
import random
import time
import json

from ip_area_spider.items import IpAreaItem

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


def analysis_ip(ip):
    try:
        ip1, ip2, ip3, ip4 = ip.split(".")
        # return {"ip1": int(ip1), "ip2": int(ip2), "ip3": int(ip3), "ip4": int(ip4)}
        return int(ip1), int(ip2), int(ip3), int(ip4)
    except ValueError:
        return None


class IpAreaSpider(scrapy.Spider):
    name = "ipAreaSpider"

    # query_url_pattern = "http://ip.taobao.com/service/getIpInfo.php?ip=%s&prev_id=%s&start_ip=%s&end_ip=%s"
    query_url_pattern = "http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=json&ip=%s&prev_id=%s&start_ip=%s&end_ip=%s&kid=%s"
    # query_url_pattern = "http://ip.ws.126.net/ipquery?ip=%s&prev_id=%s&start_ip=%s&end_ip=%s"
    """
    淘宝，有速度限制，一分钟15次
    query_url_pattern = "http://ip.taobao.com/service/getIpInfo.php?ip=%s&prev_id=%s&start_ip=%s&end_ip=%s"
    {"code":0,"data":{"country":"\u4e2d\u56fd","country_id":"CN","area":"\u534e\u5357","area_id":"800000","region":"\u5e7f\u4e1c\u7701","region_id":"440000","city":"\u6df1\u5733\u5e02","city_id":"440300","county":"","county_id":"-1","isp":"\u7535\u4fe1","isp_id":"100017","ip":"59.40.255.255"}}
    新浪，这个很快没有限制
    query_url_pattern = "http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=json&ip=%s&prev_id=%s&start_ip=%s&end_ip=%s"
    {"ret":1,"start":-1,"end":-1,"country":"\u4e2d\u56fd","province":"\u5e7f\u4e1c","city":"\u6df1\u5733","district":"","isp":"","type":"","desc":""}
    这个没试，但是结果好像不如前两个
    query_url_pattern = "http://ip.ws.126.net/ipquery?ip=%s&prev_id=%s&start_ip=%s&end_ip=%s"
    var lo="广东省", lc="深圳市"; var localAddress={city:"深圳市", province:"广东省"}
    """

    def start_requests(self):
        current_path = os.path.split(os.path.realpath(__file__))[0]
        self.log("current path: %s" % current_path, level=logging.WARN)
        file_name = current_path + os.sep + "rmc_area.txt"
        yield_num = 0
        with open(file_name, mode="r") as fd:
            for line in fd:
                line = line.strip()
                # self.log("line: %s" % line, level=logging.INFO)
                try:
                    kid, id, area_name, start_ip, end_ip = line.split()
                    start_ip1, start_ip2, start_ip3, start_ip4 = analysis_ip(start_ip)
                    end_ip1, end_ip2, end_ip3, end_ip4 = analysis_ip(end_ip)
                    if start_ip1 < end_ip1:
                        for ip_index1 in range(start_ip1, end_ip1 + 1, 1):
                            start = 0
                            end = 0
                            if ip_index1 == start_ip1 and ip_index1 != end_ip1:
                                start = start_ip2
                                end = 256
                            elif ip_index1 != start_ip1 and ip_index1 == end_ip1:
                                start = 0
                                end = end_ip2 + 1
                            else:
                                start = 0
                                end = 256

                            for ip_index2 in range(start, end, 1):
                                inner_start = 0
                                inner_end = 0
                                if ip_index2 == start_ip2 and ip_index1 == start_ip1 and ip_index2 != end_ip2:
                                    inner_start = start_ip3
                                    inner_end = 256
                                elif ip_index2 != start_ip2 and ip_index2 == end_ip2 and ip_index1 == end_ip1:
                                    inner_start = 0
                                    inner_end = end_ip3 + 1
                                else:
                                    inner_start = 0
                                    inner_end = 256

                                for ip_index3 in range(inner_start, inner_end + 1, 1):
                                    ip_4 = random.randint(1, 254)
                                    ip = "{0}.{1}.{2}.{3}".format(ip_index1, ip_index2, ip_index3, ip_4)
                                    query_url = self.query_url_pattern % (ip, id, start_ip, end_ip, kid)
                                    # self.log("scrapy url: %s" % query_url, level=logging.INFO)
                                    yield_num += 1
                                    if yield_num == 3000:
                                        time.sleep(1)
                                        yield_num = 0
                                    yield scrapy.Request(url=query_url, callback=self.parse)
                    elif start_ip2 < end_ip2:
                        for ip_index2 in range(start_ip2, end_ip2 + 1, 1):
                            start = 0
                            end = 0
                            if ip_index2 == start_ip2 and ip_index2 != end_ip2:
                                start = start_ip3
                                end = 256
                            elif ip_index2 != start_ip2 and ip_index2 == end_ip2:
                                start = 0
                                end = end_ip3 + 1
                            elif ip_index2 != start_ip2 and ip_index2 != end_ip2:
                                start = 0
                                end = 256

                            for ip_index3 in range(start, end, 1):
                                ip_4 = random.randint(1, 254)
                                ip = "{0}.{1}.{2}.{3}".format(start_ip1, ip_index2, ip_index3, ip_4)
                                query_url = self.query_url_pattern % (ip, id, start_ip, end_ip, kid)
                                # self.log("scrapy url: %s" % query_url, level=logging.INFO)
                                yield_num += 1
                                if yield_num == 3000:
                                    time.sleep(1)
                                    yield_num = 0
                                yield scrapy.Request(url=query_url, callback=self.parse)
                    elif start_ip3 < end_ip3:
                        for ip_index3 in range(start_ip3, end_ip3 + 1, 1):
                            ip_4 = random.randint(1, 254)
                            ip = "{0}.{1}.{2}.{3}".format(start_ip1, start_ip2, ip_index3, ip_4)
                            query_url = self.query_url_pattern % (ip, id, start_ip, end_ip, kid)
                            # self.log("scrapy url: %s" % query_url, level=logging.INFO)
                            yield_num += 1
                            if yield_num == 3000:
                                time.sleep(1)
                                yield_num = 0
                            yield scrapy.Request(url=query_url, callback=self.parse)
                    else:
                        ip_4 = random.randint(start_ip4, end_ip4)
                        ip = "{0}.{1}.{2}.{3}".format(start_ip1, start_ip2, start_ip3, ip_4)
                        query_url = self.query_url_pattern % (ip, id, start_ip, end_ip, kid)
                        # self.log("scrapy url: %s" % query_url, level=logging.INFO)
                        yield_num += 1
                        if yield_num == 3000:
                            time.sleep(1)
                            yield_num = 0
                        yield scrapy.Request(url=query_url, callback=self.parse)

                except ValueError as ve:
                    continue

    def parse_query(self, response):
        result = dict()
        query_str = response.url.split("?")[1]
        for params in query_str.split("&"):
            param, value = params.split("=")
            result[param] = value

        return result


    def parse(self, response):
        """
        http://www.ip138.com/ips1388.asp?ip=219.247.120.98&action=2
        try:
            area_name = response.xpath("/html/body/table/tr[3]/td/ul/li[1]/text()").extract()[0]
            ip = response.url.split("?")[1].split("&")[0].split("=")[1]
            prev_id = response.url.split("?")[1].split("&")[2].split("=")[1]
            start_ip = response.url.split("?")[1].split("&")[3].split("=")[1]
            end_ip = response.url.split("?")[1].split("&")[4].split("=")[1]
            ip_item = IpAreaItem()
            ip_item["ip"] = ip
            ip_item["prev_id"] = prev_id
            ip_item["start_ip"] = start_ip
            ip_item["end_ip"] = end_ip
            ip_item["area_name"] = area_name.encode("utf-8")
            yield ip_item
        except IndexError as ie:
            self.log("Get area failed %s" % response.url, level=logging.WARN)
            pass
        """
        try:
            result = json.loads(response.text)
            self.log("result: %s" % response.text, level=logging.DEBUG)
            """
            if result["code"] != 0:
                return

            province = result['data']['region']
            city = result['data']['city']
            """
            country = result['country']
            province = result['province']
            city = result['city']
            area_name = None
            if len(city) != 0:
                area_name = u"".join([country, province, city])
            elif len(province) != 0:
                area_name = u"".join(([country, province]))
            else:
                area_name = country

            if len(area_name) == 0:
                return

            query_dict = self.parse_query(response)
            ip = query_dict["ip"]
            prev_id = query_dict["prev_id"]
            start_ip = query_dict["start_ip"]
            end_ip = query_dict["end_ip"]
            kid = query_dict["kid"]
            ip_item = IpAreaItem()
            ip_item["kid"] = kid
            ip_item["ip"] = ip
            ip_item["prev_id"] = prev_id
            ip_item["start_ip"] = start_ip
            ip_item["end_ip"] = end_ip
            ip_item["area_name"] = area_name.encode("utf-8")
            yield ip_item
        except IndexError as ie:
            self.log("Get area failed %s" % response.url, level=logging.WARN)
            pass