#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: push_urls.py.py
@time: 2017/7/31 09:38
"""

import argparse
import logging
import os
import sys

import redis


def init_logging(file_name):
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename="{0}.log".format(file_name),
                        filemode="a")


def connect_redis(host, port, db_index, password):
    """
    connect to specified redis server
    :param host: the host of the redis server
    :param port: the port of the redis server
    :param db_index: the db index of the redis server
    :param password: the password of the redis server
    :return: the StrictRedis object
    """
    redis_conn = redis.StrictRedis(host=host, port=port, db=db_index, password=password, socket_timeout=5000)

    return redis_conn


if __name__ == "__main__":
    init_logging(os.path.basename(sys.argv[0]).rstrip(".py"))
    parser = argparse.ArgumentParser(prog="push_urls", version="%(prog)s 1.0",
                                     description="Add the url in urls file to redis database")
    parser.add_argument("-f", "--urls-file", dest="urls_file", required=True,
                        help="The urls file that contains the url you want to crawl")
    parser.add_argument("-h", "--host", dest="host", required=True, help="The host of the redis database")
    parser.add_argument("-p", "--port", dest="port", type=int, required=True, help="The port of the redis database")
    parser.add_argument("-i", "--index", dest="index", required=True, help="The db index of the redis database")
    parser.add_argument("-p", "--password", dest="password", required=True, help="The password of the redis database")
    parser.add_argument("-k", "--key", dest="key", required=True,
                        help="The key in the redis database that used to store crawl url")

    options = parser.parse_args()
    file_name = options.url_file
    host = options.host
    port = options.port
    db_index = options.index
    password = options.password
    key = options.key

    redis_conn = connect_redis(host=host, port=port, db_index=db_index, password=password)
    with open(file=file_name, mode="r") as fd:
        for line in fd:
            line = line.strip()
            redis_conn.rpushx(name=key, value=line)
