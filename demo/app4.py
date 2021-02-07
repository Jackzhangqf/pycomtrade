# -*- coding:utf-8 -*-
'''
Author: your name
Date: 2021-02-02 15:44:25
LastEditTime: 2021-02-07 10:56:36
LastEditors: Please set LastEditors
Description: 使用plotly生成一个离线的波形显示界面
FilePath: \pycomtrade\demo\app4.py
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
    chs.get_chs_data([1,2,3,4,108,113,116,103,104,105,106,107])#提取四个通道
    data_file.fd.close()#关闭数据文件句柄
    
    #生成csv数据文件
    df=chs.create_csv()

    #使用plotly绘制图形
    #print(df[df.columns[1]])#获得列索引的名称和对应的列数据
    #data = go.Scatter(x=chs.ch_objects[0].ch_points[0][:-1],y=chs.ch_objects[0].ch_points[1][:-1],mode="lines")
    data1 = go.Scatter(x=df.index,y=df[df.columns[1]],name=df.columns[1],marker={'color':'rgb(255, 255, 0)'})
    data2 = go.Scatter(x=df.index,y=df[df.columns[2]],mode="lines",name=df.columns[2],marker={'color':'rgb(0, 255, 0)'})
    data3 = go.Scatter(x=df.index,y=df[df.columns[3]],mode="lines",name=df.columns[3],marker={'color':'rgb(255, 0, 0)'})
    data5 = go.Scatter(x=df.index,y=df[df.columns[5]],mode="lines",name=df.columns[5],marker={'color':'rgb(255, 0, 0)'})
    data6 = go.Scatter(x=df.index,y=df[df.columns[6]],mode="lines",name=df.columns[6],marker={'color':'rgb(255, 0, 0)'})
    data7 = go.Scatter(x=df.index,y=df[df.columns[7]],mode="lines",name=df.columns[7],marker={'color':'rgb(255, 255, 0)'})
    data8 = go.Scatter(x=df.index,y=df[df.columns[8]],mode="lines",name=df.columns[8],marker={'color':'rgb(255, 0, 0)'})
    data9 = go.Scatter(x=df.index,y=df[df.columns[9]],mode="lines",name=df.columns[9],marker={'color':'rgb(255, 0, 0)'})
    data10 = go.Scatter(x=df.index,y=df[df.columns[10]],mode="lines",name=df.columns[10],marker={'color':'rgb(255, 0, 0)'})
    data11 = go.Scatter(x=df.index,y=df[df.columns[11]],mode="lines",name=df.columns[11],marker={'color':'rgb(255, 0, 0)'})
    data12 = go.Scatter(x=df.index,y=df[df.columns[12]],mode="lines",name=df.columns[12],marker={'color':'rgb(255, 0, 0)'})
    fig = make_subplots(2,1)#生成一个figure对象
    fig.add_trace(data1,row=1,col=1)#把Ua电压放到第一个子图中
    fig.add_trace(data2,row=1,col=1)#把Ub电压也放到第一个子图中
    fig.add_trace(data3,row=1,col=1)#把Uc电压放到第二个子图中
    fig.add_trace(data5,row=2,col=1)#把Uc电压放到第二个子图中
    fig.add_trace(data6,row=2,col=1)#把Uc电压放到第二个子图中
    fig.add_trace(data7,row=2,col=1)#把Uc电压放到第二个子图中
    fig.add_trace(data8,row=2,col=1)#把Uc电压放到第二个子图中
    fig.add_trace(data9,row=2,col=1)#把Uc电压放到第二个子图中
    fig.add_trace(data10,row=2,col=1)#把Uc电压放到第二个子图中
    fig.add_trace(data11,row=2,col=1)#把Uc电压放到第二个子图中
    fig.add_trace(data12,row=2,col=1)#把Uc电压放到第二个子图中
    fig.update_layout(title_text=u"电压波形")
    #fig.show()
    pltoff.plot(fig, filename='绘图测试')