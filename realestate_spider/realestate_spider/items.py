# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html


import sys
reload(sys)
sys.setdefaultencoding('utf8')
from abc import abstractmethod
import re

import scrapy
from scrapy import Field


class RealestateItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 类型，新房、租房还是二手房
    type = Field()
    # 房产的来源url
    refer = Field()
    # 房产链接
    url = Field()
    # 标签
    label = Field()
    # 标题
    title = Field()
    # 地区名称
    region = Field()
    # 小区名称
    community = Field()

    @abstractmethod
    def generate_label(self):
        return NotImplemented


class ResoldApartmentItem(RealestateItem):

    # 总价
    total_price = Field()
    # 每平米单价
    unit_price = Field()

    # 建筑面积
    area = Field()
    # 朝向: 东、南、西、北、南北
    orientation = Field()
    # 装修: 毛坯、简装、精装或其他装修
    decoration = Field()
    # 楼层
    floor = Field()
    # 房屋类型: 住宅、别墅、商铺或其他类型
    house_type = Field()
    # 建筑年代
    year = Field()
    # 卧室数量
    bedrooms = Field()

    def __init__(self):
        super(ResoldApartmentItem, self).__init__()
        self['type'] = u'二手房'
        self['house_type'] = u"未知"

    def generate_label(self):
        label_set = set()

        region = self['region']
        if region.find(u"雨花") != -1:
            label_set.add(u"二手房_雨花区")
        elif region.find(u"岳麓") != -1:
            label_set.add(u"二手房_岳麓区")
        elif region.find(u"天心") != -1:
            label_set.add(u"二手房_天心区")
        elif region.find(u"开福") != -1:
            label_set.add(u"二手房_开福区")
        elif region.find(u"芙蓉") != -1:
            label_set.add(u"二手房_芙蓉区")
        else:
            label_set.add(u"二手房_其他地区")

        total_price = self['total_price']
        if total_price < 40:
            label_set.add(u'二手房_40万以下')
        elif 40 <= total_price < 60:
            label_set.add(u'二手房_40_60万')
        elif 60 <= total_price < 80:
            label_set.add(u'二手房_60_80万')
        elif 80 <= total_price < 100:
            label_set.add(u'二手房_80_100万')
        elif 100 <= total_price < 120:
            label_set.add(u'二手房_100_120万')
        elif 120 <= total_price < 150:
            label_set.add(u'二手房_120_150万')
        elif 150 <= total_price < 200:
            label_set.add(u'二手房_150_200万')
        elif total_price > 200:
            label_set.add(u'二手房_200万以上')

        bedrooms = self['bedrooms']
        if bedrooms == 1:
            label_set.add(u'二手房_一室')
        elif bedrooms == 2:
            label_set.add(u'二手房_二室')
        elif bedrooms == 3:
            label_set.add(u'二手房_三室')
        elif bedrooms == 4:
            label_set.add(u'二手房_四室')
        elif bedrooms >= 5:
            label_set.add(u'二手房_五室及以上')

        area = self['area']
        if area < 50:
            label_set.add(u'二手房_50平以下')
        elif 50 <= area < 70:
            label_set.add(u'二手房_50_70平')
        elif 70 <= area < 90:
            label_set.add(u'二手房_70_90平')
        elif 90 <= area < 110:
            label_set.add(u'二手房_90_110平')
        elif 110 <= area < 130:
            label_set.add(u'二手房_110_130平')
        elif 130 <= area < 150:
            label_set.add(u'二手房_130_150平')
        elif 150 <= area < 200:
            label_set.add(u'二手房_150_200平')
        elif 200 <= area < 300:
            label_set.add(u'二手房_200_300平')
        elif area >= 300:
            label_set.add(u'二手房_300平以上')

        orientation = self['orientation']
        if orientation.find(u'东') != -1:
            label_set.add(u'二手房_朝向东')
        if orientation.find(u'西') != -1:
            label_set.add(u'二手房_朝向西')
        if orientation.find(u'南') != -1 and orientation.find(u'北') != -1:
            label_set.add(u'二手房_朝向南北')
        elif orientation.find(u'南') != -1:
            label_set.add(u'二手房_朝向南')
        elif orientation.find(u'北') != -1:
            label_set.add(u'二手房_朝向北')

        decoration = self['decoration']
        if decoration.find(u'毛坯') != -1 or decoration.find(u'清水') != -1:
            label_set.add(u'二手房_毛坯')
        elif decoration.find(u'简装') != -1 or decoration.find(u'中装') != -1 \
                or decoration.find(u'简单装修') != -1 or decoration.find(u'中等装修') != -1:
            label_set.add(u'二手房_简装')
        elif decoration.find(u'精装') != -1 or decoration.find(u'豪华装修') != -1:
            label_set.add(u'二手房_精装')
        else:
            label_set.add(u'二手房_其他装修')

        refer = self['refer']
        if refer.find('t1') != -1 \
                or re.match(r"https://cs.lianjia.com/ershoufang/(.*)?sf1/", refer) is not None:
            label_set.add(u'二手房_住宅')
        elif refer.find('t2') != -1 \
                or re.match(r"https://cs.lianjia.com/ershoufang/(.*)?sf3/", refer) is not None:
            label_set.add(u'二手房_别墅')
        elif refer.find('t4') != -1:
            label_set.add(u'二手房_商铺')
        elif refer.find('t3') != -1\
                or refer.find('t5') != -1\
                or refer.find('t6') != -1 \
                or re.match(r"https://cs.lianjia.com/ershoufang/(.*)?sf4/", refer) is not None \
                or re.match(r"https://cs.lianjia.com/ershoufang/(.*)?sf5/", refer) is not None:
            label_set.add(u'二手房_其他类型')

        # anjuke has house_type
        house_type = self['house_type']
        if house_type != u"未知":
            if house_type.find(u'普通住宅') != -1 or house_type.find(u'住宅') != -1:
                label_set.add(u'二手房_住宅')
            elif house_type.find(u'别墅') != -1:
                label_set.add(u'二手房_别墅')
            elif house_type.find(u'商铺') != -1:
                label_set.add(u'二手房_商铺')
            else:
                label_set.add(u'二手房_其他类型')

        return label_set


