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
import traceback
from items import RealestateItem, ResoldApartmentItem, RentHouseItem, LoufanItem


class RealestateJsonFilePipeline(object):
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
        self.file = open('realestate_url.json', 'wb')
        self.automation = RealestateJsonFilePipeline.init_ac(label_url_dir)

    def process_item(self, item, spider):
        if isinstance(item, RealestateItem):
            for end_index, tag_id in self.automation.iter(item["refer"]):
                item["label"] = tag_id

            line = json.dumps(dict(item)) + "\n"
            self.file.write(line)
            return item


class RealestateMongoPipeline(object):
    collection_name = 'realestate'

    def __init__(self, label_url_dir, mongo_uri, mongo_db):
        self.rent_automation, self.loupan_automation, self.ershoufang_automation = RealestateMongoPipeline.init_ac(label_url_dir)
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
        rent_automation = ahocorasick.Automaton()
        loupan_automation = ahocorasick.Automaton()
        ershoufang_automation = ahocorasick.Automaton()
        current_path = os.path.split(os.path.realpath(__file__))[0]
        for file_name in glob.glob(current_path + os.sep + label_url_dir + os.sep + "*_label_url.txt"):
            with open(file_name, mode="r") as fd:
                for line in fd:
                    line = line.strip()
                    if line is None or len(line) == 0:
                        continue
                    label, url = line.split(None, 1)
                    if url.find("zufang") != -1:
                        rent_automation.add_word(url[url.find("zufang/") + len("zufang/"):], label)
                    elif url.find("loupan") != -1:
                        loupan_automation.add_word(url[url.find("loupan/") + len("loupan/"):], label)
                    elif url.find("ershoufang") != -1:
                        ershoufang_automation.add_word(url[url.find("ershoufang/") + len("ershoufang/"):], label)

        rent_automation.make_automaton()
        loupan_automation.make_automaton()
        ershoufang_automation.make_automaton()
        return rent_automation, loupan_automation, ershoufang_automation

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        if self.client is not None:
            self.client.close()

    def process_item(self, item, spider):
        """
        if isinstance(item, LoufanItem):
            refer = item['refer']
            label_refer = refer[refer.find("zufang/") + len("zufang/"):]
            label_refer = label_refer.lstrip("pg").lstrip("0123456789")
            if refer.find("zufang") != -1:
                for end_index, tag_id in self.rent_automation.iter(label_refer):
                    item["label"] = tag_id
            elif refer.find("loupan") != -1:
                for end_index, tag_id in self.loupan_automation.iter(label_refer):
                    item["label"] = tag_id
            elif refer.find("ershoufang") != -1:
                for end_index, tag_id in self.ershoufang_automation.iter(label_refer):
                    item["label"] = tag_id

            result = self.db[self.collection_name].find({"label": item["label"], "url": item["url"], "refer": item["refer"]})
            if result.count() == 0:
                self.db[self.collection_name].insert_one(dict(item))
            else:
                print("duplicate item, url: {0}, refer{1}".format(item['url'], item['refer']))
            pass
        """
        if isinstance(item, RealestateItem):
            """
            label_set = item.generate_label()
            for label in label_set:
                try:
                    item['label'] = label.encode('utf-8')
                    result = self.db[self.collection_name].find({"label": item['label'], "url": item["url"]})
                    if result.count() == 0:
                        self.db[self.collection_name].insert_one(dict(item))
                    else:
                        print("duplicate item, url: {0}, refer{1}".format(item['url'], item['refer']))
                except UnicodeDecodeError as ude:
                    traceback.print_exc()
            """
            refer = item['refer']
            collection_name = "realestate"
            if refer.find('lianjia.com') != -1:
                collection_name = 'lianjia'
            elif refer.find('leju.com') != -1:
                collection_name = 'leju'
            elif refer.find('anjuke.com') != -1:
                collection_name = 'anjuke'
            elif collection_name.find('fang.com'):
                collection_name = 'fang'
            label_set = item.generate_label()
            for label in label_set:
                item['label'] = label.encode('utf8')
                result = self.db[collection_name].find({"label": item['label'], "url": item["url"]})
                if result.count() == 0:
                    self.db[collection_name].insert_one(dict(item))
                else:
                    print("duplicate item, url: {0}, refer: {1}".format(item['url'], item['refer']))

            return item