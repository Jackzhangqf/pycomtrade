# -*- coding:utf-8 -*-
'''
Author: Jackzhang
Date: 2021-01-18 19:33:05
LastEditTime: 2021-02-07 11:30:58
LastEditors: Please set LastEditors
Description: 将解析出来的数据进行绘图展示，这里利用plotly库进行展示
FilePath: \pycomtrade\demo\app3.py
'''
import sys,os
import datetime

import plotly.graph_objects as go
import plotly.offline as pltoff#导入离线绘图模块
from plotly.subplots import make_subplots#导入绘制多个子图模块
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
    chs.get_chs_data([3,2,1,4,77])#提取四个通道
    data_file.fd.close()#关闭数据文件句柄
    
    #生成csv数据文件
    df=chs.create_csv()

    #使用plotly绘制图形
    #print(df[df.columns[1]])#获得列索引的名称和对应的列数据
    #data = go.Scatter(x=chs.ch_objects[0].ch_points[0][:-1],y=chs.ch_objects[0].ch_points[1][:-1],mode="lines")
    data1 = go.Scatter(x=df.index,y=df[df.columns[1]],mode="lines",name=df.columns[1],marker={'color':'rgb(255, 255, 0)'})
    data2 = go.Scatter(x=df.index,y=df[df.columns[2]],mode="lines",name=df.columns[2],marker={'color':'rgb(0, 255, 0)'})
    data3 = go.Scatter(x=df.index,y=df[df.columns[3]],mode="lines",name=df.columns[3],marker={'color':'rgb(255, 0, 0)'})
    fig = go.Figure()
    fig.add_trace(data1)
    fig.add_trace(data2)
    fig.add_trace(data3)
    fig.update_layout(title_text=u"电压波形")
    #fig.show()
    fig.add_trace
    pltoff.plot(fig, filename='123')