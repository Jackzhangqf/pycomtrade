<!--
 * @Author: Jackzhangqf
 * @Date: 2021-01-17 17:31:06
 * @LastEditTime: 2021-05-31 09:22:42
 * @LastEditors: Please set LastEditors
 * @Description: This is a readme file
 * @FilePath: \pycomtrade\README.md
-->
# pycomtrade
For parse COMTRADE format of file  and contribute to data exploration
```
# Author:Jackzhang
# Email:cag125@qq.com
```
## 项目说明
> 本工程的主要功能是解析电力系统常用的COMTRADE格式的暂态故障录波文件。
>
## 开发维护说明
- 本项目为本人独立开发及维护；

## 修改历史记录
### 截至2021-01-17日支持的功能
- 解析1999版本的二进制格式的COMTRADE暂态录波文件，提取出基本的录波通道信息；
- 按照需求提取出所需通道的故障录波文件存入csv格式的文件中，便与大家用其它数据分析工具进行分析；
- 支持存储为pandas数据分析工具支持的DataFrame格式，助力大数据分析。

### 后续拟添加的功能
#### 2021-01-17
- 开发GUI工具，以可执行文件的形式提供给大家使用，进一步添加一些实用的数据分析小工具。
- ....

#### 2021-04-03
- 修复了不能正确解析NR数据文件格式，具体可参考comtrade_data.py的修改记录
- Cfg_file对象添加了parse方法，完成了parse_file()--->get_data_len()--->get_datafile_len()三个函数的功能

### 如何获得
- 第一种方法：下载ZIP格式的包，解压后即可使用。
- 第二种方法：在CMD中直接运行`git clone https://github.com/Jackhjy/pycomtrade.git`,将代码下载到本地使用;

### 所需的运行环境
- 基础运行环境为Python3.8,已不支持Python2。
- 还需要安装一些数据分析包，这里只需要在命令行模式运行`pip install -r requirement.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`,这样就会自动将需要的软件包安装好。

### 如何使用
```python
    #第一步：读取需要解析的配置文件，一定要注意配置文件和数据文件一定要同名（例如：cfg_file.CFG cfg_file.DAT）
    cfg = Cfg_file('./data/cfg_file.CFG')
    #第二步：解析配置文件并获得配置文件的基本信息
    #下面这三个函数必须按照相应顺序来进行操作
    cfg.parse_file()
    cfg.get_data_len()
    cfg.get_datafile_len()
    #第三步：根据解析得到的配置文件获得相应的数据文件信息
    data_file = Data_file(cfg)
    if data_file.check_file():
        pass
    else:
        print(u"该数据文件无效！")
    #第四步：通过配置文件和数据文件获得相应的通道对象
    chs = Ch_objects(data_file.fd,cfg)
    chs.parse_data()
    #第五步：提取所需通道的数据，具体的通道号可以参考app1中的程序运行结果。
    chs.get_chs_data([1,2,3])
    #第六步：关闭文件句柄
    data_file.fd.close()#关闭数据文件句柄

    #第七步：获得需要的数据，生成Pandas的DataFrame和csv文件（test.csv）
    df=chs.create_csv()
    #提取通道1的电压数据和时间数据
    time_x = df.index
    value_y = df[df.columns[1]]
    #这里的columns[1]中的1是表示当前提取出来的通道中排行第一的通道，并不是数据文件中的通道序列号
    #例如：第五步中提取的是录波文件中的排行1，2，3的通道，则录波文件中通道1对应的是df.columns[1]，后续依次类推
    #假设第五步中提取的是录波文件中的排行3，2，1的通道，则录波文件中通道1对应的是df.columns[3]。
    #后续大家可以进一步完成数据探索。
```

2021-05-31添加
```python
    #第一步：读取需要解析的配置文件，一定要注意配置文件和数据文件一定要同名（例如：cfg_file.CFG cfg_file.DAT）
    cfg = Cfg_file('./data/cfg_file.CFG')
    #第二步：解析配置文件并获得配置文件的基本信息
    if cfg.parse():

        #第三步：根据解析得到的配置文件获得相应的数据文件信息
        data_file = Data_file(cfg)
        if not data_file.check_file():
            print(u"该数据文件无效！")
        #第四步：通过配置文件和数据文件获得相应的通道对象
        chs = Ch_objects(data_file.fd,cfg)
        chs.parse_data()
        #第五步：提取所需通道的数据，具体的通道号可以参考app1中的程序运行结果。
        chs.get_chs_data([1,2,3])
        #第六步：关闭文件句柄
        data_file.fd.close()#关闭数据文件句柄

        #第七步：获得需要的数据，生成Pandas的DataFrame和csv文件（test.csv）
        df=chs.create_csv()
        #提取通道1的电压数据和时间数据
        time_x = df.index
        value_y = df[df.columns[1]]
        #这里的columns[1]中的1是表示当前提取出来的通道中排行第一的通道，并不是数据文件中的通道序列号
        #例如：第五步中提取的是录波文件中的排行1，2，3的通道，则录波文件中通道1对应的是df.columns[1]，后续依次类推
        #假设第五步中提取的是录波文件中的排行3，2，1的通道，则录波文件中通道1对应的是df.columns[3]。
        #后续大家可以进一步完成数据探索。

```
**希望大家多多支持哦！**

