#-*- coding:utf-8 -*-
#Author:Jackzhangqf
#Date:2017-08-31 Create this file
#[BUG001]解决不能识别int('100.000000')报错的问题2021.02.03
#----------------------------
#问题1：对于二进制数据文件的长度，计算公式为：模拟通道*2+4+4+数字通道/8入下一个整数
#算例：加入模拟通道有77，数字通道有77，则每条数据的字节数为77*2+4+4+77/8=172个字节
#----------------------------
#
#
#Functional description:Parse xxx.cfg file

import os
import os.path
import traceback

class Achannel_info(object):
    '''
    模拟通道对象
    数据格式如下：1,500kV梨阿线线路电压Ua,A,500kV梨阿线线路电压,V,0.031880338841159,-1.880939991628381,0,-8192,8191,500000,100,S
    '''
    def __init__(self):
        self.mno = None #模拟通道索引号 1-999999
        self.cch_id = None  #通道识别符 0-64个字符
        self.cph = None #通道相位特征 0-2个字符
        self.cccbm = None   #被监视的回路元件 0-64个字符
        self.munit = None   #通道单位（例如kV,V,kA,A）1-32个字符
        self.ma = None  #通道乘数 1-32个字符
        self.mb = None  #通道偏移加数 1-32个字符
        self.cskew = None   #从抽样开始后的通道时滞（us）1-32个字符
        self.mmin = None    #该通道数据值的最小数据值 1-6个字符
        self.mmax = None    #该通道数据值最大数据值范围 1-6个字符
        self.mprimary = None    #一次值 1-32个字符
        self.msecondary = None  #二次值 1-32个字符
        self.mps = None #决定是转换为一次值还是二次值 P,p,S,s只有一个字符
class Dchannel_info(object):
    '''
    数字通道对象
    数据格式如下：160,500kV梨阿线载波机总告警2,,500kV梨阿线线路电流,0
    '''
    def __init__(self):
        self.mno = None # 状态通道索引号 1-999999
        self.cch_id = None #通道名称 0-32个字符
        self.cph = None #通道相位特征 0-2个字符
        self.cccbm = None #被监视回路元件 0-64个字符
        self.my = None #当一次器件处于稳态“服务”条件时作为输入状态的状态通道的状态 一个字符，0或1


