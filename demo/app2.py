# -*- coding:utf-8 -*-
'''
Author: Jackzhang
Date: 2021-01-18 19:31:44
LastEditTime: 2021-02-07 14:07:56
LastEditors: Please set LastEditors
Description: 使用pandas-profiling做一个简单的数据探索
FilePath: \pycomtrade\demo\app2.py
'''
import sys,os
import datetime
#导入上次文件夹中的模块,也需要在pyct文件夹下新建一个空白的__init__.py
str_list = __file__.split('/')
path = '/'.join(str_list[:-2])
sys.path.append(path)
from comtrade_cfg import Cfg_file
from comtrade_data import Data_file,Ch_objects

import pandas_profiling as pp

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
    #生成报告的配置
    profile = df.profile_report(
        vars={
            'cat':{
            'length':True,
            #'unicode':True,
            }
        }
    )
    #生成最小化的html报告
    profile.set_variable("html.minify_html", False)
    profile = pp.ProfileReport(df)
    profile.to_file("output123.html")