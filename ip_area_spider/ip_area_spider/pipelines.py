# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import ahocorasick
import os
import json

from items import IpAreaItem


class IpAreaSpiderPipeline(object):

    def __init__(self):
        self.file = open('ip_area_id.json', 'wb')
        self.city_ac, self.province_ac = IpAreaSpiderPipeline.init_ac()

    @staticmethod
    def init_ac():
        city_automation = ahocorasick.Automaton()
        province_automation = ahocorasick.Automaton()
        current_path = os.path.split(os.path.realpath(__file__))[0]
        file_name = current_path + os.sep + "id_area_map.txt"
        with open(file_name, mode="r") as fd:
            for line in fd:
                line = line.strip()
                if line is None or len(line) == 0:
                    continue
                segs = line.split("\t")
                if len(segs) == 3:
                    id = segs[0].strip()
                    parent_id = segs[1].strip()
                    area_name = segs[2].strip()
                    if len(parent_id) == 0:
                        province_automation.add_word(area_name, id)
                    else:
                        city_automation.add_word(area_name, id)

        city_automation.make_automaton()
        province_automation.make_automaton()
        return city_automation, province_automation

    def process_item(self, item, spider):
        if isinstance(item, IpAreaItem):
            final_area_id = None
            try:
                for end_index, area_id in self.province_ac.iter(item["area_name"]):

                    final_area_id = area_id
            except AttributeError as ae:
                pass

            try:
                for end_index, area_id in self.city_ac.iter(item["area_name"]):
                    final_area_id = area_id
            except AttributeError as ae:
                pass

            if final_area_id is None:
                item["id"] = item["prev_id"]
            else:
                item["id"] = final_area_id
            line = json.dumps(dict(item)) + "\n"
            self.file.write(line)
            return item