class Cfg_file(object):
    def __init__(self,path):
        self.station_name="Default" #缺省厂站名称
        self.version=1991   #版本号1991或1999
        self.dev_name="Default_name"    #装置名称
        self.channel=0  #总通道数量
        self.a_c=100  #模拟通道数量
        self.d_c=100  #数字通道数量
        self.Achannel_info=[]   #模拟通道对象列表
        self.Dchannel_info=[]   #数字通道对象列表
        self.reference_frequency=50 #基准频率默认为50Hz
        self.sample_section=0   #采样段有几段
        self.sample_rate_points=[[],[]] #[[],[]]第一个列表表示采样速率，第二个列表表示对应的采样速率下的采样点数
        self.data_format=None   #二进制或者ASCII字符，True表示二进制，False表示ASCII
        self.start_t=[]    #预采样开始时间
        self.end_t=[]  #零点(启动)时间
        self.timemult=None  #时间标记
        self.path=path
        self.datafile_len = 0 #整个数据文件的长度
        self.data_len=0 #单条数据的长度
        self.datafile_name = None #不要前缀之后的文件名，后面可以用来组装.DAT文件
        self.bin_len = 0 #数字通道的总字节数
    
    def get_datafile_len(self):
        '''得到整个数据文件的长度'''
        file_len = self.data_len*self.sample_rate_points[-1][-1]
        self.datafile_len = file_len
        
    def get_data_len(self):
        '''得到一条数据的长度'''
        data_len = self.a_c*2+8
        d_temp = self.d_c%16
        temp1=int(self.d_c/16)#python3中这个值有小数点的话会保留，python2有小数点的话直接舍去就没有小数点了
        #Python2
        #temp1= self.d_c/16
        if d_temp:
            
            data_len = data_len+temp1*2+2
            self.bin_len = temp1*2+2
        else :
            data_len = data_len+temp1*2
            self.bin_len = temp1*2
        self.data_len = data_len
        
    def parse_file(self):
        line_string=None
        dir_of_file = os.path.dirname(self.path)
        self.datafile_name = os.path.splitext(self.path)[0]
        cfg_line = None
        line_count = 0#记录当前行号
        try:
            if os.path.exists(dir_of_file):
                #if os.path.splitext(self.path)[1] == ".CFG":2020-07-11修复的Bug
                if os.path.splitext(self.path)[-1] == ".CFG" or os.path.splitext(self.path)[-1] == ".cfg":
                    with open(self.path) as fd:
                        for line in fd:
                            line_count = line_count+1
                            cfg_line = line.split(",")
                            if line_count == 1:
                                self.station_name = cfg_line[0]
                                self.dev_name = cfg_line[1]
                                self.version = int(cfg_line[2])
                            elif line_count == 2:
                                self.channel = int(cfg_line[0])
                                self.a_c = int(cfg_line[1][0:-1])
                                self.d_c = int(cfg_line[2][0:-2])
                            elif line_count >= 3 and line_count <= self.a_c+2:   
                                if len(cfg_line) == 13:
                                    analog_ch_obj = Achannel_info()
                                    analog_ch_obj.mno = int(cfg_line[0])
                                    analog_ch_obj.cch_id = cfg_line[1]
                                    analog_ch_obj.cph = cfg_line[2]
                                    analog_ch_obj.cccbm = cfg_line[3]
                                    analog_ch_obj.munit = cfg_line[4]
                                    analog_ch_obj.ma = float(cfg_line[5])
                                    analog_ch_obj.mb = float(cfg_line[6])
                                    analog_ch_obj.cskew = float(cfg_line[7])
                                    analog_ch_obj.mmin = int(cfg_line[8])
                                    analog_ch_obj.mmax = int(cfg_line[9])
                                    analog_ch_obj.mprimary = float(cfg_line[10])
                                    analog_ch_obj.msecondary = float(cfg_line[11])
                                    #可能是浮点值，2020-07-11修复Bug
                                    #analog_ch_obj.mprimary = int(cfg_line[10])
                                    #analog_ch_obj.msecondary = int(cfg_line[11])
                                    analog_ch_obj.mps = cfg_line[12][0]
                                    self.Achannel_info.append(analog_ch_obj)
                                else:
                                    print (u"模拟通道采样部分行号定位错误%s"%cfg_line)
                            elif line_count > self.a_c + 2 and line_count <= self.a_c+2+self.d_c:
                                if len(cfg_line) == 5:
                                    digit_ch_obj = Dchannel_info()
                                    digit_ch_obj.mno = int(cfg_line[0])
                                    digit_ch_obj.cch_id = cfg_line[1]
                                    digit_ch_obj.cph = cfg_line[2]
                                    digit_ch_obj.cccbm = cfg_line[3]
                                    digit_ch_obj.my = int(cfg_line[4][0])
                                    self.Dchannel_info.append(digit_ch_obj)
                                else:
                                    print (u"数字通道采样部分行号定位错误%s"%cfg_line)
                            elif line_count == self.a_c+3+self.d_c:
                                if len(cfg_line) == 1:
                                    self.reference_frequency = float(cfg_line[0])
                                else:
                                    print (u"基准频率部分行号定位错误%s"%cfg_line)
                            elif line_count == self.a_c+4+self.d_c:
                                if len(cfg_line) == 1:
                                    self.sample_section = int(cfg_line[0])
                                else:
                                    print (u"采样区块数量部分行号定位错误%s"%cfg_line)   
                            elif line_count >= self.a_c+5+self.d_c and line_count <= self.a_c+5+self.d_c+self.sample_section-1:
                                if len(cfg_line) == 2:
                                    self.sample_rate_points[0].append(int(cfg_line[0]))
                                    self.sample_rate_points[1].append(int(cfg_line[1][0:-1]))
                                else:
                                    print (u"采样率信息定位错误%s"%cfg_line)
                            elif line_count == self.a_c+5+self.d_c+self.sample_section:
                                if len(cfg_line) == 2:
                                    self.start_t.append(cfg_line[0])
                                    self.start_t.append(cfg_line[1][0:-1])
                                else:
                                    print (u"开始时间信息定位错误%s"%cfg_line)
                            elif line_count == self.a_c+5+self.d_c+self.sample_section+1:
                                if len(cfg_line) == 2:
                                    self.end_t.append(cfg_line[0])
                                    self.end_t.append(cfg_line[1][0:-1])
                                else:
                                    print (u"结束时间信息定位错误%s"%cfg_line)
                            elif line_count == self.a_c+5+self.d_c+self.sample_section+2:
                                if len(cfg_line) == 1:
                                    self.data_format = cfg_line[0][0:-1]
                                else:
                                    print (u"数据格式信息定位错误%s"%cfg_line)
                            elif line_count == self.a_c+5+self.d_c+self.sample_section+3:
                                if len(cfg_line) == 1:
                                    temp_timemult = cfg_line[0].rstrip()#去除字符串末尾的换行符
                                    temp_timemult = temp_timemult.split('.')[0]#[BUG001]解决不能识别int('100.000000')报错的问题2021.02.03
                                    self.timemult = int(temp_timemult)
                                else:
                                    print (u"时间标记信息定位错误%s"%cfg_line)
                            else :
                                print (u"定义无效%s"%line_count)
                else:
                    print (u"这个不是一个配置文件！")
        except Exception as e:
            print (u"-------------------------------------------------------------错误信息")
            print ("str(Exception):\t", str(Exception))
            print ("str(e):\t\t",str(e))
            print ("repr(e):\t", repr(e))
            #print ("e.message:\t", e.values)
            print ("traceback.print_exc():", traceback.print_exc())
            print ("traceback.format_exc():\n%s" % traceback.format_exc())
            print (u"-------------------------------------------------------------错误信息结束")

                
    def cfg_info_echo(self):
        print (u"------------------.CFG解析信息--------------------")
        print (u"厂站名称：%s"%self.station_name)
        print (u"装置名称：%s"%self.dev_name)
        print (u"COMTRADE文件版本号：%s"%self.version)
        print (u"总的通道数：%s"%self.channel)
        print (u"模拟通道数：%s"%self.a_c)
        print (u"数字通道数：%s"%self.d_c)
        print (u"采样段数：%s"%self.sample_section)
        print (u"采样频率%s,各段的采样终止点%s"%(self.sample_rate_points[0],self.sample_rate_points[1]))
        print (u"采样点起始时间：%s %s"%(self.start_t[0],self.start_t[1]))
        print (u"采样触发时间：%s %s"%(self.end_t[0],self.end_t[1]))
        i=len(self.sample_rate_points[0])
        print (i)
        t=0.0
        while i:
            if i>1:
                t=t+(self.sample_rate_points[1][i-1]-self.sample_rate_points[1][i-2])*1/float(self.sample_rate_points[0][i-1])
                #t=t+1/float(self.sample_rate_points[0][i-1])
            elif i==1:
                t=t+(self.sample_rate_points[1][0])*1/float(self.sample_rate_points[0][0])
                #t=t+1/float(self.sample_rate_points[0][0])
            i=i-1
        print (u"采样总时间核对：%f"%t)
        print (u"数据格式：%s"%self.data_format)
        print (u"时间标记乘数：%s"%self.timemult)


