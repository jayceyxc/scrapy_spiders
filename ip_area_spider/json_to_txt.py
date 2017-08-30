#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: json_to_txt.py
@time: 29/08/2017 14:37
"""

import json
import os
import socket


class IpRange(object):
    def __init__( self, kid, orig_start_ip, orig_end_ip, start_ip, end_ip, area_id, area_name ):
        super(IpRange, self).__init__()
        if ip_check(start_ip) and ip_check(end_ip):
            self.kid = kid
            self.start_ip = ip_decompose(start_ip)
            self.start_ip[3] = 0
            self.end_ip = ip_decompose(end_ip)
            self.end_ip[3] = 255
            self.area_id = area_id
            self.area_name = area_name
            self.start_ip_long = socket.inet_aton('.'.join(map(str, self.start_ip)))
            self.end_ip_long = socket.inet_aton('.'.join(map(str, self.end_ip)))
            self.orig_start_ip = orig_start_ip
            self.orig_end_ip = orig_end_ip
            self.insert_sql_pattern = 'INSERT INTO rmc_area_ip_fixed (id, area_name, start_ip, start_ip_long, end_ip, end_ip_long, type) VALUES ({0}, "{1}", "{2}", INET_ATON("{2}"), "{3}", INET_ATON("{3}"), 0);'
            self.update_sql_pattern = 'UPDATE rmc_area_ip_fixed set id={0} where kid={1};'
            assert self.start_ip_long < self.end_ip_long

    def __eq__( self, other ):
        if not isinstance(other, IpRange):
            return False
        if self.start_ip == other.start_ip \
                and self.end_ip == other.end_ip \
                and self.area_id == other.area_id:
            return True
        else:
            return False

    def __cmp__( self, other ):
        assert isinstance(other, IpRange)
        if self.start_ip_long == other.start_ip_long and self.end_ip_long == other.end_ip_long:
            return 0
        elif self.end_ip_long < other.start_ip_long:
            return -1
        elif self.start_ip_long > other.end_ip_long:
            return 1

    def __repr__( self ):
        display = "区域ID: {0}, 区域名称: {1}, 起始IP: {2}, 结束IP: {3}".format(self.area_id, self.area_name,
                                                                      '.'.join(map(str, self.start_ip)),
                                                                      '.'.join(map(str, self.end_ip)))
        display += os.linesep
        return display

    def update_ip_range( self, ip, area_id ):
        if not ip_check(ip):
            print("not valid ip: {0}".format(ip))
            return False

        if area_id != self.area_id:
            return False

        update = False
        ip_arr = ip_decompose(ip)
        if ip_arr[:2] == self.start_ip[:2] and ip_arr[2] == self.start_ip[2] - 1:
            self.start_ip[2] = ip_arr[2]
            update = True

        if ip_arr[:2] == self.end_ip[:2] and ip_arr[2] == self.end_ip[2] + 1:
            self.end_ip[2] = ip_arr[2]
            update = True

        return update

    def merge_ip_range( self, other ):
        assert isinstance(other, IpRange)
        # print("merge: ", self, other)
        if self.area_id != other.area_id:
            return False

        if other.start_ip[0] == self.start_ip[0] - 1:
            if other.start_ip[1] == 255 and other.start_ip[2] == 255 and \
                            self.start_ip[1] == 0 and self.start_ip[2] == 0:
                """
                self: 11.0.0.0
                other: 10.255.255.0
                """
                self.start_ip = other.start_ip
                self.start_ip_long = other.start_ip_long
                return True
        elif other.start_ip[0] == self.start_ip[0]:
            if other.start_ip[1] == self.start_ip[1] - 1:
                if other.start_ip[2] == 255 and self.start_ip[2] == 0:
                    """
                    self: 10.221.0.0
                    other: 10.220.255.0
                    """
                    self.start_ip = other.start_ip
                    self.start_ip_long = other.start_ip_long
                    return True
            elif other.start_ip[1] == self.start_ip[1]:
                if other.start_ip[2] == self.start_ip[2] - 1:
                    """
                    self: 10.221.254.0
                    other: 10.221.253.0
                    """
                    self.start_ip = other.start_ip
                    self.start_ip_long = other.start_ip_long
                    return True

        if other.end_ip[0] == self.end_ip[0] + 1:
            if self.end_ip[1] == 255 and self.end_ip[2] == 255 and \
                            other.end_ip[1] == 0 and other.end_ip[2] == 0:
                """
                self: 10.255.255.255
                other: 11.0.0.255
                """
                self.end_ip = other.end_ip
                self.end_ip_long = other.end_ip_long
                return True
        elif other.end_ip[0] == self.end_ip[0]:
            if other.end_ip[1] == self.end_ip[1] + 1:
                if other.end_ip[2] == 0 and self.end_ip[2] == 255:
                    """
                    self: 10.221.255.255
                    other: 10.222.0.255
                    """
                    self.end_ip = other.end_ip
                    self.end_ip_long = other.end_ip_long
                    return True
            elif other.end_ip[1] == self.end_ip[1]:
                if other.end_ip[2] == self.end_ip[2] + 1:
                    """
                    self: 10.221.243.255
                    other: 10.221.244.255
                    """
                    self.end_ip = other.end_ip
                    self.end_ip_long = other.end_ip_long
                    return True

        return False

    def generate_sql( self ):
        start_ip_str = '.'.join(map(str, self.start_ip))
        end_ip_str = '.'.join(map(str, self.end_ip))
        if self.orig_start_ip == start_ip_str and self.orig_end_ip == end_ip_str:
            return self.update_sql_pattern.format(self.area_id, self.kid)
        else:
            return self.insert_sql_pattern.format(int(self.area_id), self.area_name, start_ip_str, end_ip_str)


def ip_check( ip ):
    q = ip.split('.')
    return len(q) == 4 and len(
        filter(lambda x: 0 <= x <= 255, map(int, filter(lambda x: x.isdigit(), q)))) == 4


def ip_decompose( ip ):
    if ip_check(ip):
        return map(int, ip.split('.'))


def analysis_ip_range():
    global id_area_map
    ip_range_list = list()
    with open("ip_area_id_test.json", mode="r") as fd:
        for line in fd:
            line = line.strip()
            record = json.loads(line)
            if record["id"] == record["prev_id"] or not record['id'] in id_area_map:
                continue

            # print u"\t".join([record["ip"], record["id"], record["area_name"].encode('utf-8'), record["start_ip"], record["end_ip"]])
            # print record['area_name']
            # print record["ip"], record["id"], record["area_name"].encode('utf-8'), record["start_ip"], record["end_ip"]
            area_name = id_area_map[record['id']]
            ip_range = IpRange(kid=record['kid'], orig_start_ip=record['start_ip'], orig_end_ip=record['end_ip'],
                               start_ip=record['ip'], end_ip=record['ip'], area_id=record['id'], area_name=area_name)
            # print ip_range
            ip_range_list.append(ip_range)

    sorted_ip_list = sorted(ip_range_list)
    print(sorted_ip_list)

    merge_ip_range_list = list()
    index = 0
    while index < len(sorted_ip_list):
        ip_range = sorted_ip_list[index]
        index += 1
        for i in range(index, len(sorted_ip_list), 1):
            if not ip_range.merge_ip_range(sorted_ip_list[i]):
                break
            else:
                index += 1
        # print("After merge: ", ip_range)
        merge_ip_range_list.append(ip_range)

    print("final result: ")
    print(merge_ip_range_list)
    return merge_ip_range_list


def main():
    with open("ip_area_id.json", mode="r") as fd:
        for line in fd:
            line = line.strip()
            record = json.loads(line)
            if record["id"] == record["prev_id"]:
                continue

            # print u"\t".join([record["ip"], record["id"], record["area_name"].encode('utf-8'), record["start_ip"], record["end_ip"]])
            # print record['area_name']
            print(record["ip"], record["id"], record["area_name"].encode('utf-8'), record["start_ip"], record["end_ip"])


def load_id_map():
    id_map_dict = dict()
    current_path = os.path.split(os.path.realpath(__file__))[0]
    file_name = current_path + os.sep + "ip_area_spider" + os.sep + "id_area_map.txt"
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
                id_map_dict[id] = area_name

    return id_map_dict


id_area_map = load_id_map()
if __name__ == "__main__":
    # print ip_check("192.18.12.1")
    # print ip_check("21.323.22.232")
    ip_list = analysis_ip_range()
    with open('update_rmc.sql', mode='w') as fd:
        for ip_range in ip_list:
            sql_statement = ip_range.generate_sql()
            fd.write(sql_statement)
            fd.write(os.linesep)

            # main()
