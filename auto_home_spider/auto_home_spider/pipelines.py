# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import ahocorasick
import pymongo
import glob
import os
from items import CarItem


class JsonFilePipeline(object):
    url_label_dict = {
        u"价格-0-5" : "car.autohome.com.cn/price/list-0_5-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-5-8" : "car.autohome.com.cn/price/list-5_8-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-8-10": "car.autohome.com.cn/price/list-8_10-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-10-15": "car.autohome.com.cn/price/list-10_15-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-15-20": "car.autohome.com.cn/price/list-15_20-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-20-25": "car.autohome.com.cn/price/list-20_25-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-25-35": "car.autohome.com.cn/price/list-25_35-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-35-50": "car.autohome.com.cn/price/list-35_50-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-50-100": "car.autohome.com.cn/price/list-50_100-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-100-above": "car.autohome.com.cn/price/list-100_0-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-0-1.0" : "car.autohome.com.cn/price/list-0-0-0_1.0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-1.1_1.6": "car.autohome.com.cn/price/list-0-0-1.1_1.6-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-1.7_2.0": "car.autohome.com.cn/price/list-0-0-1.7_2.0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-2.1_2.5": "car.autohome.com.cn/price/list-0-0-2.1_2.5-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-2.6_3.0": "car.autohome.com.cn/price/list-0-0-2.6_3.0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-3.1_4.0": "car.autohome.com.cn/price/list-0-0-3.1_4.0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-4.0_above": "car.autohome.com.cn/price/list-0-0-4.0_0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"自动" : "car.autohome.com.cn/price/list-0-0-0-0-1-0-0-0-0-0-0-0-0-0-0",
        u"手动" : "car.autohome.com.cn/price/list-0-0-0-0-101-0-0-0-0-0-0-0-0-0-0",
        u"手自一体": "car.autohome.com.cn/price/list-0-0-0-0-9-0-0-0-0-0-0-0-0-0-0",
        u"微型车": "http://car.autohome.com.cn/price/list-0-1-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"小型车": "http://car.autohome.com.cn/price/list-0-2-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"紧凑型车": "http://car.autohome.com.cn/price/list-0-3-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"中型车": "http://car.autohome.com.cn/price/list-0-4-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"中大型车": "http://car.autohome.com.cn/price/list-0-5-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"大型车": "http://car.autohome.com.cn/price/list-0-6-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"跑车": "http://car.autohome.com.cn/price/list-0-7-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"MPV": "http://car.autohome.com.cn/price/list-0-8-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"SUV": "http://car.autohome.com.cn/price/list-0-9-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"微面": "http://car.autohome.com.cn/price/list-0-11-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"微卡": "http://car.autohome.com.cn/price/list-0-12-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"轻客": "http://car.autohome.com.cn/price/list-0-13-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"皮卡": "http://car.autohome.com.cn/price/list-0-14-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
    }

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            label_url_dir=crawler.settings.get('LABEL_URL_MAP_DIR', "label_url"),
        )

    @staticmethod
    def init_ac(label_url_dir):
        automation = ahocorasick.Automaton()
        current_path = os.path.split(os.path.realpath(__file__))[0]
        for file_name in glob.glob(current_path + os.sep + label_url_dir + os.sep + "*_label_url.txt"):
            with open(file_name, mode="r") as fd:
                for line in fd:
                    line = line.strip()
                    if line is None or len(line) == 0:
                        continue
                    label, url = line.split(None, 1)
                    automation.add_word(url, label)

        automation.make_automaton()
        return automation

    def __init__(self, label_url_dir):
        self.file = open('cars_url.json', 'wb')
        self.automation = JsonFilePipeline.init_ac(label_url_dir)

    def process_item(self, item, spider):
        if isinstance(item, CarItem):
            for end_index, tag_id in self.automation.iter(item["refer"]):
                item["label"] = tag_id

            line = json.dumps(dict(item)) + "\n"
            self.file.write(line)
            return item


