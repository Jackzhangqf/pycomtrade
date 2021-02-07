# -*- coding: utf-8 -*-
'''
Author: Jackzhang
Date: 2021-01-17 18:33:17
LastEditTime: 2021-02-07 14:29:26
LastEditors: Please set LastEditors
Description: 测试解析出来的基本信息是否正确
FilePath: \pycomtrade\demo\app1.py
'''

import sys,os
import datetime
#导入上次文件夹中的模块,也需要在pyct文件夹下新建一个空白的__init__.py
str_list = __file__.split('/')
path = '/'.join(str_list[:-2])
sys.path.append(path)
from comtrade_cfg import Cfg_file
from comtrade_data import Data_file,Ch_objects

if __name__ == "__main__":
    cfg = Cfg_file('./data/cfg_file.CFG')
    #下面这三个函数必须按照相应顺序来进行操作
    cfg.parse_file()
    cfg.get_data_len()
    cfg.get_datafile_len()
    
    data_file = Data_file(cfg)
    if data_file.check_file():
        pass
    else:
        print(u"该数据文件无效！")
    
    chs = Ch_objects(data_file.fd,cfg)
    chs.parse_data()
    chs.get_chs_data([1,2,3])
    data_file.fd.close()#关闭数据文件句柄
    
    #生成csv数据文件
    df=chs.create_csv()

    #基本信息显示
    basic_info = "厂站名称为：{};\nCOMTRADE版本：{};\n装置名称为：{};".format(cfg.station_name,cfg.version,cfg.dev_name)
    channal_info = "总采样通道数：{};\n模拟通道数：{};\n数字通道数：{};".format(cfg.channel,cfg.a_c,cfg.d_c)
    sample_info = "采样基准频率（Hz）：{};\n采样段数：{};\n各采样段采样速率（Hz）及各段采样结束点号：{}，{};".format(cfg.reference_frequency,cfg.sample_section,cfg.sample_rate_points[0],cfg.sample_rate_points[1])
    start_datetime = datetime.datetime.strptime(' '.join(cfg.start_t),"%d/%m/%Y %H:%M:%S.%f")#采样起始位置
    end_datetime= datetime.datetime.strptime(' '.join(cfg.end_t),"%d/%m/%Y %H:%M:%S.%f")#启动位置
    now_datetime = start_datetime+datetime.timedelta(microseconds=chs.ch_objects[0].ch_points[0][-1])#结束位置
    time_info = "采样预录开始时间：{};\n零点（启动）采样时间：{};\n采样结束时间：{};".format(start_datetime.strftime('%Y-%m-%d %H:%M:%S.%f'),end_datetime.strftime('%Y-%m-%d %H:%M:%S.%f'),now_datetime.strftime('%Y-%m-%d %H:%M:%S.%f'))
    file_info = "数据文件大小（Byte）：{};\n单条数据长度：{};".format(cfg.datafile_len,cfg.data_len)
    print(basic_info)
    print(channal_info)
    print(sample_info)
    print(time_info)
    print(file_info)
    #获得每个通道的序号
    #获得所有通道的基本名称，便于使用chs.get_chs_data([1,2,3])提取所需通道2021.02.03
    info_l = []
    for i in cfg.Achannel_info:
        info_l.append([i.mno,i.cch_id])
    for i in cfg.Dchannel_info:
        info_l.append([i.mno+cfg.a_c,i.cch_id])
    print("通道名称对应的通道序号为：")
    for i in info_l:
        print(i)
    #print(info_l)
    #获得某一个通道的变比值，这里提取了通道1的变比值
    print("通道1的电压变比是{}/{}".format(cfg.Achannel_info[0].mprimary,cfg.Achannel_info[0].msecondary))

