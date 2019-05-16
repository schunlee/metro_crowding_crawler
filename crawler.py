#! /usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import hashlib
import os

import requests
import datetime, time

import sys

reload(sys)
sys.setdefaultencoding("utf-8")


def get_time_stamp13(datetime_obj):
    datetime_str = datetime.datetime.strftime(datetime_obj, '%Y-%m-%d %H:%M:00')
    datetime_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:00')
    print(datetime_obj)

    date_stamp = str(int(time.mktime(datetime_obj.timetuple())))

    data_microsecond = str("%06d" % datetime_obj.microsecond)[0:3]
    date_stamp = date_stamp + data_microsecond
    return int(date_stamp)


def get_sign(**kwargs):
    '''
    计算加密sign参数
    :param kwargs:
    :return:
    '''
    d = {
        "Accept-APIVersion": "1.0",
        "appVersionNo": "78",
        "mobileBrand": "HUAWEI",
        "mobileStandard": "WIFI",
        "platformType": "android",
        "platformVersion": "6.0",
        "sign": "p@ssw0rd",
    }

    for kw_key in kwargs:
        d[kw_key] = kwargs[kw_key]

    data = ""
    for key in sorted(d.keys()):
        data += "&" + key + "=" + d[key]

    sign_raw = data[1:]
    h = hashlib.md5()  # md5加密
    h.update(str(sign_raw).encode("utf-8"))
    sign_md5 = h.hexdigest()
    return sign_md5


def get_crowding_info(call_time):
    url = "http://webapp.cocc.cdmetro.cn:10080/api/realDmyjdSearch"
    headers = {"platformVersion": "6.0",
               "platformType": "android",
               "Accept-APIVersion": "1.0",
               "mobileBrand": "HUAWEI",
               "mobileStandard": "WIFI",
               "sign": get_sign(userId="", tokenId="", callTime=call_time),  # 关键动态加密参数
               "appVersionNo": "78",
               "callTime": call_time,
               "Content-Type": "application/x-www-form-urlencoded",
               "Host": "webapp.cocc.cdmetro.cn:10080",
               "Connection": "Keep-Alive",
               "Accept-Encoding": "gzip",
               "User-Agent": "okhttp/3.4.1"}
    return requests.post(url, headers=headers)


if __name__ == '__main__':
    pass
    '''
    单元数据如下(感觉只能获得实时数据，无法获得历史数据，callTime只对sign加密有用)：
    {u'direction': 1, u'lineName': u'1号线', u'beginCode': u'0138', u'sectionId': u'01380137',
    u'color': u'#429C38', u'remark': u'2019-05-16 15:41:18',
    u'sectionName': u'广都->四河',
    u'dmyjd': 2.37, u'updateTime': u'2019-05-16 15:39:54', u'timeDate': u'20190516',
    u'endTimeHM': u'15:35', u'dmyjdDescr': u'舒适', u'section_state': 1, u'endTime': u'2019-05-16 15:35:00',
    u'startTime': u'2019-05-16 15:20:00', u'startTimeHM': u'15:20', u'lineId': u'01', u'endCode': u'0137'}
    '''
    now_time = datetime.datetime.now()  # 获取当前时间
    call_time_str = str(get_time_stamp13(now_time))  # 转为13位时间戳
    data = get_crowding_info(call_time_str).json()  # 获取地铁拥堵数据
    with open(os.path.join(os.path.expanduser("~"), "cd_metro.csv"), "w") as f:
        csv_writer = csv.writer(f, dialect='excel', delimiter=',')
        csv_writer.writerow(data["returnData"][0].keys())
        for row in data["returnData"]:
            csv_writer.writerow(row.values())
