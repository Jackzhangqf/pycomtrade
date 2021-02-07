#-*- coding:utf-8 -*-
#Author:Jackzhangqf
#Date:2017-09-18 Create this file
#功能描述：根据解析得到的.CFG文件，解析数据文件
#BugFixed:
#(1)2021.02.02 [BUG001]不能减1，2021.02.02日修复，不然在提取数字通道39的时候会提取到31的数值，刚好错开了一个字节
#(2)2021.02.03 [BUG002]
#-----------------------------
#问题1：数据的二进制格式：（4个字节描述采样点序号，低字节在前）+（4个字节描述时间标记）+
#     （模拟通道*2）+（数字通道/8，这里有余数的话必须加1）=每个数据点的字节数
#-----------------------------
#
from comtrade_cfg import Cfg_file,Achannel_info,Dchannel_info
import os
import struct
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from scipy.optimize import leastsq 

#对象说明：
#功能一：具备选择性输出数据通道的能力，比如输出第1、2、3模拟通道和第1、2、3数字通道，便于数据分析
#功能二：具备输出不同数据格式的能力（格式可以自定义），比如：CSV，TXT

class Data_file(object):
    def __init__(self,cfg_file):
        self.ch_objects = None #在get_data函数里面创建该对象
        self.fd = None  #存储打开的文件句柄
        self.cfg = cfg_file
    def check_file(self):
        '''
        校验数据文件是否有效依据：
        （1）判别它的总长度
        （2）判断文件是否存在
        '''
        if os.path.isfile(self.cfg.datafile_name+'.DAT'):
            self.fd = open(self.cfg.datafile_name+'.DAT','rb')
            file_len = os.path.getsize(self.cfg.datafile_name+'.DAT')
            if file_len == self.cfg.datafile_len:
                return True
            else :
                print (u'文件长度不匹配：原始文件长度为%s而计算得到的文件长度为%s'%(file_len,cfg.datafile_len))
                return False
        else:
            #print (u"文件路径不存在：%s"%self.path)
            return False

        

#对象说明：
#功能一：存储一个通道的数据及通道的相关信息的对象
class Ch_object(object):
    def __init__(self,ch_id):
        self.ch_id = ch_id #通道编号，通道号从1开始,得到需要的数据的通道号，接着提取数据
        self.ch_points=[[],[]] #采集到的数据点,该数据点是经过公式ax+b处理过的数据
        self.ch_info = None #是数字通道或者模拟通道，视情况而定：Achannel_info或者Dchannel_info

