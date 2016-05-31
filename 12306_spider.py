# -*- coding: utf-8 -*-

"""
需要的第三方库：requests, pandas, openpyxl
"""

import os
import sys
import requests
import json
import re
import pandas

reload(sys)
sys.setdefaultencoding("utf-8")


class Spider_12306():
    def __init__(self):
        self.station_version = '1.8953'
        self.station_code_dict = {}
        self.name = ['车次', '始发站', '终点站', '出发站', '到达站', '出发时间', '跨越天数', '到达时间', '历时（小时:分钟）', '能否网上订票', '乘车日期',
                     '软卧', '软座', '硬卧', '硬座', '无座', '二等座', '一等座', '商务座']
        self.name_code = ['station_train_code', 'start_station_name', 'end_station_name', 'from_station_name', 'to_station_name', 'start_time', 'day_difference', 'arrive_time', 'lishi', 'canWebBuy', 'start_train_date',
                          'rw_num', 'rz_num', 'yw_num', 'yz_num', 'wz_num', 'ze_num', 'zy_num', 'swz_num']

    def get_stations_to_txt(self):
        url_station_codes = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=%s' % self.station_version
        station_codes = requests.get(url_station_codes, verify=False)
        txt = open('stations.txt', 'w')
        match = re.compile(".*?\'(.*?)\'.*?")
        find = re.findall(match, station_codes.text)
        stations = find[0].replace(' ', '')
        stations = stations.split('@')
        for i in stations[1:]:
            l = i.split('|')
            station, code = l[1], l[2]
            txt.write('%s,%s\n' % (station, code))
        txt.close()

    def get_code(self, station_name):
        txt = open('stations.txt', 'r')
        for i in txt.readlines():
            l = i.split(',')
            s_name = u'%s' % station_name
            if l[0] == s_name:
                return l[1].replace('\n', '')
        txt.close()

    def get_info(self, from_station_name, to_station_name, date):
        from_station_code = self.get_code(from_station_name)
        to_station_code = self.get_code(to_station_name)
        date = date
        url = 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate=%s&from_station=%s&to_station=%s' % (date, from_station_code, to_station_code)
        # print url
        json_data = requests.get(url, verify=False)
        # print json_data.text
        if json_data == '-1':
            print '无结果'
            return
        result = json.loads(json_data.text)
        l = result['data']['datas']
        # for i in l:
        #     print i
        info_list = []
        for i in l:
            info_list_temp = [i[j] for j in self.name_code]
            info_list.append(info_list_temp)
        frame = pandas.DataFrame(info_list, columns=self.name)
        # print frame
        frame.to_excel('out.xlsx', sheet_name='Sheet1')
        os.startfile('out.xlsx')

fr = raw_input('请输入出发站：')
to = raw_input('请输入到达站：')
da = raw_input('请输入乘车日期（如2016-01-01）：')

spider = Spider_12306()
if not os.path.exists('stations.txt'):
    spider.get_stations_to_txt()
spider.get_info(fr, to, da)
