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
import sys
import socket
import struct


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
            self.start_ip_long = convert_ip_to_long('.'.join(map(str, self.start_ip)))
            self.end_ip_long = convert_ip_to_long('.'.join(map(str, self.end_ip)))
            self.orig_start_ip = orig_start_ip
            self.orig_end_ip = orig_end_ip
            self.insert_sql_pattern = 'INSERT INTO rmc_area_ip_fixed (id, area_name, start_ip, start_ip_long, end_ip, end_ip_long, type) VALUES ("{0}", "{1}", "{2}", INET_ATON("{2}"), "{3}", INET_ATON("{3}"), 0);'
            self.update_sql_pattern = 'UPDATE rmc_area_ip_fixed set id="{0}", area_name="{1}" where kid={2};'
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

    def __cmp__(self, other):
        assert isinstance(other, IpRange)
        if self.start_ip_long == other.start_ip_long and self.end_ip_long == other.end_ip_long:
            return 0
        elif self.end_ip_long < other.start_ip_long:
            return -1
        elif self.start_ip_long > other.end_ip_long:
            return 1
        else:
            print self, other

    def __repr__( self ):
        display = "区域ID: {0}, 区域名称: {1}, 起始IP: {2}, 起始IP数字：{3}, 结束IP: {4}, 结束IP数字：{5}".format(self.area_id, self.area_name,
                                                                      '.'.join(map(str, self.start_ip)), self.start_ip_long,
                                                                      '.'.join(map(str, self.end_ip)), self.end_ip_long)
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
            return self.update_sql_pattern.format(self.area_id, self.area_name, self.kid)
        else:
            return self.insert_sql_pattern.format(int(self.area_id), self.area_name, start_ip_str, end_ip_str)


def ip_check( ip ):
    q = ip.split('.')
    return len(q) == 4 and len(
        filter(lambda x: 0 <= x <= 255, map(int, filter(lambda x: x.isdigit(), q)))) == 4


def ip_decompose( ip ):
    if ip_check(ip):
        return map(int, ip.split('.'))


# 从IP地址字符串转换为整数值
def convert_ip_to_long(ip_string):
    return struct.unpack("!L", socket.inet_aton(ip_string))[0]


# 从网络字节序的数字转换为IP地址（点号分隔）
def convert_long_to_ip(ip):
    return socket.inet_ntoa(struct.pack("!L", ip))


def analysis_ip_range():
    global id_area_map
    ip_range_list = list()
    with open("ip_area_id.json", mode="r") as fd:
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
    # print(sorted_ip_list)

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

    # print("final result: ")
    # print(merge_ip_range_list)
    return merge_ip_range_list


def load_old_ip_range():
    orig_ip_range_list = list()
    with open("rmc_area_ip_orig.txt", mode="r") as fd:
        for line in fd:
            line = line.strip()
            kid, id, area_name, start_ip, end_ip = line.split("\t")
            ip_range = IpRange(kid=kid, area_id=id, area_name=area_name, orig_start_ip=start_ip, orig_end_ip=end_ip, start_ip=start_ip, end_ip=end_ip)
            # print(ip_range)
            orig_ip_range_list.append(ip_range)

    return orig_ip_range_list