class MongoPipeline(object):
    collection_name = 'autohome_cars'
    """
    url_label_dict = {
        u"价格-0-5" : "car.autohome.com.cn/price/list-0_5-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-5-8" : "car.autohome.com.cn/price/list-5_8-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-8-10": "car.autohome.com.cn/price/list-8_10-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-10-15": "car.autohome.com.cn/price/list-10_15-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-15-20": "car.autohome.com.cn/price/list-15_20-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-20-25": "car.autohome.com.cn/price/list-20_25-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-25-35": "car.autohome.com.cn/price/list-25_35-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-35-50": "car.autohome.com.cn/price/list-35_50-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-50-100": "car.autohome.com.cn/price/list-50_100-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"价格-100-above": "car.autohome.com.cn/price/list-100_0-0-0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-0-1.0" : "car.autohome.com.cn/price/list-0-0-0_1.0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-1.1_1.6": "car.autohome.com.cn/price/list-0-0-1.1_1.6-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-1.7_2.0": "car.autohome.com.cn/price/list-0-0-1.7_2.0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-2.1_2.5": "car.autohome.com.cn/price/list-0-0-2.1_2.5-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-2.6_3.0": "car.autohome.com.cn/price/list-0-0-2.6_3.0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-3.1_4.0": "car.autohome.com.cn/price/list-0-0-3.1_4.0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"排量-4.0_above": "car.autohome.com.cn/price/list-0-0-4.0_0-0-0-0-0-0-0-0-0-0-0-0-0",
        u"自动" : "car.autohome.com.cn/price/list-0-0-0-0-1-0-0-0-0-0-0-0-0-0-0",
        u"手动" : "car.autohome.com.cn/price/list-0-0-0-0-101-0-0-0-0-0-0-0-0-0-0",
        u"手自一体": "car.autohome.com.cn/price/list-0-0-0-0-9-0-0-0-0-0-0-0-0-0-0",
        u"微型车": "http://car.autohome.com.cn/price/list-0-1-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"小型车": "http://car.autohome.com.cn/price/list-0-2-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"紧凑型车": "http://car.autohome.com.cn/price/list-0-3-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"中型车": "http://car.autohome.com.cn/price/list-0-4-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"中大型车": "http://car.autohome.com.cn/price/list-0-5-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"大型车": "http://car.autohome.com.cn/price/list-0-6-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"跑车": "http://car.autohome.com.cn/price/list-0-7-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"MPV": "http://car.autohome.com.cn/price/list-0-8-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"SUV": "http://car.autohome.com.cn/price/list-0-9-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"微面": "http://car.autohome.com.cn/price/list-0-11-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"微卡": "http://car.autohome.com.cn/price/list-0-12-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"轻客": "http://car.autohome.com.cn/price/list-0-13-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
        u"皮卡": "http://car.autohome.com.cn/price/list-0-14-0-0-0-0-0-0-0-0-0-0-0-0-0-1.html",
    }
    """

    def __init__(self, label_url_dir, mongo_uri, mongo_db):
        self.automation = MongoPipeline.init_ac(label_url_dir)
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            label_url_dir=crawler.settings.get('LABEL_URL_MAP_DIR', "label_url"),
            mongo_uri=crawler.settings.get('MONGO_URI', '127.0.0.1:19191'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    @staticmethod
    def init_ac(label_url_dir):
        automation = ahocorasick.Automaton()
        current_path = os.path.split(os.path.realpath(__file__))[0]
        for file_name in glob.glob(current_path + os.sep + label_url_dir + os.sep + "*_label_url.txt"):
            with open(file_name, mode="r") as fd:
                for line in fd:
                    line = line.strip()
                    if line is None or len(line) == 0:
                        continue
                    label, url = line.split(None, 1)
                    automation.add_word(url, label)

        automation.make_automaton()
        return automation

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        if self.client is not None:
            self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, CarItem):
            for end_index, tag_id in self.automation.iter(item["refer"]):
                item["label"] = tag_id

            result = self.db[self.collection_name].find({"label": item["label"], "url": item["url"], "refer": item["refer"]})
            if result.count() == 0:
                self.db[self.collection_name].insert_one(dict(item))

            return item