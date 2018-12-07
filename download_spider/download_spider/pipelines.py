#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import requests

from .items import DownloadItem


class DownloadSpiderPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, DownloadItem):
            session = requests.session()
            captcha_content = session.get(item['url']).content
            with open(item['filename']) as fd:
                fd.write(captcha_content)