if __name__ == "__main__":
    '''try:
    
        #cfg_file = open(u".\\data\\cfg_file.CFG")
        #line_string=cfg_file.readline()
        #line_string=cfg_file.readline()
        #line_string=cfg_file.readline()
        with open(".\\data\\cfg_file.CFG") as f:
            for line in f :
                x= line.split(",")
                print int(x[2][0:4])
                break
        
        print line
        print float('-1231.4')
    
    except Exception,e:
        print e.message
    '''
    file_len = os.path.getsize('./data/cfg_file.DAT')
    print (u"数据文件长度为：%s"%file_len)
    cfg = Cfg_file('./data/cfg_file.CFG')
        #下面这三个函数必须按照相应顺序来进行操作
    cfg.parse_file()
    cfg.get_data_len()
    cfg.get_datafile_len()
    print (u"单条数据长度为：%s"%cfg.data_len)
    print (u"整个数据文件为：%s"%cfg.datafile_len)
    print (len(cfg.Achannel_info))
    print (cfg.Achannel_info[0].mmin)
    print (cfg.Achannel_info[0].mprimary)
    print (cfg.Achannel_info[0].ma)
    print (cfg.timemult)
    print (cfg.Dchannel_info[0].cch_id)
    print (cfg.data_format)
    cfg.cfg_info_echo()
    
    
