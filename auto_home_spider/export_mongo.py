#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: export_mongo.py
@time: 22/08/2017 12:57
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import pymongo


def load_label_name_id():
    tag_label_map = dict()
    with open(name="tag_name_id.txt", mode="r") as fd:
        for line in fd:
            line = line.strip()
            segs = line.split(None)
            if len(segs) == 4:
                tag_name = segs[2]
                label_id = segs[3]
                tag_name = tag_name.decode('utf8')
                print(tag_name, label_id)
                tag_label_map[tag_name] = label_id

    return tag_label_map


def export_url_label():
    mongo_uri = "127.0.0.1:19191"
    db_name = "autohome"
    collection_name = "autohome_cars"

    tag_label_map = load_label_name_id()
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    col = db[collection_name]
    cursor = col.find({}, {"url":1, "label":1, "_id":0})
    with open("url_label.txt", mode="w") as fd:
        for result in cursor:
            fd.write(u"\t".join([tag_label_map[result["label"]], result["url"]]))
            fd.write(os.linesep)
        fd.flush()


if __name__ == "__main__":
    export_url_label()
