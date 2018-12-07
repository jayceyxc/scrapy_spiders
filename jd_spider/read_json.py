#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: read_json.py
@time: 2017/3/20 上午10:13
"""

import sys
import os
import json

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: " + sys.argv[0] + " <filename>"
        sys.exit(-1)

    final = ""
    with open(sys.argv[1], 'r') as f:
        for line in f:
            line = line.strip()
            final += line

    #print final
    total = json.loads(final, encoding='utf8')
    for book_info in total:
        #print type(book_info)
        for key in book_info.keys():
            print key + ": " + book_info[key]