def merge_with_old(new_ip_list, old_ip_list):
    with open("update_rmc_new2.sql", mode="w") as out:
        for old_ip_range in old_ip_list:
            old_start_ip_long = old_ip_range.start_ip_long
            old_end_ip_long = old_ip_range.end_ip_long
            expect_start_ip_long = old_start_ip_long
            pre_end_ip_long = 0
            match_start = False
            match_end = False
            """
            mismatch 表示匹配过程中
            """
            mismatch = False
            """
            has_update 表示是否已经使用过UPDATE语句占用原来的kid，一个old_ip_range只能有一个UPDATE，其他的都是INSERT
            """
            has_update = False
            for new_ip_range in new_ip_list:
                new_start_ip_long = new_ip_range.start_ip_long
                new_end_ip_long = new_ip_range.end_ip_long
                if new_start_ip_long < old_start_ip_long:
                    continue
                if new_end_ip_long > old_end_ip_long:
                    break

                if new_start_ip_long == old_start_ip_long and new_end_ip_long == old_end_ip_long:
                    if has_update is True:
                        print("Has error, has update is already True. %s, %s", old_ip_range, new_ip_range)
                        out.close()
                        return 0
                    sql_statement = 'UPDATE rmc_area_ip_fixed set id="{0}", area_name="{1}" where kid={2};'.format(new_ip_range.area_id, new_ip_range.area_name, old_ip_range.kid)
                    out.write(sql_statement)
                    out.write(os.linesep)
                    break
                if new_start_ip_long == old_start_ip_long:
                    match_start = True
                if new_end_ip_long == old_end_ip_long:
                    match_end = True

                if has_update is False:
                    if new_start_ip_long > old_start_ip_long:
                        expect_start_ip_long = new_end_ip_long + 1
                        sql_statement = 'UPDATE rmc_area_ip_fixed set end_ip=INET_NTOA({0}), end_ip_long={0} WHERE kid={1};'.format(new_start_ip_long - 1, old_ip_range.kid)
                        out.write(sql_statement)
                        out.write(os.linesep)
                        sql_statement = 'INSERT INTO rmc_area_ip_fixed (id, area_name, start_ip, start_ip_long, end_ip, end_ip_long, type) VALUES ("{0}", "{1}", INET_NTOA({2}), {2}, INET_NTOA({3}), {3}, 0);'.format(new_ip_range.area_id, new_ip_range.area_name, new_ip_range.start_ip_long, new_ip_range.end_ip_long)
                        out.write(sql_statement)
                        out.write(os.linesep)
                        has_update = True
                    elif new_start_ip_long == old_start_ip_long:
                        expect_start_ip_long = new_end_ip_long + 1
                        sql_statement = 'UPDATE rmc_area_ip_fixed set end_ip=INET_NTOA({0}), end_ip_long={0} WHERE kid={1};'.format(new_end_ip_long, old_ip_range.kid)
                        out.write(sql_statement)
                        out.write(os.linesep)
                        has_update = True
                else:
                    if new_start_ip_long == expect_start_ip_long:
                        sql_statement = 'INSERT INTO rmc_area_ip_fixed (id, area_name, start_ip, start_ip_long, end_ip, end_ip_long, type) VALUES ("{0}", "{1}", INET_NTOA({2}), {2}, INET_NTOA({3}), {3}, 0);'.format(new_ip_range.area_id, new_ip_range.area_name, new_ip_range.start_ip_long, new_ip_range.end_ip_long)
                        out.write(sql_statement)
                        out.write(os.linesep)
                        expect_start_ip_long = new_end_ip_long + 1
                    elif new_start_ip_long > expect_start_ip_long:
                        sql_statement = 'INSERT INTO rmc_area_ip_fixed (id, area_name, start_ip, start_ip_long, end_ip, end_ip_long, type) VALUES ("{0}", "{1}", INET_NTOA({2}), {2}, INET_NTOA({3}), {3}, 0);'.format(old_ip_range.area_id, old_ip_range.area_name, expect_start_ip_long, new_start_ip_long - 1)
                        out.write(sql_statement)
                        out.write(os.linesep)
                        sql_statement = 'INSERT INTO rmc_area_ip_fixed (id, area_name, start_ip, start_ip_long, end_ip, end_ip_long, type) VALUES ("{0}", "{1}", INET_NTOA({2}), {2}, INET_NTOA({3}), {3}, 0);'.format(new_ip_range.area_id, new_ip_range.area_name, new_ip_range.start_ip_long, new_ip_range.end_ip_long)
                        out.write(sql_statement)
                        out.write(os.linesep)
                        expect_start_ip_long = new_end_ip_long + 1

                if expect_start_ip_long > old_end_ip_long:
                    break
        out.flush()
        out.close()


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
    orig_ip_range = load_old_ip_range()
    sorted_orig_ip_list = sorted(orig_ip_range)
    ip_list = analysis_ip_range()
    merge_with_old(ip_list, sorted_orig_ip_list)
    sys.exit(0)
