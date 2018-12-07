#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import json
from .items import MovieItem, EmailItem


class JsonPipeline(object):
    def __init__(self):
        self.file = open('movies.json', 'wb')

    def process_item(self, item, spider):
        if isinstance(item, MovieItem):
            line = json.dumps(dict(item)) + "\n"
            self.file.write(line.encode())
            return item


class MongoPipeline(object):
    collection_name = 'movie_items'

    def __init__(self, mongo_uri, mongo_db, collection_name):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection_name = collection_name
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
            collection_name=crawler.settings.get('MONGO_COLLECTION', 'movie_items')
        )

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        #print "MongoPipeline" + str(item)
        if isinstance(item, MovieItem):
            result = self.db[self.collection_name].find({"movie_id":item["movie_id"]})
            if result.count() == 0:
                self.db[self.collection_name].insert(dict(item))
            else:
                print(result.count())
            return item