class LoufanItem(RealestateItem):
    # 每平米单价
    unit_price = Field()
    # 房屋类型: 住宅、别墅、商铺或其他类型
    house_type = Field()
    # 新盘地址
    address = Field()

    def __init__(self):
        super(LoufanItem, self).__init__()
        self['type'] = u'新房'
        self['house_type'] = u"未知"
        self['address'] = u"未知"

    def generate_label(self):
        label_set = set()

        region = self['region']
        if region.find(u"雨花") != -1:
            label_set.add(u"新房_雨花区")
        elif region.find(u'岳麓') != -1:
            label_set.add(u"新房_岳麓区")
        elif region.find(u'芙蓉') != -1:
            label_set.add(u"新房_芙蓉区")
        elif region.find(u'开福') != -1:
            label_set.add(u"新房_开福区")
        elif region.find(u'天心') != -1:
            label_set.add(u"新房_天心区")
        elif region.find(u'望城') != -1 \
                or region.find(u'星沙') != -1 \
                or region.find(u'长沙县') != -1 \
                or region.find(u'长株潭') != -1:
            label_set.add(u"新房_其他地区")

        try:
            unit_price = int(self['unit_price'])
            if 1500 < unit_price < 5000:
                """
                some house is the total price, here except the price smaller than 1500.
                """
                label_set.add(u'新房_5千以下')
            elif 5000 <= unit_price < 7000:
                label_set.add(u'新房_5千_7千')
            elif 7000 <= unit_price < 9000:
                label_set.add(u'新房_7千_9千')
            elif 9000 <= unit_price < 12000:
                label_set.add(u'新房_9千_1万2')
            elif 12000 <= unit_price < 15000:
                label_set.add(u'新房_1万2_1万5')
            elif unit_price > 15000:
                label_set.add(u'新房_1万5以上')
        except ValueError as ve:
            pass

        refer = self['refer']
        if refer.find('house.leju.com/cs/search/c1') != -1 \
                or re.match(r"https://cs.fang.anjuke.com/loupan/all/h1(.*)?/", refer) is not None \
                or re.match(r"http://cs.fang.lianjia.com/loupan/(.*)?l1/", refer) is not None:
            label_set.add(u'新房_一室')
        elif refer.find('house.leju.com/cs/search/c2') != -1 \
                or re.match(r"https://cs.fang.anjuke.com/loupan/all/h2(.*)?/", refer) is not None \
                or re.match(r"http://cs.fang.lianjia.com/loupan/(.*)?l2/", refer) is not None:
            label_set.add(u'新房_二室')
        elif refer.find('house.leju.com/cs/search/c3') != -1 \
                or re.match(r"https://cs.fang.anjuke.com/loupan/all/h3(.*)?/", refer) is not None \
                or re.match(r"http://cs.fang.lianjia.com/loupan/(.*)?l3/", refer) is not None:
            label_set.add(u'新房_三室')
        elif refer.find('house.leju.com/cs/search/c4') != -1 \
                or re.match(r"https://cs.fang.anjuke.com/loupan/all/h4(.*)?/", refer) is not None \
                or re.match(r"http://cs.fang.lianjia.com/loupan/(.*)?l4/", refer) is not None:
            label_set.add(u'新房_四室')
        elif refer.find('house.leju.com/cs/search/c5') != -1 \
                or refer.find('house.leju.com/cs/search/c6') != -1 \
                or refer.find('house.leju.com/cs/search/c7') != -1 \
                or re.match(r"https://cs.fang.anjuke.com/loupan/all/h5(.*)?/", refer) is not None \
                or re.match(r"http://cs.fang.lianjia.com/loupan/(.*)?l5/", refer) is not None \
                or re.match(r"http://cs.fang.lianjia.com/loupan/(.*)?l6/", refer) is not None:
            label_set.add(u'新房_五室及以上')

        if refer.find('house.leju.com/cs/search/f1') != -1 \
                or re.match(r"https://cs.fang.anjuke.com/loupan/all/(.*)?w1/", refer) is not None:
            label_set.add(u'新房_住宅')
        elif refer.find('house.leju.com/cs/search/f3') != -1 \
                or re.match(r"https://cs.fang.anjuke.com/loupan/all/(.*)?w2/", refer) is not None:
            label_set.add(u'新房_别墅')
        elif refer.find('house.leju.com/cs/search/f8') != -1 \
                or re.match(r"https://cs.fang.anjuke.com/loupan/all/(.*)?w4/", refer) is not None:
            label_set.add(u'新房_商铺')
        elif refer.find('house.leju.com/cs/search/f2') != -1\
                or refer.find('house.leju.com/cs/search/f4') != -1 \
                or re.match(r"https://cs.fang.anjuke.com/loupan/all/(.*)?w3/", refer) is not None \
                or re.match(r"https://cs.fang.anjuke.com/loupan/all/(.*)?w5/", refer) is not None:
            label_set.add(u'新房_其他类型')

        # lianjia has house_type
        house_type = self['house_type']
        if house_type != u"未知":
            if house_type.find(u'普通住宅') != -1 or house_type.find(u'住宅') != -1:
                label_set.add(u'新房_住宅')
            elif house_type.find(u'别墅') != -1:
                label_set.add(u'新房_别墅')
            elif house_type.find(u'商铺') != -1:
                label_set.add(u'新房_商铺')
            else:
                label_set.add(u'新房_其他类型')
            return label_set

        return label_set