class Ch_objects(object):
    def __init__(self,fd,cfg):
        self.id_list = [] #需要提取的ID号列表，列表长度为0的话默认导出全部
        self.ch_objects=[] #需要提取的通道对象列表(这个是经过数据处理之后的数据啦)，可以直接使用的说
        self.all_ch = [] #提取所有通道数据存放的列表，未被处理过的数据，原始数据，一个列表对应原始数据里面的一条数据
        self.fd = fd  #数据文件的文件句柄
        self.one_len = cfg.data_len #一个数据包的长度
        self.cfg=cfg
        
    def save_csv(self,path_name):
        '''保存为CSV文件格式'''
        pass
    
    def parse_data(self):
        '''全局函数，解析出全部的数据，再按需提取'''
        fmt1='<2i'
        #[BUG002]将无符号整型改为有符号整型，因为每个厂家选取的零点的位置不同，
        # 有的选取最开始的时间为零点（预录开始时间），有的则是选取装置启动那一瞬间的时间为零点（前面预录的为负值）
        #修复时间：2021.02.03
        fmt2= str(self.cfg.a_c)+'h'
        #fmt3=str(cfg.bin_len)+'x'#二进制数据先不解析，作为填充字节不解析
        fmt3 = str(self.cfg.bin_len)+'c'
        fmt=fmt1+fmt2+fmt3
        #print (fmt)#输出格式字符串
        self.fd.seek(0,0)
        tuple_data=None
        for i in range(0,self.cfg.sample_rate_points[-1][-1]):#得到总的采样点数，用来做循环判据
            bin_data=self.fd.read(self.one_len)
            tuple_data = struct.unpack(fmt,bin_data)
            self.all_ch.append(list(tuple_data))
        #print (tuple_data)
        #print list(tuple_data)
        #print len(self.all_ch)
        
    def get_chs_data(self,id_list):
        '''
        Info:根据输入的通道号，生成相应的通道数据
        '''
        ch_infolist = self.cfg.Achannel_info+self.cfg.Dchannel_info
        self.ch_objects=[]
        #生成需要提取的通道列表
        if len(id_list):
            list_id = id_list
        else:
            list_id = list(range(1,self.cfg.a_c+self.cfg.d_c+1))
        for i in list_id:
            ch_obj=Ch_object(i)
            ch_obj.ch_info=ch_infolist[i-1]
            for data in self.all_ch:
                if isinstance(ch_obj.ch_info,Achannel_info):
                    ch_obj.ch_points[0].append(data[1]*self.cfg.timemult)#这里添加的是时间坐标数据
                    value = self.cfg.Achannel_info[i-1].ma*data[i+1]+self.cfg.Achannel_info[i-1].mb
                    ch_obj.ch_points[1].append(value)#这里添加的是数值坐标数据                  
                elif isinstance(ch_obj.ch_info,Dchannel_info):
                    '''
                    #2020.07.09
                    >>> s=b'\x00'
                    >>> s.hex()
                    '00'
                    >>> s1 = s.hex()
                    >>> type(s1)
                    <class 'str'>
                    >>> '0x'+ s1 #这个前缀是必须要加的，一定要注意
                    >>> s2=eval(s1)
                    >>> type(s2)
                    <class 'int'>
                    >>> s3 = '{:08b}'.format(s2)
                    >>> type (s3)
                    <class 'str'>
                    >>> s4 = list(s3)
                    >>> print s4
                    >>> print (s4)
                    ['0', '0', '0', '0', '0', '0', '0', '0']

                    '''
                    #数字通道的数据提取
                    data_d = data[(-self.cfg.bin_len):]#提取所有数字通道的字符列表
                    #获得数字通道号
                    #ch_num = i-self.cfg.d_c#[BUG003]应该是减去模拟通道数，而不是减去自己的数量（数字通道数）
                    ch_num = i-self.cfg.a_c
                    char_index = int(ch_num/8)
                    add_one = ch_num%8
                    bit_position = 0
                    if add_one:
                        char_index+1
                        bit_position = add_one
                    else:
                        bit_position = 8
                    bit_position = add_one
                    #[BUG001]不能减1，2021.02.02日修复，不然在提取数字通道39的时候会提取到31的数值，刚好错开了一个字节
                    #bin_bits = data_d[char_index-1]
                    bin_bits = data_d[char_index]
                    #将字节码变为按位展示的字符串列表
                    a1 = bin_bits.hex()
                    a2 = '0x'+a1
                    a3 = eval(a2)
                    a4 = '{:08b}'.format(a3)
                    a5 = list(a4)
                    #反转字符列表
                    #bits_strlist = a5.reverse()#默认是最高位索引为0,反转后最高位索引为0,这个会返回None
                    bits_strlist = a5[::-1] #默认是最高位索引为0,反转后最高位索引为0,这个能正常返回反转后的数据
                    bits_intlist = []
                    for bit in bits_strlist:
                        bits_intlist.append(int(bit))
                    ch_obj.ch_points[1].append(bits_intlist[bit_position-1])
                    ch_obj.ch_points[0].append(data[1])      
                else:
                    raise TypeError("You need a class[Achannel_info,Dchannel_info]")
                self.ch_objects.append(ch_obj)
    def create_csv(self,path=None):
        '''
        Info:Create a *.csv
        Date:2020.07.09
        Author:Jackzhangqf
        Add:
        [2020-07-10]:完成该功能，并进行了测试
        '''
        import datetime
        import pandas as pd
        #选择正确的起始点[BUG002]
        if self.ch_objects[0].ch_points[0][0] >= 0:#如果是以预录点为零点
            start_datetime = datetime.datetime.strptime(' '.join(self.cfg.start_t),"%d/%m/%Y %H:%M:%S.%f")#采样起始位置
            print("该文件选取预录点为零点")
        else:#如果以启动点为零点
            start_datetime = datetime.datetime.strptime(' '.join(self.cfg.end_t),"%d/%m/%Y %H:%M:%S.%f")#采样起始位置
            print("该文件选取启动点为零点")
        end_datetime= datetime.datetime.strptime(' '.join(self.cfg.end_t),"%d/%m/%Y %H:%M:%S.%f")#启动位置
        start_microtime = start_datetime.microsecond
        now_microtime = start_microtime
        pd_datetimelist = []
        #添加采样频率信息
        pd_dict = {}
        pd_dict[u'Freq'] = []
        just_once = 1
        for ch in self.ch_objects:
            pd_dict[ch.ch_info.cch_id] = ch.ch_points[1]
            #将时间相对值变为绝对时间值作为时间索引
            if just_once:
                just_once = 0
                count_points =0
                cc = 0 
                for i in ch.ch_points[0]:
                    now_microtime = i
                    now_datetime = start_datetime+datetime.timedelta(microseconds=now_microtime)
                    #添加进入pd_datetimelist列表中
                    pd_datetimelist.append(now_datetime)
                    #添加采样率信息进入数据文件中2020-07-11
                    j_front = 0
                    freq_index = 0
                    #获得索引值
                    for j in self.cfg.sample_rate_points[1]:
                        if count_points<j and count_points>=j_front:
                            freq_index=self.cfg.sample_rate_points[1].index(j,0,len(self.cfg.sample_rate_points[1]))
                            break#这个很关键，不让全部数据都显示为1000的采样率        
                        #表示已到采样频率的变化边界    
                        else :
                            j_front = j
                    count_points = count_points+1
                    #提取对应的索引频率
                    pd_dict[u'Freq'].append(self.cfg.sample_rate_points[0][freq_index])
                    
        #print ("频率数据长度：%s"%len(pd_dict[u'Freq']))
        pd_indexs = pd.to_datetime(pd_datetimelist)
        df = pd.DataFrame(pd_dict,index=pd_indexs)
        
        #df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list('ABCD'))
        #将DataFrame存储为csv,index表示是否显示行名，default=True
        df.to_csv("test.csv",sep=',')
        return df
        #dataframe.to_csv("test.csv",index=False,sep=',')

            
