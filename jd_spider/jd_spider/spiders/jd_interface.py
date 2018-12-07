#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: jd_interface.py
@time: 2017/2/17 上午11:31
"""

from bs4 import BeautifulSoup
import urllib2
import sys
import json
import leveldb
import requests


reload(sys)
sys.setdefaultencoding("utf-8")

cate_dict = {"9987_653_655":"手机"}


def load_category_map(filename):
    global cate_dict
    with open(filename, "r") as fd:
        for line in fd:
            line = line.strip()
            cate_id, cate_name = line.split("\t", 1)
            cate_dict[cate_id] = cate_name


def get_category_name(cate_dict, cate_id):
    if cate_id in cate_dict:
        return cate_dict[cate_id]
    else:
        return "未知分类"


def parse_url_params(url):
    params = []
    if len(url.split('?')) > 1:
        params = url.split('?')[1].split('&')
    elif len(url.split('#')) > 1:
        params = url.split('#')[1].split('&')

    param_kv_dict = {}
    for pair in params:
        if len(pair.split('=')) == 2:
            (key, value) = pair.split('=')
            if value != '':
                param_kv_dict[key] = value

    return param_kv_dict


def get_item_info(ware_id):
    global cate_dict
    url = "http://item.m.jd.com/product/"+ str(ware_id)+".html"
    req = urllib2.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36')
    response = urllib2.urlopen(req)
    content = response.read()
    soup = BeautifulSoup(content, 'html.parser')
    item_info = dict()
    for i in soup.find_all('input'):
        try:
            type = i['type']
            id = i['id']
            if u'hidden' == type:
                if id == "currentWareId":
                    item_info[u"商品ID"] = i['value']
                elif id == "goodName":
                    item_info[u"商品名称"] = i['value']
                elif id == "jdPrice":
                    item_info[u"京东价"] = i['value']
                elif id == "categoryId":
                    item_info[u"商品分类"]  = get_category_name(cate_dict, i["value"])

        except KeyError:
            print "Key Error"
            continue

    if item_info.has_key(u"商品ID"):
        total_comments, good_comments, normal_comments, bad_comments = get_jd_comment_count(item_info[u"商品ID"])
        item_info[u"评价总数"] = total_comments
        item_info[u"好评数"] = good_comments
        item_info[u"中评数"] = normal_comments
        item_info[u"差评数"] = bad_comments
    return item_info


def get_jd_comment_count(ware_id):
    url = 'http://item.m.jd.com/ware/getDetailCommentList.json?wareId=' + str(ware_id)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}
    r2 = requests.get(url=url, headers=headers)
    data = json.loads(r2.text, encoding='utf-8')
    return data['wareDetailComment']['allCnt'],data['wareDetailComment']['goodCnt'],data['wareDetailComment']['normalCnt'],data['wareDetailComment']['badCnt']

if __name__ == "__main__":
    ware_ids = ["3034770", "3133853", "3740498", "3629977", "2938299", "3435085", "3352172", "1176133", "1095474","1965719893"]
    for _id in ware_ids:
        item, exists = get_item_info(_id)
        print json.dumps(item, ensure_ascii=False)