class RentHouseItem(RealestateItem):
    # 租金
    rent_price = Field()
    # 付款方式
    billing_type = Field()
    # 租赁方式
    rent_type = Field()
    # 建筑面积
    area = Field()
    # 朝向: 东、南、西、北、南北
    orientation = Field()
    # 装修: 毛坯、简装、精装或其他装修
    decoration = Field()
    # 楼层
    floor = Field()
    # 建筑年代
    year = Field()
    # 卧室数量
    bedrooms = Field()

    def __init__( self ):
        super(RentHouseItem, self).__init__()
        self['type'] = u'租房'

    def generate_label(self):
        label_set = set()

        region = self['region']
        if region.find(u"雨花") != -1:
            label_set.add(u"租房_雨花区")
        elif region.find(u"岳麓") != -1:
            label_set.add(u"租房_岳麓区")
        elif region.find(u"天心") != -1:
            label_set.add(u"租房_天心区")
        elif region.find(u"开福") != -1:
            label_set.add(u"租房_开福区")
        elif region.find(u"芙蓉") != -1:
            label_set.add(u"租房_芙蓉区")
        else:
            label_set.add(u"租房_其他地区")

        rent_price = self['rent_price']
        if rent_price < 1000:
            label_set.add(u'租房_1千以下')
        elif 1000 <= rent_price < 1500:
            label_set.add(u'租房_1千_1千5')
        elif 1500 <= rent_price < 2000:
            label_set.add(u'租房_1千5_2千')
        elif 2000 <= rent_price < 2500:
            label_set.add(u'租房_2千_2千5')
        elif 2500 <= rent_price < 3000:
            label_set.add(u'租房_2千5_3千')
        elif 3000 <= rent_price < 5000:
            label_set.add(u'租房_3千_5千')
        elif rent_price >= 5000:
            label_set.add(u'租房_5千以上')

        bedrooms = self['bedrooms']
        if bedrooms == 1:
            label_set.add(u'租房_一室')
        elif bedrooms == 2:
            label_set.add(u'租房_二室')
        elif bedrooms == 3:
            label_set.add(u'租房_三室')
        elif bedrooms == 4:
            label_set.add(u'租房_四室')
        elif bedrooms >= 5:
            label_set.add(u'租房_五室及以上')

        return label_set