def find_max_index(data_list,time_list):
    time_index=0
    time_add=0
    x_data=data_list[0]
    for x1 in data_list:
        if x1>x_data:
            x_data=x1
            time_index=time_add
            
        time_add = time_add+1     
    return [x_data,time_list[time_index]]
        
if __name__ == '__main__':
    cfg = Cfg_file('./data/cfg_file.CFG')
    #下面这三个函数必须按照相应顺序来进行操作
    cfg.parse_file()
    cfg.get_data_len()
    cfg.get_datafile_len()
    
    data_file = Data_file(cfg)
    if data_file.check_file():
        pass
    else:
        print (u"该数据文件无效！")
    
    chs = Ch_objects(data_file.fd,cfg)
    chs.parse_data()
    chs.get_chs_data([1,2,3])
    data_file.fd.close()#关闭数据文件句柄
    
    #生成csv数据文件
    df=chs.create_csv()
    print(df[6299:6304])
    print ('-*'*10)
    print(df[6385:6390])
    print ('-*'*10)
    print(df[8875:8880])
    print ('-*'*10)
    print(df[11874:-1]) 
    #import pandas_profiling as pp
    #profile = df.profile_report(
      #vars={
          #'cat':{
            #'length':True,
            #'unicode':True,
          #}
      #}
    #)
    #profile.set_variable("html.minify_html", False)
    #profile = pp.ProfileReport(df)
    #profile.to_file("output123.html")
    #测量电压的相角
    t_start = 0
    t_end = 100
    a_onecycle=chs.ch_objects[3].ch_points[1][t_start:t_end]
    a_time=chs.ch_objects[3].ch_points[0][t_start:t_end]
    a_onecycle2=chs.ch_objects[0].ch_points[1][6301:6401]
    a_time2=chs.ch_objects[0].ch_points[0][6251:6351]
    b_onecycle=chs.ch_objects[1].ch_points[1][t_start:t_end]
    b_time=chs.ch_objects[1].ch_points[0][t_start:t_end]
    c_onecycle=chs.ch_objects[2].ch_points[1][t_start:t_end]
    c_time=chs.ch_objects[2].ch_points[0][t_start:t_end]
    a_current=chs.ch_objects[3].ch_points[1][t_start:t_end]
    
    #print (a_time)
    #print (len(chs.ch_objects[0].ch_points[1]))
    #import pandas as pd 
    #data = pd.to_datetime(['2020-01-02 13:01:02.000111','2020-01-02 13:01:02.000112'])
    #print (data)
    
    #(1)这种方法精度不够,直接找波峰-------------------------------------
    a_max=find_max_index(a_onecycle,a_time)
    b_max=find_max_index(b_onecycle,b_time)
    c_max=find_max_index(c_onecycle,c_time)
    a_cmax=find_max_index(a_current,c_time)
    sample_f=5000
    f=50
    print ((a_max[1]-b_max[1])*360*f/float(1000000))
    print ((b_max[1]-c_max[1])*360*f/float(1000000))
    print ((c_max[1]-a_max[1])*360*f/float(1000000))
    print ((a_max[1]-a_cmax[1])*360*f/float(1000000))
    
    #（2）采用三次样条插值来拟合曲线，精度一般---------------------------
    x1=a_time
    y1=a_onecycle
    x2=b_time
    y2=b_onecycle
    new_points=1000   #插值后得到的点数，原始是100个点
    x1_new = np.linspace(x1[0],x1[-1],new_points)
    x2_new = np.linspace(x2[0],x2[-1],new_points)
    x0_new =  np.linspace(0,x2[-1]-x2[0],new_points)
    
    f=interpolate.interp1d(x1,y1,kind='cubic')
    y1_new=f(x1_new)
    
    f=interpolate.interp1d(x2,y2,kind='cubic')
    y2_new=f(x2_new)
    
    
    a_max=find_max_index(y1_new,x1_new)
    b_max=find_max_index(y2_new,x2_new)

    print (u"经过三次样条插值后电压AB角差为：")
    print ((a_max[1]-b_max[1])*360*50/float(1000000))
 
    
    #（3）采用最小二乘拟合正弦函数(失败告终)----------------------------
    def func(x,p):
        """
        数据拟合所用的函数：A*sin(2*pi*k*x+theta)
        """
        A,k,theta = p
        return A*np.sin(2*np.pi*k*x+theta)
    def residuals(p,y,x):
        """
        试验数据x,y和拟合函数之间的差，p为拟合需要找到的系数
        """
        #print "test------"
        return y-func(x,p)
    p0=[57,50,0]
    a_times=np.array(a_time)/float(1000000)
    #print a_times
    plsq1 = leastsq(residuals,p0,args=(np.array(a_onecycle),np.array(a_times)))
    plsq2 = leastsq(residuals,p0,args=(np.array(b_onecycle),np.array(a_times)))
    
    print (plsq1,plsq2)
    print (u"最小二乘正弦拟合得到的角差为：")
    print ((plsq1[0][2]-plsq2[0][2])/(2*np.pi)*360)
    x1_news=np.array(x1_new)/1000000
    
    y1_plsq =func(np.array(x1_news),plsq1[0])
    y2_plsq =func(np.array(x1_news),plsq2[0])
    
    #（4）最小二乘法多项式拟合，精度还可以（部分段还是精度不够）----------------------------
    #这里要注意，每段的起始点都为0，不然拟合到后面的波形之后，误差较大
    a0_time=list(np.array(a_time)-a_time[0])#不管取哪段，起始点都设置为0
    b0_time=list(np.array(b_time)-b_time[0])
    
    n=9#9次多项式
    #目标函数
    def real_func(x):
        return 0
    
    #多项式函数
    def fit_func(p,x):
        f  = np.poly1d(p)
        return f(x)
    
    #误差函数
    def residuals1(p,y,x):
        ret = fit_func(p,x)-y
        return ret
    
    p0= np.random.randn(n)
    
    plsq3 = leastsq(residuals1,p0,args=(a_onecycle,a0_time))
    plsq4 = leastsq(residuals1,p0,args=(b_onecycle,a0_time))
    #print u'拟合参数为：',plsq3
    y3_plsq = fit_func(plsq3[0],x0_new)
    y4_plsq = fit_func(plsq4[0],x0_new)
    
    a_max=find_max_index(y3_plsq,x0_new)
    b_max=find_max_index(y4_plsq,x0_new)
    
    print (u"经过最小二乘法多项式拟合后电压AB角差为：")
    print ((a_max[1]-b_max[1])*360*50/float(1000000))    
    
    #计算有效值------这种方法可行
    a1=np.array(a_onecycle)
    a2=a1**2
    a3=a2.mean()
    print (u"RMS有效值为：")
    print (np.sqrt(a3))
    
    #使用matplotlib绘制A,B,C相的电压图
    '''
    plt.figure(figsize=(80,40))
    plt.plot(chs.ch_objects[0].ch_points[0],chs.ch_objects[0].ch_points[1],color='yellow',linewidth=2)
    #plt.plot(x0_new,y3_plsq,'go')
    #plt.plot(a0_time,y1,'ro')
    #plt.plot(x1_news,y1_plsq,'yo')
    #plt.plot(chs.ch_objects[1].ch_points[0],chs.ch_objects[1].ch_points[1],color='green',linewidth=2)
    #plt.plot(chs.ch_objects[2].ch_points[0],chs.ch_objects[2].ch_points[1],color='red',linewidth=2)
    plt.xlabel("Time(us)")
    plt.ylabel(chs.ch_objects[0].ch_info.munit)
    plt.title("First Example")
    plt.legend()
    plt.show()
    '''
    import datetime
    datet = datetime.datetime.strptime(' '.join(cfg.start_t),"%d/%m/%Y %H:%M:%S.%f")
    #print (datet)
    dd = datet+datetime.timedelta(microseconds=1110000)
    #print (dd)
    
    #使用plotly绘制
    '''
    import plotly.graph_objects as go

    #data = go.Scatter(x=chs.ch_objects[0].ch_points[0][:-1],y=chs.ch_objects[0].ch_points[1][:-1],mode="lines")
    data1 = go.Scatter(x=a_time,y=a_onecycle,mode="lines")
    data2 =  go.Scatter(x=a_time,y=a_onecycle2,mode="markers")
    fig = go.Figure(data=[data1,data2])
    fig.update_layout(title_text=u"电压波形")
    fig.show()
    '''
    