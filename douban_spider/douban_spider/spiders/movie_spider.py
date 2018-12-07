#!/usr/bin/env python3
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: movie_spider.py
@time: 2017/7/20 09:48
"""

import json
import logging

import chardet
import pymongo
import scrapy

from ..items import MovieItem

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


class MovieSpider(scrapy.Spider):
    name = "moviespider"
    tags = [u'热门', u'最新', u'经典', u'可播放', u'豆瓣高分', u'冷门佳片', u'大陆', u'美国', u'香港', u'台湾', u'英国', u'法国', u'德国', u'意大利',
            u'西班牙', u'印度', u'泰国', u'俄罗斯', u'伊朗', u'加拿大', u'澳大利亚', u'爱尔兰', u'瑞典', u'巴西', u'丹麦', u'华语', u'欧美', u'韩国',
            u'日本', u'剧情', u'动作', u'喜剧', u'爱情', u'科幻', u'悬疑', u'犯罪', u'恐怖', u'青春', u'励志', u'战争', u'文艺', u'黑色幽默', u'传记',
            u'情色', u'暴力', u'音乐', u'家庭', u'治愈']
    url_pattern = "https://movie.douban.com/j/search_subjects?type=movie&tag=%s&sort=recommend&page_limit=20&page_start=%d"
    mongo_uri = "127.0.0.1:19191"
    mongo_db = "douban"
    collection_name = "movie_items"

    def start_requests(self):
        for start in range(0, 310, 20):
            for tag in self.tags:
                url = (self.url_pattern) % (tag, start)
                # print url
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # self.log("status: %d, content: %s" % (response.status, response.body), logging.INFO)
        if response.status == 200:
            data = json.loads(response.text)
            movie_list = data['subjects']
            for i in range(len(movie_list)):
                movie_data = movie_list[i]
                self.log("id: %s, rate: %s, title: %s, url: %s" % (
                    movie_data['id'], movie_data['rate'], movie_data['title'], movie_data['url']), logging.INFO)
                yield scrapy.Request(movie_data['url'], callback=self.detail_parse)

    def detail_parse(self, response):
        if response.status == 200:
            try:
                movie_id = response.url.lstrip("https://").split("/")[2]
                name = response.xpath("//div[@id='content']//span[@property='v:itemreviewed']/text()").extract()[0]
                year = response.xpath("//div[@id='content']//span[@class='year']/text()").extract()[0]
                year = year.strip("()")
                rating_average = \
                    response.xpath(
                        "//div[@class='rating_self clearfix']//strong[@class='ll rating_num']/text()").extract()[0]
                rating_sum = \
                    response.xpath(
                        "//div[@class='rating_self clearfix']//div[@class='rating_sum']/a/span/text()").extract()[0]
                director_span_list = response.xpath("//div[@id='info']//a[@rel='v:directedBy']")
                directors = set()
                for director in director_span_list:
                    directors.add(director.xpath("./text()").extract()[0])
                actor_span_list = response.xpath("//div[@id='info']//span[@class='attrs']//a[@rel='v:starring']")
                actors = set()
                for actor in actor_span_list:
                    actors.add(actor.xpath("./text()").extract()[0])
                genre_span_list = response.xpath("//div[@id='info']//span[@property='v:genre']")
                genres = set()
                for genre in genre_span_list:
                    genres.add(genre.xpath("./text()").extract()[0])
                show_time = -1
                try:
                    show_time = \
                        response.xpath("//div[@id='info']//span[@property='v:initialReleaseDate']/text()").extract()[0]
                except IndexError:
                    self.log("url %s has no show time!" % response.url, logging.ERROR)
                    pass
                duration = -1
                try:
                    duration = response.xpath("//div[@id='info']//span[@property='v:runtime']/text()").extract()[0]
                except IndexError:
                    self.log("url %s has no duration!" % response.url, logging.ERROR)
                    pass
                keywords = response.xpath("//meta[@name='keywords']/@content").extract()[0]
                description = response.xpath("//meta[@name='description']/@content").extract()[0]

                item = MovieItem()
                item["movie_id"] = int(movie_id)
                item["movie_name"] = name
                item["movie_year"] = int(year)
                item["rating_average"] = float(rating_average)
                item["rating_sum"] = int(rating_sum)
                item["directors"] = u",".join(directors)
                item["actors"] = u",".join(actors)
                item["categories"] = u",".join(genres)
                item["show_time"] = show_time
                item["duration"] = duration
                item["keywords"] = keywords
                item["description"] = description
                item["url"] = response.url

                yield item
                # yield {
                #     "movie_id": int(movie_id),
                #     "movie_name": name,
                #     "year": int(year),
                #     "rating_average": float(rating_average),
                #     "rating_sum": int(rating_sum),
                #     "directors": u",".join(directors),
                #     "actors": u",".join(actors),
                #     "categories": u",".join(genres),
                #     "show_time": show_time,
                #     "duration": duration,
                #     "keywords": keywords,
                #     "description": description,
                #     "url": response.url,
                # }
            except IndexError:
                self.log("process url %s error!" % response.url, logging.ERROR)
                pass
        else:
            self.log("request url %s error! response code %d" % (response.url, response.status), logging.ERROR)
